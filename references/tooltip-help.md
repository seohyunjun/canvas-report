# Help tooltips

A report has **two kinds** of tooltip. One engine, two jobs.

| | Value tooltip | Help tooltip |
|---|---|---|
| Trigger | hover/focus on a chart mark | hover · focus · tap on any `[data-help]` element |
| Content | the number | how to read it, what it means, what to watch for |
| Hierarchy | value emphasised, name secondary | title emphasised, body explains |
| Without it | the chart cannot be explored | the chart gets misread |

## Where they go

| Position | Content | Required |
|---|---|---|
| `?` chip beside a chart title | what am I looking at · how do I read it · what can I do | ✅ every chart |
| a derived metric's name (dotted underline) | the formula, the denominator, whether it is an estimate | ✅ every computed metric |
| a stat tile's label | what the comparison is against | recommended |
| an axis label / legend item | any non-obvious choice, such as an axis not starting at zero | when applicable |
| a filter control | what changes, and what does **not** change | recommended |
| a section title | why this lens | optional |

## Writing the copy

Never more than three sentences. The order is fixed.

```
1) what it shows      "The total per period."
2) how to read it     "A bar above zero is growth, below zero is decline."
3) what you can do    "Click a bar to expand the detail below."
note) the caveat      "The axis does not start at zero."
```

- Do not name the chart type. "This is a line chart" is not information.
- **Define with a formula.** "per-capita amount = total ÷ headcount" beats "the average amount".
- Say the word "estimate" inside the tooltip when the number is one.
- Write about where readers actually go wrong. If two similar metrics have different definitions,
  put the difference in the `note`.

## The accessibility contract (implemented by the shell's `wireHelp()`)

- Mouse hover, keyboard focus and touch tap all open the same content.
- A tap pins it; clicking outside or pressing `Esc` closes it. Scrolling closes it.
- Title and body are joined into an `aria-label` so a screen reader gets them.
- The tooltip container is `pointer-events:none`, so it never covers its own trigger.
- It flips to the other side when it would leave the viewport.
- **No information exists only in a tooltip.** The same content must also be in a `card-note`
  or the methodology section.

## Inserting values safely

Series names and category names come from the data — a CSV header, an API response, user input.
**Always use `textContent` / `createTextNode`.** Never concatenate into `innerHTML`.
The shell's `showData` / `showHelp` already do this. Use those functions instead of hand-rolling
a tooltip.

## Localisation

Every fixed string the reader sees lives in the shell's `[L] CR_STRINGS` block. Translate that
block, not the code. The copy you write for a specific report — chart titles, help bodies,
card notes — is written directly in the wiring, in whatever language the report is in.
Number and date formatting follow `<html lang="...">` through `Intl`.
