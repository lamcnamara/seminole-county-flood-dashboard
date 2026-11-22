"""Prepare a manual Seminole flood review or build its offline candidate."""
import argparse
import base64
import csv
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from html import escape
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parent
PAGE = "Seminole-County-Flooding-Impact-Dashboard.html"
PROJECT_FILES = ("project.json", "README.md", "AGENTS.md", "refresh.py")


def read_project(folder=PROJECT):
    return json.loads((folder / "project.json").read_bytes())


def link(url, label):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def render_register(project):
    """Render ordinary HTML so an exported page works with scripting disabled."""
    sources = []
    for source in project["sources"]:
        links = [link(source["url"], source["publisher"])]
        if "reference" in source:
            links.append(link(source["reference"], "Companion source"))
        sources.append(
            f'<article id="{escape(source["id"].lower())}"><h3>{escape(source["name"])}</h3>'
            f'<p class="register-meta">{escape(source["id"])} · {escape(source["trigger"])}</p>'
            f'<p>{escape(source["method"])}</p><p>{escape(source["accept"])}</p>'
            f'<p>{" · ".join(links)} · {link("#" + source["section"], "Dashboard section")}</p></article>'
        )
    opportunities = []
    for item in project["opportunities"]:
        refs = [link("#" + key.lower(), key) for key in item["sourceIds"]]
        opportunities.append(
            f'<li id="{escape(item["id"].lower())}"><strong>{escape(item["title"])}</strong>'
            f'<span class="register-meta">{escape(item["id"])} · {escape(item["priority"])} priority · {escape(item["status"])}</span>'
            f'<p>{escape(item["next"])}</p><p>{link(item["url"], "Source to evaluate")} · {" / ".join(refs)}</p></li>'
        )
    history = "".join(
        f'<li><strong>{escape(row["date"])} · {escape(row["type"])}</strong>'
        f'<p>{escape(row["note"])}</p><small>Edition {escape(row["edition"])}</small></li>'
        for row in project["history"]
    )
    return (
        '<section id="project"><header class="section-head"><h2>Edition management</h2></header>'
        '<p class="intro">Each edition begins with a manual source review. The editing kit includes the project register, '
        'capture command and publication guide. Opening this page works offline.</p>'
        '<div class="project-links">' + link("#review", "Open the review checklist") + ' · '
        + link("#edition-files", "Editing kit and evidence") + '</div>'
        f'<details id="source-register"><summary>Sources to check ({len(sources)})</summary>'
        f'<div class="inside feeds">{"".join(sources)}</div></details>'
        f'<details id="expansion"><summary>Expansion opportunities ({len(opportunities)})</summary>'
        f'<div class="inside"><ol class="project-list">{"".join(opportunities)}</ol></div></details>'
        '<details id="edition-history"><summary>Edition and maintenance history</summary>'
        f'<div class="inside"><ul class="project-list">{history}</ul></div></details></section>'
    )


def now():
    return datetime.now(timezone.utc)


def timestamp_id():
    return now().strftime("%Y%m%dT%H%M%S%fZ")


def sync_project(kit):
    destination = kit / "seminole-flood"
    destination.mkdir(exist_ok=True)
    for name in PROJECT_FILES:
        shutil.copyfile(PROJECT / name, destination / name)


def start_review(dashboard, runs, reviewer):
    raw = dashboard.read_bytes()
    match = re.search(rb'download="seminole-flood-editing-kit.zip" href="data:application/zip;base64,([^"]+)"', raw)
    edition = re.search(rb'<body data-edition="([^"]+)"', raw)
    if not match or not edition:
        raise ValueError("Choose a dashboard with an edition identifier and embedded editing kit.")
    project = read_project()
    runs.mkdir(parents=True, exist_ok=True)
    run = runs / timestamp_id()
    with tempfile.TemporaryDirectory(dir=runs) as staging:
        draft = Path(staging) / "draft"
        kit = draft / "kit"
        kit.mkdir(parents=True)
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(match[1], validate=True))) as archive:
            for member in archive.infolist():
                if not (kit / member.filename).resolve().is_relative_to(kit.resolve()):
                    raise ValueError(f"Invalid editing kit path: {member.filename}")
            archive.extractall(kit)
        sync_project(kit)
        (draft / "previous.html").write_bytes(raw)
        with (draft / "source-review.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["source_id", "source", "starting_url", "outcome", "checked_at", "source_as_of",
                             "evidence_file_or_url", "decision_or_gap", "reviewer"])
            for source in project["sources"]:
                writer.writerow([source["id"], source["name"], source["url"], "pending", "", "", "", "", reviewer])
        record = {"project": project["projectId"], "startedAt": now().isoformat(), "reviewer": reviewer,
                  "baseEdition": edition[1].decode(), "runId": run.name}
        (draft / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        draft.rename(run)
    return run


def capture_request(name, url, folder, contact):
    result = {"url": url, "http": None, "outcome": "unavailable"}
    user_agent = "SeminoleFloodDashboard/1.0" + (f" ({contact})" if contact else "")
    request = Request(url, headers={"User-Agent": user_agent,
                                    "Accept": "application/geo+json, application/ld+json, application/json"})
    try:
        with urlopen(request, timeout=20) as response:
            result.update(http=response.status, finalURL=response.geturl(), serverDate=response.headers.get("Date"),
                          access=response.headers.get("Access-Control-Allow-Origin"))
            payload = response.read()
        # Preserve a surprising response as evidence for the editor too.
        document = json.loads(payload)
        if name == "rainlist":
            records = document["@graph"]
        elif name == "alerts" or name.startswith("usgs"):
            records = document["features"]
        elif name.endswith("-meta"):
            if document["lid"].upper() != name.split("-")[0]:
                raise ValueError("Gauge identifier mismatch")
            records = [document]
        else:
            records = document["observed"]["data"]
            if not isinstance(document["forecast"]["data"], list):
                raise ValueError("Missing forecast series")
        if not isinstance(records, list):
            raise ValueError("Expected a list of results")
        result.update(outcome="received" if records else "empty", count=len(records))
        (folder / (name + ".json")).write_bytes(payload)
    except HTTPError as error:
        result.update(http=error.code, error=str(error))
    except (URLError, OSError, HTTPException) as error:
        result["error"] = str(error)
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        result.update(outcome="needs review", error=str(error))
        (folder / (name + ".response")).write_bytes(payload)
    result["retrieved"] = now().isoformat()
    (folder / (name + ".info")).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def collect(run, contact, selected):
    # Read the frozen register from this run. A retry gets its own evidence folder.
    project = read_project(run / "kit" / "seminole-flood")
    machine = {s["id"]: s for s in project["sources"] if s.get("requests")}
    chosen = list(dict.fromkeys(selected or machine))
    if set(chosen) - machine.keys():
        raise ValueError("Collectable source IDs: " + ", ".join(machine))
    folder = run / "captures" / timestamp_id()
    folder.mkdir(parents=True)
    end = now()
    window = {k: d.strftime("%Y-%m-%dT%H:%M:%SZ") for k, d in (("start", end - timedelta(hours=72)), ("end", end))}
    manifest = []
    for source_id in chosen:
        for name, url in machine[source_id]["requests"].items():
            result = capture_request(name, url.format(**window), folder, contact)
            manifest.append({"sourceId": source_id, "sample": name, **result})
            print(f'{name}: {result["outcome"]}', flush=True)
            (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(folder)
    return 1 if any(entry["outcome"] in ("unavailable", "needs review") for entry in manifest) else 0


def build_candidate(run):
    kit = run / "kit"
    sync_project(kit)
    with tempfile.TemporaryDirectory(dir=run) as staging:
        candidate = Path(staging) / PAGE
        for script in ("build.py", "verify.py"):
            subprocess.run([sys.executable, "-X", "utf8", str(kit / script), str(candidate)], check=True)
        candidate.replace(run / PAGE)
    return run / PAGE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start", help="Archive the current page and open a fresh offline review")
    start.add_argument("--dashboard", type=Path, default=PROJECT.parent / PAGE)
    start.add_argument("--runs", type=Path, default=PROJECT / "runs")
    start.add_argument("--reviewer", default="")
    capture = commands.add_parser("collect", help="Retrieve raw machine-readable evidence for one review")
    capture.add_argument("run", type=Path)
    capture.add_argument("--contact", help="Optional contact for the agency request User-Agent")
    capture.add_argument("--source", action="append", help="Limit to one machine source ID; repeat as needed")
    build = commands.add_parser("build", help="Build and verify a candidate from a reviewed kit")
    build.add_argument("run", type=Path)
    args = parser.parse_args()
    if args.command == "start":
        print(start_review(args.dashboard, args.runs, args.reviewer).resolve())
        return 0
    run = args.run.resolve()
    if json.loads((run / "run.json").read_bytes())["project"] != read_project()["projectId"]:
        raise ValueError("Choose a run for this project.")
    if args.command == "collect":
        return collect(run, args.contact, args.source)
    print(build_candidate(run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
