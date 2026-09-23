// Numerical Expressions website.
// Runs the real Python package in the browser with Pyodide, so results match the CLI exactly.

"use strict";

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/";

// Tasks, in journalists' terms. Each lists the numbers it asks for and the operations it runs.
const TASKS = {
  change: {
    tag: "Change",
    name: "A change",
    hint: "Two numbers from different dates",
    numbers: [
      { key: "initial", label: "Old number", hint: "For example, last year's figure" },
      { key: "final", label: "New number", hint: "For example, this year's figure" },
    ],
    wording: ["unit", "subject"],
    operations: ["difference", "percentage", "percentage_difference", "ratio", "trend"],
    relatable: true,
  },
  percent: {
    tag: "Percentages",
    name: "Percentages and polls",
    hint: "Unemployment, vote share, any rate in %",
    numbers: [
      { key: "initial", label: "Old percentage", hint: "Write 4.1 for 4.1%" },
      { key: "final", label: "New percentage", hint: "Write 3.6 for 3.6%" },
      { key: "sample", label: "People surveyed", hint: "Only for polls: checks the margin of error", optional: true, wide: true, integer: true },
    ],
    wording: ["subject"],
    operations: ["difference", "percentage_difference", "trend"],
    options: { percent_values: true },
  },
  share: {
    tag: "Share",
    name: "Part of a total",
    hint: "“One in five”",
    numbers: [
      { key: "initial", label: "Total", hint: "Everyone, for example the population" },
      { key: "final", label: "Part", hint: "The group you're writing about" },
    ],
    wording: ["unit"],
    operations: ["share"],
  },
  rate: {
    tag: "Rate",
    name: "Rate per 100,000",
    hint: "Compare places of different sizes",
    numbers: [
      { key: "initial", label: "Number of events", hint: "For example, murders or cases" },
      { key: "final", label: "Population", hint: "People living there" },
      { key: "per", label: "Per how many residents", hint: "100,000 is usual for crime and health", wide: true, optional: true },
    ],
    wording: ["unit"],
    unitHint: "What you're counting, for example murders",
    operations: ["rate"],
  },
  inflation: {
    tag: "Money",
    name: "Money over time",
    hint: "Adjust for inflation",
    numbers: [
      { key: "initial", label: "Old amount", hint: "Money at the earlier date" },
      { key: "final", label: "New amount", hint: "Money today" },
      { key: "cpi_then", label: "Price index then", hint: "From your statistics office" },
      { key: "cpi_now", label: "Price index now", hint: "Same index series" },
    ],
    wording: ["unit", "subject"],
    operations: ["inflation"],
  },
  risk: {
    tag: "Risk",
    name: "Risk",
    hint: "Relative vs. absolute",
    numbers: [
      { key: "initial", label: "Old risk (%)", hint: "Write 2 for 2%" },
      { key: "final", label: "New risk (%)", hint: "Write 3 for 3%" },
    ],
    wording: [],
    operations: ["risk"],
    options: { percent_values: true },
  },
  relatable: {
    tag: "Context",
    name: "Make it relatable",
    hint: "Compare with a population",
    numbers: [{ key: "initial", label: "Number", hint: "For example, people affected", wide: true }],
    wording: ["unit"],
    operations: ["relatable"],
    single: true,
  },
};

const WORDING_FIELDS = {
  unit: { label: "Unit", hint: "$, R$, people, personas, km…" },
  subject: { label: "What is measured", hint: "Starts the news-style sentence, for example Homicides" },
};

// Example stories: each fills the form with real numbers to show what the tool does.
const EXAMPLES = [
  { task: "change", title: "Homicides", values: { initial: "48,200", final: "61,500" }, options: { subject: "Homicides" } },
  { task: "change", title: "Budget", values: { initial: "1,200,000", final: "1,550,000" }, options: { unit: "$", subject: "The budget", hedge: "directional" } },
  { task: "change", title: "From zero", values: { initial: "0", final: "12" }, options: {} },
  { task: "percent", title: "Unemployment", values: { initial: "4.1", final: "3.6" }, options: { subject: "Unemployment" } },
  { task: "percent", title: "Poll", values: { initial: "42", final: "45", sample: "625" }, options: { subject: "Support for the president" } },
  { task: "share", title: "Poverty", values: { initial: "16,000,000", final: "3,200,000" }, options: { unit: "people" } },
  { task: "rate", title: "Murder rate", values: { initial: "320", final: "1,937,086", per: "100,000" }, options: { unit: "murders" } },
  { task: "rate", title: "Homicidios (es)", values: { initial: "320", final: "1.937.086", per: "100.000" }, options: { unit: "homicidios", lang: "es" } },
  { task: "inflation", title: "Budget", values: { initial: "5,000,000", final: "9,000,000", cpi_then: "100", cpi_now: "211" }, options: { subject: "The budget" } },
  { task: "inflation", title: "Orçamento (pt)", values: { initial: "5.000.000", final: "12.000.000", cpi_then: "100", cpi_now: "211" }, options: { lang: "pt", unit: "R$", subject: "O orçamento" } },
  { task: "risk", title: "Medical study", values: { initial: "2", final: "3" }, options: {} },
  { task: "relatable", title: "3 million", values: { initial: "3,000,000" }, options: {} },
  { task: "relatable", title: "9 milhões (pt)", values: { initial: "9.000.000" }, options: { lang: "pt" } },
];

const KINDS = {
  difference: "The change as an amount",
  percentage: "As a percentage of the old number",
  percentage_difference: "Percent change",
  ratio: "As a multiple",
  trend: "News-style sentence",
  share: "Part of a total",
  rate: "Rate",
  risk: "Risk",
  inflation: "After inflation",
  relatable: "Comparison",
};

const DEFAULT_OPTIONS = { lang: "en", unit: "", subject: "", hedge: "off", style: "ap" };

const $ = (id) => document.getElementById(id);

let state = {
  task: "change",
  example: 0,
  values: {},
  options: { ...DEFAULT_OPTIONS },
  relatable: false,
};

let engine = null; // the Python run() function, once Pyodide has loaded

// ---------------------------------------------------------------------------------------
// Reading numbers the way journalists type them: "1,937,086", "1.937.086", "4,1", "3.6%".

function parseNumber(raw) {
  let text = String(raw ?? "").trim().replace(/[\s _]/g, "").replace(/%$/, "");
  if (text === "") return { empty: true };
  const negative = /^[-−–]/.test(text);
  text = text.replace(/^[-−–+]/, "");
  const commas = (text.match(/,/g) || []).length;
  const dots = (text.match(/\./g) || []).length;
  if (commas && dots) {
    // Both separators: the last one is the decimal point.
    const decimal = text.lastIndexOf(",") > text.lastIndexOf(".") ? "," : ".";
    const thousands = decimal === "," ? "." : ",";
    text = text.split(thousands).join("").replace(decimal, ".");
  } else if (commas || dots) {
    const sep = commas ? "," : ".";
    const count = commas || dots;
    const [, after] = text.split(sep);
    // "1,937,086" or "1.500": a separator followed by groups of three digits is thousands.
    // "0.125" is always a decimal: nobody writes thousands after a zero.
    const groupsOfThree = new RegExp(`^[1-9]\\d{0,2}(\\${sep}\\d{3})+$`).test(text);
    if (count > 1 || (groupsOfThree && after.length === 3)) text = text.split(sep).join("");
    else text = text.replace(sep, ".");
  }
  if (!/^\d+(\.\d+)?$/.test(text)) return { invalid: true };
  const value = Number(text) * (negative ? -1 : 1);
  return { value };
}

// ---------------------------------------------------------------------------------------
// Loading the Python engine.

async function loadEngine() {
  const status = $("status");
  try {
    const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
    await pyodide.loadPackage("micropip");
    const manifest = await (await fetch("dist/manifest.json")).json();
    const wheelUrl = new URL(`dist/${manifest.wheel}`, location.href).href;
    pyodide.globals.set("WHEEL_URL", wheelUrl);
    await pyodide.runPythonAsync(`
import micropip
# num2words lists docopt as a dependency only for its own command line; it isn't needed here.
await micropip.install("num2words", deps=False)
await micropip.install(WHEEL_URL, deps=False)

import json
from numerical_expressions import Options, describe_all

def run(payload):
    p = json.loads(payload)
    try:
        results = describe_all(p["initial"], p["final"], p["operations"], Options(**p["options"]))
    except ValueError as error:
        return json.dumps({"failure": str(error)})
    return json.dumps({"results": [r.to_dict() for r in results]}, ensure_ascii=False)
`);
    engine = pyodide.globals.get("run");
    status.dataset.state = "ready";
    status.textContent = "Ready";
    update();
  } catch (error) {
    console.error(error);
    status.dataset.state = "failed";
    status.textContent = "Couldn't load";
    showPlaceholder("The calculator couldn't load. Check your internet connection and reload the page. It needs to download about 10 MB the first time.");
  }
}

// ---------------------------------------------------------------------------------------
// Rendering.

function renderTasks() {
  const box = $("tasks");
  box.innerHTML = "";
  for (const [id, task] of Object.entries(TASKS)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "task";
    button.setAttribute("aria-pressed", String(id === state.task));
    button.innerHTML = `<span class="label"></span><b></b><span class="hint"></span>`;
    button.querySelector(".label").textContent = task.tag;
    button.querySelector("b").textContent = task.name;
    button.querySelector(".hint").textContent = task.hint;
    button.addEventListener("click", () => selectExample(EXAMPLES.findIndex((e) => e.task === id)));
    box.appendChild(button);
  }
}

function renderExamples() {
  const box = $("examples");
  box.innerHTML = "";
  EXAMPLES.forEach((example, index) => {
    if (example.task !== state.task) return;
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = example.title;
    chip.setAttribute("aria-pressed", String(index === state.example));
    chip.addEventListener("click", () => selectExample(index));
    box.appendChild(chip);
  });
}

function makeField({ key, label, hint, wide, numeric, value }) {
  const wrap = document.createElement("div");
  wrap.className = "field" + (wide ? " wide" : "");
  const id = `f-${key}`;
  wrap.innerHTML = `<label for="${id}"></label><input id="${id}" type="text" autocomplete="off"><small></small>`;
  wrap.querySelector("label").textContent = label;
  const input = wrap.querySelector("input");
  input.value = value ?? "";
  if (numeric) {
    input.className = "num";
    input.inputMode = "decimal";
  }
  const small = wrap.querySelector("small");
  small.textContent = hint || "";
  small.dataset.hint = hint || "";
  return { wrap, input, small };
}

function renderForm() {
  const task = TASKS[state.task];

  const numbers = $("numbers");
  numbers.innerHTML = "";
  for (const spec of task.numbers) {
    const { wrap, input } = makeField({ ...spec, numeric: true, value: state.values[spec.key] });
    input.addEventListener("input", () => { state.values[spec.key] = input.value; scheduleUpdate(); });
    numbers.appendChild(wrap);
  }

  const wording = $("wording");
  wording.innerHTML = "";
  for (const key of task.wording) {
    const spec = WORDING_FIELDS[key];
    const hint = key === "unit" && task.unitHint ? task.unitHint : spec.hint;
    const { wrap, input } = makeField({ key, label: spec.label, hint, wide: true, value: state.options[key] });
    input.addEventListener("input", () => { state.options[key] = input.value; scheduleUpdate(); });
    wording.appendChild(wrap);
  }

  for (const button of $("hedge").querySelectorAll("button")) {
    button.setAttribute("aria-pressed", String(button.dataset.value === state.options.hedge));
  }
  $("ap").checked = state.options.style === "ap";
  $("lang").value = state.options.lang;
  $("relatable-row").hidden = !task.relatable;
  $("relatable").checked = state.relatable;
}

function showPlaceholder(text) {
  $("results").innerHTML = "";
  const p = document.createElement("p");
  p.className = "placeholder";
  p.textContent = text;
  $("results").appendChild(p);
}

function copyText(text, button) {
  const done = () => {
    button.textContent = "Copied";
    button.classList.add("done");
    setTimeout(() => { button.textContent = button.dataset.label; button.classList.remove("done"); }, 1500);
  };
  if (navigator.clipboard?.writeText) navigator.clipboard.writeText(text).then(done, () => selectFallback(button));
  else selectFallback(button);
}

function selectFallback(button) {
  const target = button.closest(".line")?.querySelector("p") || $("results");
  const range = document.createRange();
  range.selectNodeContents(target);
  const selection = getSelection();
  selection.removeAllRanges();
  selection.addRange(range);
}

function renderResults(results) {
  const box = $("results");
  box.innerHTML = "";
  // The same refusal usually applies to several kinds of suggestion (a change from zero
  // can't be a percentage, a multiple or a trend), so show it once.
  const refusals = new Map();
  for (const result of results) {
    if (!result.error) continue;
    const reason = result.error.replace(/^\w+: /, "");
    if (!refusals.has(reason)) refusals.set(reason, []);
    refusals.get(reason).push(KINDS[result.operation] || result.operation);
  }
  for (const [reason, kinds] of refusals) {
    const card = document.createElement("article");
    card.className = "kind";
    card.innerHTML = `<header><span class="label"></span></header>`;
    card.querySelector(".label").textContent = `Not possible: ${kinds.join(", ").toLowerCase()}`;
    const row = flag("error", "Refused", reason);
    row.style.borderTop = "0";
    card.appendChild(row);
    box.appendChild(card);
  }
  for (const result of results) {
    if (result.error) continue;
    const card = document.createElement("article");
    card.className = "kind";
    card.innerHTML = `<header><span class="label"></span><code></code></header>`;
    card.querySelector(".label").textContent = KINDS[result.operation] || result.operation;
    card.querySelector("code").textContent = result.operation;

    for (const phrase of result.phrases) {
      const line = document.createElement("div");
      line.className = "line";
      line.innerHTML = `<p></p><button type="button" class="copy" data-label="Copy">Copy</button>`;
      line.querySelector("p").textContent = phrase;
      line.querySelector("button").addEventListener("click", (event) => copyText(phrase, event.currentTarget));
      card.appendChild(line);
    }
    for (const warning of result.warnings) card.appendChild(flag("note", "Note", warning));
    box.appendChild(card);
  }
}

function flag(kind, tag, text) {
  const row = document.createElement("div");
  row.className = `flag ${kind}`;
  row.innerHTML = `<span class="label"></span><span></span>`;
  row.firstChild.textContent = tag;
  row.lastChild.textContent = text;
  return row;
}

// ---------------------------------------------------------------------------------------
// Turning the form into a request for the Python package.

function readForm() {
  const task = TASKS[state.task];
  const numbers = {};
  let ok = true;
  for (const spec of task.numbers) {
    const input = $(`f-${spec.key}`);
    const small = input.parentElement.querySelector("small");
    const parsed = parseNumber(input.value);
    let problem = null;
    if (parsed.invalid) problem = "Write a number, for example 1937086 or 1,937,086";
    else if (parsed.empty && !spec.optional) problem = "Required";
    else if (spec.integer && !parsed.empty && !Number.isInteger(parsed.value)) problem = "Write a whole number";
    input.setAttribute("aria-invalid", String(Boolean(problem) && !(parsed.empty && !input.value)));
    if (problem) {
      ok = false;
      small.className = parsed.empty ? "" : "bad";
      small.textContent = parsed.empty ? small.dataset.hint : problem;
      continue;
    }
    // Show how an input with separators was read, so "1.500" never silently becomes 1.5.
    const shown = !parsed.empty && /[.,]/.test(input.value) ? `Read as ${parsed.value}` : "";
    small.className = shown ? "read" : "";
    small.textContent = shown || small.dataset.hint;
    if (!parsed.empty) numbers[spec.key] = parsed.value;
  }
  return ok ? numbers : null;
}

function buildRequest(numbers) {
  const task = TASKS[state.task];
  const options = {
    lang: state.options.lang,
    hedge: state.options.hedge,
    style: state.options.style,
    ...(task.options || {}),
  };
  for (const key of task.wording) {
    const value = (state.options[key] || "").trim();
    if (value) options[key] = value;
  }
  for (const key of ["sample", "per", "cpi_then", "cpi_now"]) {
    if (numbers[key] !== undefined) options[key] = numbers[key];
  }
  const operations = [...task.operations];
  if (task.relatable && state.relatable) operations.push("relatable");
  return {
    initial: numbers.initial,
    final: task.single ? numbers.initial : numbers.final,
    operations,
    options,
  };
}

let timer = null;
function scheduleUpdate() {
  clearTimeout(timer);
  timer = setTimeout(update, 180);
}

function update() {
  const numbers = readForm();
  if (!engine) {
    showPlaceholder("Loading the calculator. The first visit downloads about 10 MB and takes a few seconds; after that it's quick.");
    return;
  }
  if (!numbers) {
    showPlaceholder("Fill in the numbers on the left to see suggestions.");
    return;
  }
  const response = JSON.parse(engine(JSON.stringify(buildRequest(numbers))));
  if (response.failure) showPlaceholder(response.failure);
  else renderResults(response.results);
}

function selectExample(index) {
  const example = EXAMPLES[index];
  state = {
    task: example.task,
    example: index,
    values: { ...example.values },
    options: { ...DEFAULT_OPTIONS, ...example.options },
    relatable: false,
  };
  renderTasks();
  renderExamples();
  renderForm();
  update();
}

// ---------------------------------------------------------------------------------------
// Controls that don't depend on the task.

for (const button of $("hedge").querySelectorAll("button")) {
  button.addEventListener("click", () => {
    state.options.hedge = button.dataset.value;
    for (const other of $("hedge").querySelectorAll("button")) other.setAttribute("aria-pressed", String(other === button));
    update();
  });
}
$("ap").addEventListener("change", () => { state.options.style = $("ap").checked ? "ap" : "figures"; update(); });
$("relatable").addEventListener("change", () => { state.relatable = $("relatable").checked; update(); });
$("lang").addEventListener("change", () => { state.options.lang = $("lang").value; update(); });
$("form").addEventListener("submit", (event) => { event.preventDefault(); update(); });
$("copy-all").addEventListener("click", (event) => {
  const text = [...$("results").querySelectorAll(".line p")].map((p) => p.textContent).join("\n");
  if (text) copyText(text, event.currentTarget);
});

selectExample(0);
loadEngine();
