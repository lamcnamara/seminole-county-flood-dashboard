# Seminole County flood dashboard

To request an edition, say **“Refresh the Seminole County flooding dashboard.”** This opens a manual review of warnings, river stages, forecasts, rain, roads, public notices and reporting. Opening the HTML reads the saved edition. Each source retains its own observation, issue or effective time.

The published file is `../Seminole-County-Flooding-Impact-Dashboard.html`. This folder holds the shared source register, expansion queue and edition history in `project.json`. The dashboard renders them under **Edition management** and includes a copy of this folder in its downloadable editing kit.

## Start a review

### Next data review

The issued snapshot is **November 24, 2026 at 8:37 am EST**. Both Seminole gauges measured major flooding at 7:30 am EST: 13.13 ft above Lake Harney and 8.01 ft near Sanford. Sanford first reached 8.0 ft at 6:45 am. The county listed 27 road locations and 25 facility closures. FHP continued to list the SR 46 crossing closure. County Order 2026-011 extended the local emergency for seven days. Check the noon NWS statements, subsequent readings at both gauges and the next county road bulletin. The road list is dated noon Monday. The latest archived rainfall bulletin remains the Nov 20 statement. [NWS warnings](https://beta.weather.gov/forecast/county/12117/) · [County bulletin](https://www.seminolecountyfl.gov/departments-services/prepare-seminole/emergency-event/flooding/) · [FHP incidents](https://trafficincidents.flhsmv.gov/SmartWebClient/CadView.aspx)

### Open a review

Run these commands in PowerShell from the project root with Python 3.9 or newer. Substitute the reviewer's name. Add `--contact` with an email address or project URL if you want agencies to have a contact for the requests.

```powershell
$run = python .\seminole-flood\refresh.py start --reviewer "Reviewer name"
python .\seminole-flood\refresh.py collect "$run"
```

The first command creates a timestamped directory under `seminole-flood/runs/`. It archives the issued page as `previous.html`, extracts its editing kit into `kit/`, and creates `run.json` and `source-review.csv`. The CSV starts with one pending row per source. Opening a new review leaves the issued page available. If working from the editing kit alone, place the issued HTML beside the `seminole-flood` folder or pass its full path with `start --dashboard`.

The second command saves agency responses, per-request metadata and a manifest under a new `captures/` directory for each attempt. For a targeted check, add e.g. `--source SRC-02`. Each .info file records the request URL, HTTP status when received, retrieval time and outcome. A nonzero exit means at least one request failed or needs inspection. A retry preserves earlier evidence. The collector handles the NWS county alert feed, NWPS metadata and series, four USGS stations and the NWS rainfall **index**. It does not issue an edition.

## Decide what can be published

1. **Review evidence.** Use `project.json` for source URLs, section mappings, review triggers and acceptance criteria. Check for paging or truncation. Save the selected rainfall product separately from its search index. Review the rendered county bulletin, road viewers, health and education notices, signed orders and original news articles manually. Store dated copies or citations beside the run. Keep map layers with their original retrieval dates until a change warrants checking them.
2. **Record each decision.** Fill the corresponding CSV row with the check time, the source's own time, a file path or exact URL, the reviewer and a decision. Use `changed`, `confirmed unchanged`, `empty`, `unavailable`, `withheld` or `not applicable`. Explain partial coverage, missing timestamps or conflicts. A successful empty alert response supports only the checked area, event filter and retrieval time. Preserve the prior record on failure. Show historical values with their original dates or omit them from current totals. Never infer open roads from a missing incident.
3. **Prepare the candidate.** Use the latest accepted files for each source. Copy matched JSON and .info pairs into `kit/samples/` under the existing sample keys. Keep unaccepted captures in `captures/`. Review the county section structure, station identity and units, forecast issuance, observation ages and rainfall period codes before normalization. Edit the signed-off editorial records and news review in the kit. For a quiet edition, describe the checked scope and any verified empty feeds. Omit unsupported warnings, forecasts, news or closures.
4. **Set the data cutoff.** Enter the edition ID and offset-aware capture cutoff in `kit/edition.json`. Use a distinct ID for a new published cutoff. Key any edited warning summaries to their exact CAP message IDs. A new message uses its agency text until reviewed. Keep the news review time in `samples/news-review.json`. Either run `python -X utf8 "$run/kit/prepare.py"` after checking the source-specific parser for the new bulletin format or update `kit/snapshot.json` directly from the accepted evidence. The latter route needs only the standard library for the build.
5. **Reconcile every surface.** Review `template.html` for the lead, warning summary, forecast milestones, upstream and tributary notes, road and facility counts, community instructions, rainfall callouts and access notes. Review the CAP summaries in `edition.json` and the station implications, table captions and chart assumptions in `build.py`. The baseline includes event-specific prose. Adapt affected renderers when a feed has no forecast or a different reach, product or bulletin structure. Use a visible “unavailable” explanation if a section cannot be supported. Add or update edition-specific assertions against independently reviewed evidence. Once the narrative and values agree, set the template's `editorial-edition` meta value to the edition ID.
6. **Log the outcome.** Add a newest-first entry to the project folder's `project.json` history with date, type, edition ID and a concise description. Use `Data edition`, `Correction`, `Review only` or `Maintenance`. For corrections, identify the old and corrected claim and the evidence. If nothing warrants a new data edition, keep the previous cutoff, record the review and its gaps, and rebuild only if publishing the history change. Record follow-up work under a stable expansion ID. The build copies the current project folder into the candidate kit.

## Build, test and issue

```powershell
python .\seminole-flood\refresh.py build "$run"
$candidate = Join-Path "$run" "Seminole-County-Flooding-Impact-Dashboard.html"
Start-Process $candidate
```

Build writes the candidate inside the run after offline checks pass. Check desktop and narrow widths. Compare the hero values, charts, alert count and tables with the archived evidence. Exercise road search and filters, rainfall periods, map zoom and community selection, fragment links and both downloads. Use the keyboard for the map dialog and checklist. Reload to confirm checklist persistence and inspect the console. Export the completed browser review log into the run. The CSV is the source-by-source editorial record. The browser checklist records the edition checks.

When the reviewed file is ready to issue, copy it to the original filename. Keep the run directory with the previous edition, issued candidate, source decisions, raw captures and review export.

```powershell
Copy-Item -LiteralPath $candidate -Destination .\Seminole-County-Flooding-Impact-Dashboard.html
```

To roll back, copy the same run's `previous.html` to the original filename. Record the rollback and reason in the project history. Retain the superseded candidate for comparison.

## Maintain the register

The finished November 21 edition passed offline browser checks at 1440 and 390 pixels. The headline and station cards agreed with the saved gauge observations. The map, road and rainfall filters, saved checklist, fragment links and downloads worked with no browser console errors. Building from the downloadable editing kit reproduced the issued HTML byte for byte.

The November 22 setup review reproduced the November 21 edition from its editing kit and checked the downloaded snapshot against the original bytes. Desktop and narrow offline browser checks covered the map, filters, register links, checklist persistence and downloads. The collector passed a replay of all 12 archived machine requests and cases for an empty feed, an outage and a changed response format. A direct live NWS alert request from the local execution environment encountered a DNS lookup failure. If that happens on a review, try the exact registry URL in a network-enabled browser. Save the response and its retrieval metadata or leave the source marked unavailable.

- **Sources.** Keep each `SRC-##` ID stable when an endpoint moves. Update its publisher, section, check trigger, method, acceptance rule and URL. Keep exact per-edition retrieval evidence in the run. For new machine feeds, test the response schema before adding a request mapping to the collector.
- **Expansion.** Each `EXP-##` row identifies its priority, status, source IDs, evidence link and next check. Move it from candidate review to implementation when the required sample and coverage are confirmed. Record the edition or technical issue when delivered. Use source checks and operational needs to reprioritize on each manual invocation.
- **History.** Keep the data cutoff separate from the management date. Source discovery or a successful request alone cannot advance an edition. The baseline edition is `2026-11-21-1823-EST`.

## Publication and corrections

The public dashboard and its refresh tools are maintained in the [Seminole County Flood Dashboard repository](https://github.com/lamcnamara/seminole-county-flood-dashboard). GitHub Pages serves the root of the `main` branch. Keep the HTML filename and existing section links stable between editions.

For a correction, identify the edition, affected section, relevant source ID and the issuing agency’s dated evidence. Use the [issue tracker](https://github.com/lamcnamara/seminole-county-flood-dashboard/issues) for corrections and proposed changes. Emergency reports belong with the responsible agency.

Before committing an edition, review the downloadable kit as well as the rendered page. Keep reviewer notes, exports and working captures in the local review directory. After deployment, open the [published dashboard](https://lamcnamara.github.io/seminole-county-flood-dashboard/), follow a section link and compare the displayed cutoff with the approved candidate.
