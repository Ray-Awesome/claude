"""Snapshot AI data sources and report what changed since the last run.

Usage: python3 monitor/ai_sources.py [state.json]
Prints a JSON report of new/changed items and rewrites the state file.
Korean law changes are checked separately by the routine (Korean Law connector).
"""
import html
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (ai-source-monitor)"}


def fetch(url):
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    ctx = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", "replace")


MONTHS = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]


def epoch():
    # The page embeds its dataset list as JSON props: one object per data explorer
    # (page url) and one per download (has "type"). Both carry id, title and date.
    t = html.unescape(fetch("https://epoch.ai/data"))
    pat = re.compile(r'\{"id":\[0,"([^"]+)"\],"title":\[0,"([^"]+)"\],(.*?)"date":\[3,"(\d{4})-(\d\d)-(\d\d)')
    pages, items = {}, {}
    for i, title, body, y, m, d in pat.findall(t):
        url = re.search(r'"url":\[0,"([^"]+)"\]', body)
        if '"type":' not in body:
            if url:
                pages[i] = url.group(1)
            continue
        items[i] = {"title": title, "updated": f"{MONTHS[int(m) - 1]} {int(d)}, {y}"}
    return {"https://epoch.ai" + pages.get(i, f"/data/{i}"): v for i, v in items.items()}


def aiid():
    t = fetch("https://incidentdatabase.ai/rss.xml")
    items = {}
    for it in re.findall(r"<item>(.*?)</item>", t, re.S):
        g = lambda tag: (re.search(rf"<{tag}(?:\s[^>]*)?>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>", it, re.S) or [None, ""])[1].strip()
        cite = re.search(r"\(https://incidentdatabase\.ai/cite/(\d+)", it)
        items[g("guid")] = {"title": html.unescape(g("title")), "link": g("link"), "date": g("pubDate"),
                            "incident": cite.group(1) if cite else ""}
    return items


def oecd():
    t = fetch("https://oecd.ai/en/wonk")
    slugs = dict.fromkeys(re.findall(r'href="(/en/wonk/[a-z0-9\-]+)"', t))
    return {"https://oecd.ai" + s: {"title": s.rsplit("/", 1)[1].replace("-", " ")} for s in slugs}


def hai():
    t = fetch("https://hai.stanford.edu/ai-index")
    years = sorted(set(re.findall(r"/ai-index/(20\d\d)-ai-index-report", t)))
    return {f"https://hai.stanford.edu/ai-index/{y}-ai-index-report": {"title": f"{y} AI Index Report"} for y in years}


SOURCES = {"Epoch AI data": epoch, "AI Incident Database": aiid, "OECD.AI Wonk": oecd, "Stanford AI Index": hai}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "state.json")
    old = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    report = {"checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "sources": {}}
    new_state = {}
    for name, fn in SOURCES.items():
        prev = old.get(name)
        try:
            cur = fn()
            if not cur:
                raise ValueError("parsed 0 items; page layout may have changed")
        except Exception as e:  # keep the old snapshot so tomorrow still diffs against it
            report["sources"][name] = {"error": f"{type(e).__name__}: {e}"}
            if prev is not None:
                new_state[name] = prev
            continue
        new_state[name] = cur
        if prev is None:
            report["sources"][name] = {"first_run": True, "count": len(cur)}
            continue
        added = [dict(url=k, **v) for k, v in cur.items() if k not in prev]
        changed = [dict(url=k, before=prev[k], **v) for k, v in cur.items() if k in prev and prev[k] != v]
        report["sources"][name] = {"count": len(cur), "new": added, "changed": changed}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new_state, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
    print()


if __name__ == "__main__":
    main()
