# AI source monitor

A daily routine (22:59 KST) checks these sources and emails what changed:

| Source | What counts as new |
|---|---|
| Epoch AI data hub (epoch.ai/data) | a dataset added or its "Updated" date changed |
| AI Incident Database RSS | a report not seen before |
| OECD.AI Wonk blog | a post not seen before |
| Stanford HAI AI Index | a new report year |
| Korean laws with "인공지능" in the name (Korean Law connector) | a law added, or its MST, promulgation or effective date changed; new scheduled amendments |

- `ai_sources.py` fetches the four websites, diffs against `state.json`, prints a JSON report and rewrites `state.json`. Stdlib only.
- `laws.json` holds the law baseline; the routine updates it after each check.
- The environment's network policy must allow epoch.ai, incidentdatabase.ai, oecd.ai and hai.stanford.edu.
- A source that fails to parse keeps its previous snapshot and is reported as an error, so a layout change shows up instead of silently dropping out.
