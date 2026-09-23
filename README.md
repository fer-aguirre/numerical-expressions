# Numerical Expressions

**A writing assistant for journalists who work with numbers.** Give it two numbers and it suggests clear, accurate ways to put them in a story. It also warns you about the mistakes that most often slip into print.

```
$ numexp 48200 61500 --subject Homicides -o percentage_difference trend
61,500 is 27.59% higher than 48,200
61,500 is a 27.59% increase over 48,200
  Note: Rises and falls aren't symmetrical: going back from 61,500 to 48,200 would be a 21.63%
  fall, not 27.59%.
Homicides jumped 27.59%, from 48,200 to 61,500
Homicides jumped by 13,300, from 48,200 to 61,500
```

It writes in English, Spanish and Brazilian Portuguese.

Created by: Fernanda Aguirre Ruíz

---

## What it helps with

- **Describing a change** as an amount, a percentage, a multiple ("double", "a third") or a news-style sentence.
- **Choosing the right verb.** A 2% rise "edged up"; a 60% rise "surged". It never calls a small change a surge.
- **Percentage points vs. percent.** Unemployment going from 4.1% to 3.6% is a fall of 0.5 *percentage points*, not 0.5%.
- **Parts of a total.** 3.2 million out of 16 million becomes "one in five".
- **Rates.** 320 murders in a city of 1.9 million becomes "16.5 murders per 100,000 residents", so places of different sizes can be compared fairly.
- **Inflation.** A budget that "rose 80%" may have fallen 15% once prices are taken into account. It gives both.
- **Polls.** It warns you when a change is within the margin of error.
- **Risk.** "The risk rose 50%" can mean going from 2 in 100 to 3 in 100. It gives the relative and the absolute change.
- **Big numbers readers can picture.** 3 million becomes "about the population of the city of Buenos Aires".
- **Rounding honestly.** 27.59% becomes "nearly 28%", and 40.4% becomes "more than 40%".
- **Avoiding misleading comparisons.** It refuses to calculate a percentage change from zero, and it never writes "three times less".

It's an assistant, not an editor. Read every suggestion before you use it, and check the numbers against your source.

---

## Use it in your browser

The easiest way to use the tool is the website: **https://fer-aguirre.github.io/numerical-expressions/**. There's nothing to install.

1. Choose what you're writing about: a change, percentages and polls, a part of a total, a rate, money over time, risk, or a big number to make relatable.
2. Type your numbers. Commas and points are fine: `1,937,086`, `1.937.086` and `4,1` all work, and the page shows how it read each number.
3. Copy the suggestions you want into your story.

Everything runs in your browser, so the numbers you type are never sent anywhere. The first visit takes a few seconds to load.

The rest of this guide covers the command-line version, `numexp`. It has the same suggestions, and it's handy if you work in a terminal or want to use the tool in scripts.

---

## Install Numerical Expressions

Open a terminal (**Terminal** on a Mac, **PowerShell** on Windows), paste this line and press Enter:

```
pip install https://github.com/fer-aguirre/numerical-expressions/archive/refs/heads/main.zip
```

Then try it:

```
numexp 10 20
```

If you see a few sentences about 10 and 20, it works. To update to the latest version later, run the same `pip install` line again with `--upgrade` added after `install`.

**If it doesn't work:**

- **"pip: command not found".** You need Python 3.9 or newer; download it from [python.org](https://www.python.org/downloads/). On Windows, tick "Add Python to PATH" in the installer, or use `py -m pip install ...` instead of `pip install ...`.
- **"numexp: command not found".** The install worked, but your terminal can't find the command. Use `python -m numerical_expressions 10 20` instead (`py -m numerical_expressions 10 20` on Windows).

**Other ways to install:**

- **uv** installs `numexp` in its own isolated space, so it can't clash with other Python programs:

  ```
  uv tool install https://github.com/fer-aguirre/numerical-expressions/archive/refs/heads/main.zip
  ```

- **pipx** does the same, if you already use it:

  ```
  pipx install https://github.com/fer-aguirre/numerical-expressions/archive/refs/heads/main.zip
  ```

- **From a copy of the code:** download or clone the repository, open a terminal in its folder and run `pip install .`

---

## How to use it

Type `numexp`, then the **old number**, then the **new number**:

```
numexp 48200 61500
```

- Write numbers without commas: `1550000`, not `1,550,000`. Decimals use a point: `3.6`.
- Add options after the numbers to change what you get. Each option is explained below.
- Suggestions come in blocks, one per kind of suggestion. (The examples here leave out the blank lines between blocks.)
- Lines starting with **Note** are advice. Lines starting with **Error** mean the comparison would mislead readers, and they say what to write instead.
- `numexp --help` shows a summary of everything in this guide.

### Describe a change

With no options, you get every standard way of describing the change:

```
$ numexp 48200 61500
61,500 is 13,300 more than 48,200
61,500 equals 127.59% of 48,200
61,500 is 27.59% higher than 48,200
61,500 is a 27.59% increase over 48,200
  Note: Rises and falls aren't symmetrical: going back from 61,500 to 48,200 would be a 21.63%
  fall, not 27.59%.
61,500 is 1.28 times as much as 48,200
The figure jumped 27.59%, from 48,200 to 61,500
The figure jumped by 13,300, from 48,200 to 61,500
```

The note is there because percent changes don't reverse: a 27.59% rise isn't undone by a 27.59% fall. It matters when a figure rises and then falls back, or the other way round.

Use `--subject` to say what's being measured, so the last sentences read like a lede:

```
$ numexp 48200 61500 --subject Homicides
...
Homicides jumped 27.59%, from 48,200 to 61,500
Homicides jumped by 13,300, from 48,200 to 61,500
```

These sentences start with the subject rather than a figure, so they can open a sentence. The AP Stylebook spells out a number that begins a sentence, so the other suggestions, which start with a figure, need rewording before they can lead.

The verb depends on the size of the change:

| Change | Rising | Falling |
|---|---|---|
| under 3% | edged up | edged down |
| 3% to 20% | rose | fell |
| 20% to 50% | jumped | fell sharply |
| 50% or more | surged | plunged |

### Round the figures

Exact figures like 27.59% are rarely what a story needs. Add `--hedge directional` to round them with an honest qualifier:

```
$ numexp 48200 61500 --subject Homicides --hedge directional -o percentage_difference trend
61,500 is nearly 28% higher than 48,200
61,500 is a nearly 28% increase over 48,200
  Note: Rises and falls aren't symmetrical: going back from 61,500 to 48,200 would be a 21.63%
  fall, not 27.59%.
Homicides jumped nearly 28%, from 48,200 to 61,500
Homicides jumped by more than 13,000, from 48,200 to 61,500
```

"Nearly" means the real figure is a little lower, and "more than" means it's a little higher. If you'd rather not say which way it was rounded, use `--hedge roughly`, which gives "roughly 28%".

### Add units: money, people, anything

Use `--unit`. Put a currency symbol in quotes. Large numbers are written the way readers expect ("$1.2 million"):

```
$ numexp 1200000 1550000 --unit '$'
$1.55 million is $350,000 more than $1.2 million
...

$ numexp 3 7 --unit people
Seven people is four people more than three people
```

Numbers under 10 are spelled out, following the general rule of the [AP Stylebook](https://www.apstylebook.com/) ("eight editors, two cats"). AP keeps figures for measurements, and so does the tool when the unit is one it recognizes, such as `km`, `kg`, `tonnes`, `toneladas` or `hectares`:

```
$ numexp 3 7 --unit km
7 km is 4 km more than 3 km
```

For anything else that AP writes in figures, such as ages, add `--style figures` to always use digits. AP also spells out "zero percent", and the tool does the same.

### Percentages: points, not percent

When both numbers are already percentages, such as unemployment, poverty or vote share, add `%` to both. The tool then gives the change in **percentage points** and warns you not to mix the two up:

```
$ numexp 4.1% 3.6% --subject Unemployment
3.6% is 0.5 percentage points lower than 4.1%
3.6% is 12.2% lower than 4.1%
Unemployment fell 0.5 percentage points, from 4.1% to 3.6% (a 12.2% relative change)
  Note: Both values are percentages: the difference is 0.5 percentage points, while the
  relative change is 12.2%. Don't write '0.5%' when you mean percentage points.
```

"Unemployment fell 0.5%" would be wrong here: it means a fall to about 4.08%.

### Polls: is the change real?

When the percentages come from a survey, add `--sample` with the number of people surveyed. The tool works out the margin of error and tells you whether the change is within it:

```
$ numexp 42% 45% --sample 625 --subject "Support for the president" -o trend
Support for the president rose 3 percentage points, from 42% to 45% (a 7.14% relative change)
  Note: Both values are percentages: the difference is 3 percentage points, while the relative
  change is 7.14%. Don't write '3%' when you mean percentage points.
  Note: With a sample of 625 people, the margin of error is about ±4 percentage points. This
  change of 3 percentage points is within it, so it may not be a real change.
```

A change within the margin of error shouldn't be reported as a rise or a fall. "Support was roughly unchanged" is safer.

### A part of a total ("one in five")

Put the **total first** and the **part second**, then add `-o share`:

```
$ numexp 16000000 3200000 -o share --unit people
One in five (3.2 million out of 16 million people)
One-fifth of the total (3.2 million out of 16 million people)
20% of the total (3.2 million out of 16 million people)
```

### Compare places of different sizes: rates

A city of 2 million will have more crimes than a town of 20,000, so comparing raw counts misleads. Put the **number of events first** and the **population second**, then add `-o rate`:

```
$ numexp 320 1937086 -o rate --unit murders
16.5 murders per 100,000 residents
320 murders in a population of 1.94 million is a rate of 16.5 per 100,000 residents
```

Per 100,000 residents is the usual base for crime and health figures. For a different base, add `--per`: `--per 1000` gives "per 1,000 residents". If the first number is bigger than the second, the tool asks you to check the order.

### Adjust for inflation

A budget or salary that rose in pesos, reais or dollars may have lost value once prices went up. Add a price index (usually the consumer price index, CPI) for each date: `--cpi-then` for the old number and `--cpi-now` for the new one.

```
$ numexp 5000000 9000000 --cpi-then 100 --cpi-now 211 --subject "The budget" -o inflation
5 million then is equivalent to 10.55 million at today's prices
9 million is 80% higher than 5 million in nominal terms, but 14.69% lower after adjusting for inflation
The budget surged 80% in nominal terms, but fell 14.69% after adjusting for inflation
  Note: Both index values must come from the same price index (for example, the national
  consumer price index) and have the same base year.
```

Get both index values from your country's statistics office (INDEC, IBGE, INEGI, DANE…), from the same index series. The tool doesn't include inflation data, because it changes every month.

### Risk: relative vs. absolute

Studies and press releases often say a risk "rose 50%" or "fell by half". That's the relative change, and on a small risk it can mean very little. Write both risks as percentages and add `-o risk`:

```
$ numexp 2% 3% -o risk
The risk went from two in 100 to three in 100
That is from one in 50 to about one in 33
That is a 50% increase in relative risk, or 1 percentage point in absolute risk
  Note: Press releases often quote only the relative change. Report the absolute risk too, so
  readers can judge how much it matters.
```

Readers understand "3 in 100" more easily than "3%", so lead with that.

### Make a big number relatable

Give a single number, and the tool compares it with the population of a country or city:

```
$ numexp 3000000
3 million is about the population of the city of Buenos Aires (3.12 million, INDEC Census 2022)
  Note: Check that the benchmark figure is current before publishing.
```

To do the same while comparing two numbers, add `--relatable`. The built-in comparisons are these populations, from each country's statistics office:

| Place | Population | Source |
|---|---:|---|
| Brazil | 214,211,951 | IBGE estimate 2026 |
| Mexico | 130,911,314 | INEGI estimate 2025 |
| Colombia | 53,057,212 | DANE projection 2025 |
| Argentina | 46,466,688 | INDEC projection 2026 |
| São Paulo (city) | 11,451,999 | IBGE Census 2022 |
| Mexico City | 9,209,944 | INEGI Census 2020 |
| Buenos Aires (city) | 3,121,707 | INDEC Census 2022 |

A comparison only appears when your number is within 10% of one of these. Always check that a figure is still current before you publish it. Your newsroom can add its own comparisons, such as stadium capacities or city budgets, with `--benchmarks FILE`. The file uses the same format as the built-in list in `numerical_expressions/phrasing/benchmarks.json`: a value, a label for each language, and a source.

### Write in Spanish or Portuguese

Add `--lang es` for Spanish, `--lang es-MX` for Spanish with Mexican number formatting ($1.2 millones, 30%), or `--lang pt` for Brazilian Portuguese:

```
$ numexp 1200000 1550000 --lang es-MX --unit '$' --subject "El presupuesto" --hedge directional -o trend
El presupuesto aumentó con fuerza casi 30%, de $1.2 millones a $1.55 millones
El presupuesto aumentó con fuerza en $350,000, de $1.2 millones a $1.55 millones

$ numexp 250 90 --lang pt --subject "O desmatamento" -o trend
O desmatamento despencou 64%, de 250 para 90
O desmatamento despencou 160, de 250 para 90
```

Put quotes around a subject with spaces, like "El presupuesto".

### Choose which suggestions you get

`-o` picks specific kinds of suggestion. For example, `-o trend` gives only the sentence, and `-o difference trend` gives the amount and the sentence.

| Name | What it gives | Example |
|---|---|---|
| `difference` | The change as an amount | 20 is 10 more than 10 |
| `percentage` | The new number as a percentage of the old | 20 equals 200% of 10 |
| `percentage_difference` | The percent change | 20 is 100% higher than 10 |
| `ratio` | Multiples and fractions | 30 is triple 10 · 30 is 3 times as much as 10 |
| `trend` | A news-style sentence | The figure rose 10%, from 100 to 110 |
| `share`\* | A part of a total (total first) | One in five (3.2 million out of 16 million) |
| `rate`\* | Events per 100,000 residents (events first) | 16.5 murders per 100,000 residents |
| `risk`\* | Relative and absolute risk (write both with %) | The risk went from two in 100 to three in 100 |
| `inflation`\* | Nominal vs. inflation-adjusted change (runs with `--cpi-then` and `--cpi-now`) | The budget surged 80% in nominal terms, but fell 14.69% after adjusting for inflation |
| `relatable`\* | A comparison with a population | 3 million is about the population of the city of Buenos Aires |
| `ratio_difference`\* | "N times more", explained | 30 is 2 times more than 10 (i.e. 3 times as much) |

\* Only when you ask for it.

`ratio_difference` is there for completeness. Readers often misread "times more": some take "2 times more than 10" to mean 20, others 30. Prefer "times as much", or a percentage.

---

## When it refuses

Some comparisons mislead readers, so the tool gives an **Error** and tells you what to write instead:

```
$ numexp 0 12 -o percentage_difference
Error: percentage_difference: cannot compare against an initial value of zero; describe the
absolute change instead: 12 is 12 more than zero
```

It refuses:
- **A percentage change from zero.** Going from 0 to 12 isn't an "infinite" increase. Say it went from zero to 12.
- **A percentage change across zero.** Going from a loss of 10 to a profit of 10 isn't a 200% increase. Describe the amounts.
- **Ratios of negative numbers.**
- **A share where the part is bigger than the total.** Check which number is which.
- **A rate with a population of zero**, or a risk that isn't written as a percentage between 0% and 100%.
- **An inflation adjustment without both price index values.**

---

## All options

| Option | What it does |
|---|---|
| `--subject TEXT`, `-s` | What is measured, for the news-style sentence: `--subject Unemployment` |
| `--hedge directional` | Round with "nearly" or "more than". `--hedge roughly` rounds with "roughly" |
| `--unit UNIT`, `-u` | Add a unit: `'$'`, `'R$'`, `'€'`, `people`, `personas`, `tonnes`… |
| `--style figures` | Always use digits, even for numbers under 10 |
| `--lang LANG`, `-l` | `en` (default), `es`, `es-MX` or `pt` |
| `-o NAME …` | Only these kinds of suggestion (see the table above) |
| `--percent`, `-p` | The numbers are percentages. Same as writing `4.1% 3.6%` |
| `--per N` | The population base for `-o rate` (default 100,000) |
| `--cpi-then INDEX`, `--cpi-now INDEX` | The price index at each date, to adjust for inflation |
| `--sample N` | For poll percentages: how many people were surveyed |
| `--relatable` | Also compare the numbers with populations |
| `--benchmarks FILE` | Use your newsroom's own comparisons |
| `--unit-position prefix` / `suffix` | Force the unit before or after the number |
| `--json` | Output for other programs: the value, suggestions, notes and any error for each kind of suggestion |

**Negative numbers** work as usual: `numexp -10 -5`. Negative *percentages* need the options first and the numbers after `--`, like this: `numexp -o trend -- -5% -2%`.

---

## Known limits

- **Spanish and Portuguese don't agree gender.** The tool always uses the masculine form, so it writes "uno de cada cinco" and "um em cada cinco". With a feminine noun, change it in your copy: "una de cada cinco personas", "uma em cada cinco pessoas", "duas em cada três pessoas".
- **Verbs for rates.** For percentages, the verb is chosen from the relative change. A rise from 2% to 3% is a 50% relative change, so it "surged". For rates, decide for yourself whether that verb fits.
- **The margin of error is a rule of thumb.** It uses Steve Doig's shortcut (1 divided by the square root of the sample size), which holds for a simple random sample at 95% confidence. Many polls use weighting or other designs with a larger margin, so check the pollster's own figure. Comparing two separate polls also needs a bigger change than one margin to be clear.
- **Rates say "residents".** If your population is something else, such as students or drivers, adjust the wording.
- **Population figures age.** The comparison figures come from 2020–2026 releases. Check the latest figure before publishing.

---

## Working on the website

The website lives in `web/`: `index.html`, `styles.css` and `app.js`. It loads [Pyodide](https://pyodide.org), which runs Python in the browser, and installs this package into it. So the website and `numexp` always give the same suggestions.

To try it on your computer, run this from a copy of the code:

```
uv run python scripts/build_web.py --serve
```

Then open http://localhost:8000. The build script packages the Python code into `web/dist/`; run it again after changing the code.

Every push to `main` runs the tests and publishes the website to GitHub Pages (`.github/workflows/website.yml`). Before the first time, in the repository's **Settings → Pages**, set **Source** to **GitHub Actions**.

---

## License

Released under the [MIT License](LICENSE).

## Acknowledgments

- [The Associated Press Stylebook](https://www.apstylebook.com/)
- Poynter's Numeracy Primer: How to Write About Numbers, for relative vs. absolute risk. The course page is no longer online; see its [tip sheet on reporting risk](https://journalistsresource.org/health/risk-health-journalism-tips-poynter/), republished by Journalist's Resource.
- [Newsroom Math Crib Sheet](https://www.datovazurnalistika.cz/wp-content/uploads/2014/07/Newsroom-Math-Crib-Sheet-Steve-Doig.pdf) by Steve Doig, for percent change, rates, inflation adjustment and the margin of error.
