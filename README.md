# Seminole County Flooding Impact Dashboard

Explore the November 2026 flooding along the St. Johns River in Seminole County, Florida. The dashboard brings the Lake Harney and Sanford river gauges together with a county reference map, road reports, rainfall measurements and local notices.

**[Open the dashboard](https://lamcnamara.github.io/seminole-county-flood-dashboard/)**

The flood data were captured through **November 25, 2026 at 11:55 a.m. EST**. The local news review closed at **11:59 a.m. EST**. Each warning, observation and forecast carries its own time. For current warnings, road conditions and public instructions, use the [National Weather Service](https://beta.weather.gov/forecast/county/12117/), [FL511](https://www.fl511.com/) and [Seminole County Emergency Management](https://www.seminolecountyfl.gov/departments-services/prepare-seminole/).

Provisional USGS observations at 11:30 am EST were 13.21 ft above Lake Harney and 8.43 ft near Sanford, both in major flood stage. NWS forecast 8.5 ft near Sanford Wednesday evening. The county listed 25 road locations and 20 flood-related recreation closures, plus one trail closed for construction. FHP still listed the SR 46 crossing as closed. The county also posted Thanksgiving hours for its three supply sites.

## Reading the edition

| Section | What you can check |
| --- | --- |
| [River levels and outlook](https://lamcnamara.github.io/seminole-county-flood-dashboard/Seminole-County-Flooding-Impact-Dashboard.html#levels) | Compare measured stages with the forecast issued for each reach. Each gauge uses its own flood thresholds. |
| [Roads and public access](https://lamcnamara.github.io/seminole-county-flood-dashboard/Seminole-County-Flooding-Impact-Dashboard.html#roads) | Search the 25 distinct county road locations by location and condition. State road closures have separate agency citations. |
| [Rainfall](https://lamcnamara.github.io/seminole-county-flood-dashboard/Seminole-County-Flooding-Impact-Dashboard.html#rain) | Compare the 18 station reports by accumulation period and ending time. |
| [Sources and edition files](https://lamcnamara.github.io/seminole-county-flood-dashboard/Seminole-County-Flooding-Impact-Dashboard.html#edition-files) | Download the source snapshot or the editing kit, including the agency samples and selected source fields, map inputs, page builder and verifier. |

USGS supplies the observed stages above Lake Harney, near Sanford and at the tributary gauges. NOAA’s National Water Prediction Service supplies the river forecasts and upstream Cocoa readings. NWS Melbourne issues the warnings and rainfall bulletin. County and state agencies are cited separately for road and facility notices. The [source register](seminole-flood/project.json) records each source’s scope and acceptance criteria.

## Open offline or prepare a new edition

Download [the standalone HTML file](Seminole-County-Flooding-Impact-Dashboard.html) and open it in a browser. The map, charts, filters and data downloads work offline. Opening the file displays the saved edition.

For a manual refresh, follow the [maintainer guide](seminole-flood/README.md). It covers collecting evidence, reviewing changes, rebuilding the page, and verifying the result before publication. A browser review checklist can be saved locally and exported. Each new data edition has its own identifier and Eastern cutoff.

To reproduce the current edition, download and extract the editing kit from the dashboard, then run these commands in the extracted folder with Python 3.9 or newer.

```shell
python -X utf8 build.py
python -X utf8 verify.py Seminole-County-Flooding-Impact-Dashboard.html
```

Please include the edition ID and a dated source when [reporting a correction](https://github.com/lamcnamara/seminole-county-flood-dashboard/issues). This edition is `2026-11-25-1155-EST`.
