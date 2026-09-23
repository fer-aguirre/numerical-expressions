from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional, Tuple

from .describe import DEFAULT_OPERATIONS, OPERATIONS, describe_all
from .phrasing import HEDGE_MODES, STYLES, UNIT_POSITIONS, available_locales, load_locale
from .results import Options


def parse_value(text: str) -> Tuple[float, bool]:
    """Parse "12.5" or "12.5%"; the flag says whether it was written as a percentage."""
    is_percent = text.endswith("%")
    try:
        return float(text.rstrip("%")), is_percent
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from None


DESCRIPTION = """\
Suggest clear, accurate ways to write about the change between two numbers.

Give an initial and a final value; numexp prints one or more suggested phrases
per operation, plus notes about common mistakes (e.g. percent vs. percentage
points). Misleading comparisons, such as a percentage change from zero, are
refused with an error that suggests what to write instead.

operations (-o):
  difference             absolute change        20 is 10 more than 10
  percentage             final as % of initial  20 equals 200% of 10
  percentage_difference  percent change         20 is 100% higher than 10
  ratio                  multiples, fractions   20 is double 10
  ratio_difference *     "N times more", safely 30 is 2 times more than 10
                                                (i.e. 3 times as much)
  trend                  news-style sentence    The figure rose 10%, from 100 to 110
  share *                part of a total        One in five (3.2 million out of 16 million)
  rate *                 events per residents   16.5 murders per 100,000 residents
  risk *                 relative vs absolute   The risk went from two in 100 to three in 100
  inflation *            nominal vs real        The budget surged 80% in nominal terms, but
                                                fell 14.69% after adjusting for inflation
  relatable *            familiar benchmarks    3 million is about the population of the
                                                city of Buenos Aires

  * not run by default; ask for them with -o. The values mean something
    different for these:
      share      INITIAL is the total, FINAL is the part
      rate       INITIAL is the number of events, FINAL is the population
      risk       both values are risks, written as percentages (2% 3%)
      inflation  runs automatically with --cpi-then and --cpi-now
    With a single value, numexp runs relatable only.
"""

EPILOG = """\
examples:
  numexp 1200000 1550000 --unit '$' --hedge directional
  numexp 4.1% 3.6% --subject Unemployment -o trend
  numexp 16000000 3200000 -o share --unit people
  numexp 320 1937086 -o rate --unit murders
  numexp 5000000 9000000 --cpi-then 100 --cpi-now 211 --subject "The budget"
  numexp 42% 45% --sample 625 --subject Support -o trend
  numexp 9000000 --lang es

negative values:
  Negative numbers work as-is:  numexp -10 -5
  Negative percentages must come after --, with the options before it:
                                numexp -o trend -- -5% -2%

exit status:
  0  every operation produced suggestions
  1  at least one operation was refused (the reason is printed to stderr)
  2  invalid command line
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="numexp",
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("initial_value", type=parse_value, metavar="INITIAL",
                        help="the starting value (the total, for share); write 5%% for a percentage")
    parser.add_argument("final_value", type=parse_value, metavar="FINAL", nargs="?",
                        help="the new value (the part, for share); write 7%% for a percentage. "
                             "Leave it out to compare a single number with benchmarks")

    what = parser.add_argument_group("what to calculate")
    what.add_argument("-o", "--operations", nargs="+", choices=OPERATIONS, default=None,
                      metavar="OP",
                      help="one or more operations from the list above "
                           "(default: all except ratio_difference, share and relatable)")
    what.add_argument("-p", "--percent", action="store_true",
                      help="the values are percentages, so changes are also given in percentage "
                           "points; same as writing 5%% 7%%")

    wording = parser.add_argument_group("how to write it")
    wording.add_argument("-l", "--lang", default="en", choices=available_locales(), metavar="LANG",
                         help=f"language of the suggestions: {', '.join(available_locales())} "
                              "(default: %(default)s)")
    wording.add_argument("-u", "--unit",
                         help="unit for amounts: '$' gives $1.2 million, 'people' gives 3,400 people")
    wording.add_argument("--unit-position", choices=UNIT_POSITIONS, default="auto",
                         help="where the unit goes; auto puts currency symbols before the number "
                              "and words after it (default: %(default)s)")
    wording.add_argument("--hedge", choices=HEDGE_MODES, default="off",
                         help="off keeps exact figures (29.17%%); directional rounds to 'nearly "
                              "30%%' or 'more than 40%%'; roughly rounds to 'roughly 30%%' "
                              "(default: %(default)s)")
    wording.add_argument("--style", choices=STYLES, default="ap",
                         help="ap spells out whole numbers under 10, as the AP Stylebook does; "
                              "figures always uses digits, which AP prefers for measurements "
                              "(5 km) and ages (default: %(default)s)")
    wording.add_argument("-s", "--subject",
                         help="what is being measured, used in trend sentences "
                              "(default: 'The figure', or its translation)")

    context = parser.add_argument_group("rates, inflation and polls")
    context.add_argument("--per", type=float, default=100_000, metavar="N",
                         help="population base for -o rate: 1000 gives 'per 1,000 residents' "
                              "(default: 100,000)")
    context.add_argument("--cpi-then", type=float, metavar="INDEX",
                         help="the price index (e.g. the consumer price index) at the date of "
                              "INITIAL; with --cpi-now, adds the inflation-adjusted change")
    context.add_argument("--cpi-now", type=float, metavar="INDEX",
                         help="the same price index at the date of FINAL")
    context.add_argument("--sample", type=int, metavar="N",
                         help="for poll percentages: how many people were surveyed, to check "
                              "whether a change is within the margin of error")

    benchmarks = parser.add_argument_group("relatable comparisons")
    benchmarks.add_argument("--relatable", action="store_true",
                            help="also compare the values with the populations of Brazil, Mexico, "
                                 "Colombia, Argentina, São Paulo, Mexico City and Buenos Aires "
                                 "(same as adding -o relatable)")
    benchmarks.add_argument("--region",
                            help="only use benchmarks tagged with this region, e.g. latin-america; "
                                 "useful with your own --benchmarks file (implies --relatable)")
    benchmarks.add_argument("--benchmarks", metavar="FILE",
                            help="use your own benchmarks from a JSON file instead of the built-in "
                                 "populations (implies --relatable; see README)")

    output = parser.add_argument_group("output")
    output.add_argument("--json", action="store_true",
                        help="print structured results (value, phrases, warnings, error) as JSON")
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    single_value = args.final_value is None
    if single_value:
        # One number: nothing to compare it with except benchmarks.
        if args.operations and args.operations != ["relatable"]:
            parser.error("these operations compare two values; give both INITIAL and FINAL")
        args.final_value = args.initial_value
        args.operations = ["relatable"]
    (initial, initial_is_percent), (final, final_is_percent) = args.initial_value, args.final_value
    if initial_is_percent != final_is_percent:
        parser.error("write both values as percentages or neither")
    if (args.cpi_then is None) != (args.cpi_now is None):
        parser.error("give both --cpi-then and --cpi-now")
    if args.sample is not None and not (args.percent or initial_is_percent):
        parser.error("--sample only applies to poll percentages; write the values with %, e.g. 42% 45%")
    if args.sample is not None and args.sample <= 0:
        parser.error("--sample must be a positive number of people")

    options = Options(
        lang=args.lang,
        unit=args.unit,
        unit_position=args.unit_position,
        hedge=args.hedge,
        style=args.style,
        percent_values=args.percent or initial_is_percent,
        subject=args.subject,
        benchmarks=args.benchmarks,
        region=args.region,
        per=args.per,
        cpi_then=args.cpi_then,
        cpi_now=args.cpi_now,
        sample=args.sample,
    )
    operations = list(args.operations or DEFAULT_OPERATIONS)
    if (args.relatable or args.benchmarks or args.region) and "relatable" not in operations:
        operations.append("relatable")
    if args.cpi_then is not None and "inflation" not in operations:
        operations.append("inflation")

    results = describe_all(initial, final, operations, options)

    # Accented Spanish and Portuguese text must survive legacy Windows consoles.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    if args.json:
        payload = {"initial_value": initial, "final_value": final, "options": vars(options),
                   "results": [result.to_dict() for result in results]}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        labels = load_locale(args.lang).get("labels")
        for result in results:
            if result.error:
                print(f"{labels['error']}: {result.error}", file=sys.stderr, flush=True)
            for phrase in result.phrases:
                print(phrase, flush=True)
            for warning in result.warnings:
                print(f"  {labels['warning']}: {warning}", flush=True)
            if result.phrases or result.warnings:
                print()

    sys.exit(1 if any(result.error for result in results) else 0)


if __name__ == "__main__":
    main()
