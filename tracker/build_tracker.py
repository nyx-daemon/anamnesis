"""Build the public Anamnesis project tracker from tracker.json. Standard library only.

The sanitizer runs first and fails closed: nothing is written unless the data and every rendered output
pass the deny list (deny_terms.txt, one regex per line, matched case-insensitively), carry no invisible
characters (Unicode Default_Ignorable ranges) and no control characters other than newline, and repeat
no five-word run of the owner's quoted words from the private source notes.

Outputs, beside this script unless --out says otherwise:
  shell.html            the published page: about 30 KB of markup, CSS and a plain-JavaScript renderer that
                        fetches tracker.public.json from beside itself and draws every section client-side. It holds
                        no item text. Its fallback (JavaScript off, fetch failed or timed out) names the data files,
                        the commit the shell was built at and the Colony post, baked in from the data's colony field.
                        Rendered from shell_template.html (--shell-template), with CSS, KINDS, VOCAB and TONE filled
                        in from this script. A rebuild whose shell differs only in its commit stamp leaves the
                        existing shell.html untouched, so the shell changes only when its content does.
  TRACKER.md            the same content as plain markdown, for agents that cannot run JavaScript
  tracker.public.json   the same data as tracker.json
  tracker.html          the old static page (every item rendered, the dataset embedded as application/json); kept
                        as a local reference, no longer published
tracker.json itself is stamped with as_of_commit and built_at.

The Artifact publishes shell.html as its page, with tracker.public.json and TRACKER.md beside it as supporting files.
A data refresh replaces only the supporting files, which needs a file listing, not a read of the page. REFRESH.md
is the runbook; refresh_tracker.sh builds, verifies and prints the calls.

Usage:
  python3 -I build_tracker.py               build
  python3 -I build_tracker.py --self-test   prove the build refuses a deny term and a U+200B, in the data and in
                                            the shell template
  python3 -I build_tracker.py --novel       list sentences in the data not found in the public sources
  options: --data PATH  --out DIR  --commit SHA  --shell-template PATH
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent
DENY_FILE = HERE / "deny_terms.txt"
SHELL_TEMPLATE = HERE / "shell_template.html"
SHELL_MAX_BYTES = 64 * 1024   # the shell exists to be cheap to read before a republish
COLONY_URL = re.compile(r"https://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~%/-]*)?")
# Public sources, whose wording the data reuses (for --novel), and the notes that hold the owner's quotes.
PUBLIC_SOURCES = ["public/anamnesis_digest.md", "format_panel_2026-11-26.md", "format_tests_2026-11-26.md",
                  "D3_panel_2026-11-26.md"]
QUOTE_SOURCES = ["format_panel_2026-11-26.md", "format_tests_2026-11-26.md", "D3_panel_2026-11-26.md",
                 "07_decisions.md", "08_episode_schema.md"]
DIGEST = "public/anamnesis_digest.md"
FONT_LINK = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Commissioner:wght@400;600;700'
             '&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">')

UI_KEYS = ["eyebrow", "marks_note", "map_kicker", "tasks_kicker", "footer_data", "no_falsify"]
KINDS = ["decision", "option", "task", "test", "fact", "question", "assumption", "risk"]
VOCAB = {"decision": ["decided", "proposed", "open"], "option": ["decided", "proposed", "open"],
         "task": ["todo", "claimed", "in-progress", "blocked", "done"],
         "test": ["planned", "pre-registered", "running", "run"], "fact": ["measured", "inferred", "hypothesis"],
         "question": ["open", "answered"], "assumption": ["untested", "supported", "refuted"],
         "risk": ["open", "mitigated", "accepted"]}
TONE = {"decided": "dec", "done": "dec", "run": "dec", "measured": "dec", "answered": "dec", "supported": "dec",
        "mitigated": "dec", "accepted": "dec",
        "proposed": "pro", "in-progress": "pro", "claimed": "pro", "running": "pro", "pre-registered": "pro",
        "inferred": "pro",
        "open": "opn", "todo": "opn", "planned": "opn", "hypothesis": "opn", "untested": "opn",
        "blocked": "blk", "refuted": "blk"}
EV_KINDS = {"measured", "inferred", "hypothesis"}
# Coverage the tracker promises. A missing id fails the build.
REQUIRED = (["D%d" % i for i in range(11)] + ["D3.Q1", "D3.Q2", "D3.A", "D3.B", "D3.C", "D3.call"]
            + ["FT", "FT.opt1", "FT.opt2", "FT.opt3", "FT.opt4", "FT.panel", "FT.call", "FT.env", "FT.checks"]
            + ["T.M1", "T.M2", "T.G", "T.R", "T.R2", "T.mut", "T.key", "T.harness", "T.field", "T.vendor"]
            + ["INV", "INV.rewrite", "G5.Q"] + ["G%d" % i for i in range(8)]
            + ["RG.producer", "RG.verifier", "RG.screen", "RG.classifier", "RG.index", "RG.signer"]
            + ["E%d" % i for i in range(1, 9)] + ["EV.08d", "RULEA", "GS2", "T0", "T2", "T2b", "T3a", "T3b", "T3c"]
            + ["M%d" % i for i in range(9)] + ["PB", "P.corpus"]
            + ["O1", "O2", "O3", "O4", "O5", "O6", "O7", "O8", "O9", "O10", "O11", "O12", "O13-15", "O16-20",
               "O19", "O21", "O22", "O23"])

# Unicode Default_Ignorable_Code_Point, as fixed ranges (the set the design spec writes out).
INVISIBLE = [(0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C), (0x115F, 0x1160), (0x17B4, 0x17B5),
             (0x180B, 0x180F), (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x206F), (0x3164, 0x3164),
             (0xFE00, 0xFE0F), (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3),
             (0x1D173, 0x1D17A), (0xE0000, 0xE0FFF)]
_inv_class = "".join(f"\\U{a:08x}-\\U{b:08x}" for a, b in INVISIBLE)
BAD_CHARS = re.compile(f"[{_inv_class}\\x00-\\x09\\x0b-\\x1f\\x7f-\\x9f]")


class Refused(Exception):
    pass


# ====================================================================== sanitizer
def load_deny():
    if not DENY_FILE.is_file():
        raise Refused(f"deny list missing: {DENY_FILE.name}")
    raw = DENY_FILE.read_text(encoding="utf-8")
    terms = [ln for ln in raw.split("\n") if ln.strip()]
    if not terms:
        raise Refused("deny list is empty")
    out = []
    for t in terms:
        try:
            out.append((t, re.compile(t, re.IGNORECASE)))
        except re.error as e:
            raise Refused(f"deny term does not compile: line {terms.index(t) + 1} ({e})") from None
    return out


def walk_strings(obj, path="$"):
    """Every decoded string in a JSON value, keys included."""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.<key>", k
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")


def scan_text(label, text, deny, hits):
    for t, rx in deny:
        for m in rx.finditer(text):
            hits.append(f"{label}: deny term on line {deny_index(deny, t)} of the list, at offset {m.start()}")
    for m in BAD_CHARS.finditer(text):
        hits.append(f"{label}: forbidden character U+{ord(m.group()):04X} at offset {m.start()}")


def deny_index(deny, t):
    return [x for x, _ in deny].index(t) + 1


def owner_quotes():
    """Quoted words in the private notes: italic quotes and parenthesised quotes, which is how the owner's are set."""
    quotes = set()
    for f in QUOTE_SOURCES:
        p = DOCS / f
        if not p.is_file():
            raise Refused(f"quote source missing, cannot check owner quotes: {f}")
        s = p.read_text(encoding="utf-8")
        quotes.update(re.findall(r'\*"([^"]+)"\*', s))             # italic quotes
        quotes.update(re.findall(r'\([^()"\n]*"([^"\n]+)"\)', s))    # a quote inside parentheses
    return quotes


def words(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def quote_hits(data_text, digest_text):
    """Five-word runs of an owner quote found in the data and not in the (sanitized) digest."""
    dw = " " + " ".join(words(digest_text)) + " "
    tw = " " + " ".join(words(data_text)) + " "
    hits = []
    for q in owner_quotes():
        w = words(q)
        if len(w) < 3:
            continue
        grams = [w] if len(w) < 5 else [w[i:i + 5] for i in range(len(w) - 4)]
        for g in grams:
            frag = " " + " ".join(g) + " "
            if frag in tw and frag not in dw:
                hits.append(f"data repeats {len(g)} words of a quoted line from the private notes")
                break
    return hits


def scan_html(page, deny, hits, label="tracker.html"):
    """The rendered page minus its static stylesheet and the one known font link."""
    s = re.sub(r"<style>.*?</style>", "", page, flags=re.S)
    if s.count(FONT_LINK) > 1:
        hits.append(f"{label}: font link repeated")
    s = s.replace(FONT_LINK, "")
    scan_text(label, s, deny, hits)


def scan_shell(shell, data, deny, hits):
    """The shell gets the page scan, and must stay small and free of item text: it is a renderer, not a copy."""
    # Like the static page, its <style> blocks are skipped (CSS property names trip the list): keep the template's
    # own CSS to a few rules, and put no words in it.
    scan_html(shell, deny, hits, "shell.html")
    size = len(shell.encode())
    if size > SHELL_MAX_BYTES:
        hits.append(f"shell.html: {size:,} bytes, over the {SHELL_MAX_BYTES:,} byte cap")
    for it in data["items"]:
        if it["title"] in shell or esc(it["title"]) in shell:
            hits.append(f"shell.html: carries the title of item {it['id']}")
            break


# ====================================================================== validation
def validate(data):
    errs = []
    for k in ("title", "about", "goal", "architecture", "technology", "vocab", "where_we_stand", "for_agents", "areas", "items", "colony",
              "ui"):
        if k not in data:
            errs.append(f"top level: missing {k}")
    for k in UI_KEYS:
        if not str(data.get("ui", {}).get(k, "")).strip():
            errs.append(f"top level: ui.{k} is missing or empty")
    if data.get("vocab") != VOCAB:
        errs.append("top level: vocab differs from the builder's status vocabulary")
    col = data.get("colony", {})
    for k in ("site", "colony", "post"):
        if not isinstance(col.get(k), str) or not col[k].strip():
            errs.append(f"top level: colony.{k} is missing or empty")
    if "url" in col and not (isinstance(col["url"], str) and COLONY_URL.fullmatch(col["url"])):
        errs.append("top level: colony.url must be a plain https URL")
    areas = [a["name"] for a in data.get("areas", [])]
    ids = [it.get("id") for it in data.get("items", [])]
    seen = set()
    for i in ids:
        if not isinstance(i, str) or not re.fullmatch(r"[A-Z][A-Za-z0-9]*(?:[.\-][A-Za-z0-9]+)*", i):
            errs.append(f"bad id: {i!r}")
        if i in seen:
            errs.append(f"duplicate id: {i}")
        seen.add(i)
    need = ["id", "kind", "area", "title", "status", "summary", "why", "evidence", "assumptions", "falsify", "tests",
            "depends_on", "discussion", "open_for_agents", "how_to_help", "sources", "updated"]
    for it in data.get("items", []):
        iid = it.get("id")
        for k in need:
            if k not in it:
                errs.append(f"{iid}: missing {k}")
        if errs and errs[-1].startswith(f"{iid}: missing"):
            continue
        if it["kind"] not in KINDS:
            errs.append(f"{iid}: unknown kind {it['kind']}")
        elif it["status"] not in VOCAB[it["kind"]]:
            errs.append(f"{iid}: status {it['status']} is not a {it['kind']} status")
        if it["area"] not in areas:
            errs.append(f"{iid}: unknown area {it['area']}")
        if not it["title"].strip() or not it["summary"].strip():
            errs.append(f"{iid}: empty title or summary")
        if not it["how_to_help"].strip():
            errs.append(f"{iid}: empty how_to_help")
        if not isinstance(it["open_for_agents"], bool):
            errs.append(f"{iid}: open_for_agents must be true or false")
        elif not it["open_for_agents"] and not str(it.get("local_only_reason", "")).strip():
            errs.append(f"{iid}: local-only without local_only_reason")
        for ref in it["tests"] + it["depends_on"] + ([it["parent"]] if it.get("parent") else []):
            if ref not in seen:
                errs.append(f"{iid}: reference to unknown id {ref}")
            if ref == iid:
                errs.append(f"{iid}: refers to itself")
        for e in it["evidence"]:
            if set(e) != {"claim", "value", "kind", "source"} or e["kind"] not in EV_KINDS:
                errs.append(f"{iid}: malformed evidence entry")
        for d in it["discussion"]:
            if set(d) != {"who", "gist", "source"}:
                errs.append(f"{iid}: malformed discussion entry")
        for s in it["sources"]:
            if set(s) != {"doc", "section", "commit"} or not re.fullmatch(r"[0-9a-f]{7,40}", s["commit"]):
                errs.append(f"{iid}: malformed source")
        if not it["sources"]:
            errs.append(f"{iid}: no source")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", it["updated"]):
            errs.append(f"{iid}: updated is not YYYY-MM-DD")
        if not all(isinstance(a, str) for a in it["assumptions"]):
            errs.append(f"{iid}: assumptions must be strings")
    for r in REQUIRED:
        if r not in seen:
            errs.append(f"coverage: required id {r} is missing")
    validate_arch(data.get("architecture"), seen, errs)
    validate_goal_tech(data.get("goal"), data.get("technology"), seen, errs)
    if errs:
        raise Refused("validation failed:\n  " + "\n  ".join(errs))


ARCH_KEYS = ("lede", "rules_head", "map_head", "flow_head", "layers_head", "map_note", "rules", "overlay", "lanes",
             "doors", "waits_on", "flow", "layers")


GOAL_KEYS = ("lede", "problems_head", "problems", "aims_head", "aims", "non_goals_head", "non_goals")
TECH_KEYS = ("lede", "rows", "survey_head", "survey", "survey_note")


def validate_goal_tech(goal, tech, seen, errs):
    """The goal and technology blocks: exact keys, text where text is due, and every id real."""
    def block(name, b, keys):
        if not isinstance(b, dict):
            errs.append(f"{name}: missing or not an object")
            return False
        if set(b) != set(keys):
            errs.append(f"{name}: keys must be exactly {', '.join(keys)}")
            return False
        return True

    def rows(name, rs, fields):
        if not isinstance(rs, list) or not rs:
            errs.append(f"{name}: empty")
            return
        for j, r in enumerate(rs):
            if not isinstance(r, dict) or set(r) != set(fields) | {"items"}:
                errs.append(f"{name}[{j}]: needs {', '.join(fields)} and items")
                continue
            for f in fields:
                if not isinstance(r[f], str) or not r[f].strip():
                    errs.append(f"{name}[{j}].{f}: empty or not text")
            ids = r["items"]
            if not isinstance(ids, list) or not ids or not all(isinstance(i, str) for i in ids):
                errs.append(f"{name}[{j}]: items must be a non-empty list of ids")
                continue
            errs.extend(f"{name}[{j}]: unknown id {i}" for i in ids if i not in seen)

    if block("goal", goal, GOAL_KEYS):
        for k in ("lede", "problems_head", "aims_head", "non_goals_head"):
            if not isinstance(goal[k], str) or not goal[k].strip():
                errs.append(f"goal {k}: empty or not text")
        for k in ("problems", "aims", "non_goals"):
            rows(f"goal {k}", goal[k], ("text",))
    if block("technology", tech, TECH_KEYS):
        for k in ("lede", "survey_head", "survey_note"):
            if not isinstance(tech[k], str) or not tech[k].strip():
                errs.append(f"technology {k}: empty or not text")
        rows("technology rows", tech["rows"], ("part", "choice", "why", "over"))
        rows("technology survey", tech["survey"], ("system", "took", "left"))


def validate_arch(arch, seen, errs):
    """The architecture map. Every box points at an existing item, because a dead id blanks the whole public page."""
    if not isinstance(arch, dict):
        errs.append("architecture: missing or not an object")
        return
    missing = [k for k in ARCH_KEYS if k not in arch]
    if missing:
        errs.append(f"architecture: missing {', '.join(missing)}")
        return
    if set(arch) - set(ARCH_KEYS):
        errs.append(f"architecture: unknown keys {sorted(set(arch) - set(ARCH_KEYS))}")

    def text(where, v):
        if not isinstance(v, str) or not v.strip():
            errs.append(f"architecture {where}: empty or not text")

    def refs(where, ids):
        if not isinstance(ids, list) or not ids or not all(isinstance(i, str) for i in ids):
            errs.append(f"architecture {where}: items must be a non-empty list of ids")
            return
        for i in ids:
            if i not in seen:
                errs.append(f"architecture {where}: unknown id {i}")

    def box(where, b, nested=False):
        if not isinstance(b, dict) or set(b) - {"name", "line", "items", "tag", "kids"}:
            errs.append(f"architecture {where}: malformed box")
            return
        text(f"{where} name", b.get("name"))
        text(f"{where} line", b.get("line"))
        refs(f"{where} {b.get('name')}", b.get("items"))
        if "tag" in b:
            text(f"{where} tag", b["tag"])
        if "kids" in b:
            if nested or not isinstance(b["kids"], list) or not b["kids"]:
                errs.append(f"architecture {where}: kids must be a non-empty list, one level deep")
                return
            for kd in b["kids"]:
                box(f"{where} {b.get('name')}", kd, nested=True)

    for k in ("lede", "rules_head", "map_head", "flow_head", "layers_head", "map_note"):
        text(k, arch[k])
    box("overlay", arch["overlay"])
    box("doors", arch["doors"])
    if not arch["doors"].get("kids"):
        errs.append("architecture doors: the doors are its kids, and there are none")
    if not isinstance(arch["lanes"], list) or not arch["lanes"]:
        errs.append("architecture lanes: empty")
    else:
        for ln in arch["lanes"]:
            if not isinstance(ln, dict) or set(ln) != {"name", "lede", "out", "nodes"} or not ln["nodes"]:
                errs.append("architecture lanes: a lane needs name, lede, out and nodes")
                continue
            text(f"lane {ln['name']} name", ln["name"])
            text(f"lane {ln['name']} lede", ln["lede"])
            if not isinstance(ln["out"], str):
                errs.append(f"architecture lane {ln['name']}: out must be text, empty for the last lane")
            for b in ln["nodes"]:
                box(f"lane {ln['name']}", b)
    for k in ("rules", "flow"):
        if not isinstance(arch[k], list) or not arch[k]:
            errs.append(f"architecture {k}: empty")
            continue
        for j, r in enumerate(arch[k]):
            if not isinstance(r, dict) or set(r) != {"text", "items"}:
                errs.append(f"architecture {k}[{j}]: needs text and items")
                continue
            text(f"{k}[{j}]", r["text"])
            refs(f"{k}[{j}]", r["items"])
    w = arch["waits_on"]
    if not isinstance(w, dict) or set(w) != {"lede", "items"}:
        errs.append("architecture waits_on: needs lede and items")
    else:
        text("waits_on lede", w["lede"])
        refs("waits_on", w["items"])
    if not isinstance(arch["layers"], list) or not arch["layers"]:
        errs.append("architecture layers: empty")
    else:
        for r in arch["layers"]:
            if not isinstance(r, dict) or set(r) != {"code", "name", "what", "git", "items"}:
                errs.append("architecture layers: a row needs code, name, what, git and items")
                continue
            for k in ("code", "name", "what", "git"):
                text(f"layer {r['code']} {k}", r[k])
            refs(f"layer {r['code']}", r["items"])


# ====================================================================== shared helpers
def esc(s):
    return html.escape(s, quote=True)


def inline(s):
    """Escape, then markdown-lite inline: `code`, **bold**, *italic*."""
    parts = re.split(r"(`[^`]+`)", s)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(f"<code>{esc(p[1:-1])}</code>")
            continue
        p = esc(p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", p)
        out.append(p)
    return "".join(out)


def md_block(text):
    """Markdown-lite blocks: paragraphs, - lists, 1. lists, | tables, fenced code."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        fence = re.match(r"^(```+|~~~~+)", ln)
        if fence:
            f = fence.group(1)
            j = i + 1
            body = []
            while j < len(lines) and not lines[j].startswith(f):
                body.append(lines[j])
                j += 1
            out.append(f'<pre class="fx"><code>{esc(chr(10).join(body))}</code></pre>')
            i = j + 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(md_table(rows))
            continue
        if re.match(r"^- ", ln):
            lis = []
            while i < len(lines) and re.match(r"^- ", lines[i]):
                lis.append(lines[i][2:])
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in lis) + "</ul>")
            continue
        m = re.match(r"^(\d+)\. ", ln)
        if m:
            start = int(m.group(1))
            lis = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                lis.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            st = f' start="{start}"' if start != 1 else ""
            out.append(f"<ol{st}>" + "".join(f"<li>{inline(x)}</li>" for x in lis) + "</ol>")
            continue
        para = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(- |\d+\. |\||```|~~~~)", lines[i]):
            para.append(lines[i])
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "".join(out)


def md_table(rows):
    def cells(r):
        r = r.strip()
        r = r[1:-1] if r.endswith("|") else r[1:]
        return [c.strip() for c in re.split(r"(?<!\\)\|", r)]
    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]] if len(rows) > 1 and re.match(r"^\|[\s:|-]+\|?$", rows[1]) else \
        [cells(r) for r in rows[1:]]
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = "".join("<tr>" + "".join(f"<td>{inline(c.replace(chr(92) + '|', '|'))}</td>" for c in r) + "</tr>"
                  for r in body)
    return f'<div class="tablewrap"><table class="t"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def relations(items):
    by = {it["id"]: it for it in items}
    needed_by = {i: [] for i in by}
    tested_for = {i: [] for i in by}
    children = {i: [] for i in by}
    for it in items:
        for d in it["depends_on"]:
            needed_by[d].append(it["id"])
        for t in it["tests"]:
            tested_for[t].append(it["id"])
        if it.get("parent"):
            children[it["parent"]].append(it["id"])
    return by, needed_by, tested_for, children


def counts(items):
    c = {}
    for it in items:
        c.setdefault(it["kind"], {}).setdefault(it["status"], 0)
        c[it["kind"]][it["status"]] += 1
    return c


# ====================================================================== markdown export
def arch_md(arch, by):
    """The architecture as text, for readers without JavaScript: the same boxes, in lane order, with live statuses."""
    def ref(i):
        return f"{i} ({by[i]['status']})"

    def box(b, indent=""):
        tag = f" `{b['tag']}`" if b.get("tag") else ""
        out = [f"{indent}- **{b['name']}**{tag} · {ref(b['items'][0])}. {b['line']}"
               + (f" Also: {', '.join(ref(i) for i in b['items'][1:])}." if len(b["items"]) > 1 else "")]
        for kd in b.get("kids", []):
            out += box(kd, indent + "  ")
        return out

    L = ["## Architecture", "", arch["lede"], "", f"### {arch['rules_head']}", ""]
    for j, r in enumerate(arch["rules"], 1):
        L.append(f"{j}. {r['text']} ({', '.join(ref(i) for i in r['items'])})")
    L += ["", f"### {arch['map_head']}", "", arch["map_note"], ""]
    L += box(arch["overlay"])
    L.append("")
    for j, ln in enumerate(arch["lanes"], 1):
        L += [f"#### {j}. {ln['name']}: {ln['lede']}", ""]
        for b in ln["nodes"]:
            L += box(b)
        if ln["out"]:
            L += ["", f"→ *{ln['out']}*"]
        L.append("")
    L += box(arch["doors"])
    L += ["", f"{arch['waits_on']['lede']} {', '.join(ref(i) for i in arch['waits_on']['items'])}.", "",
          f"### {arch['flow_head']}", ""]
    for j, r in enumerate(arch["flow"], 1):
        L.append(f"{j}. {r['text']} ({', '.join(ref(i) for i in r['items'])})")
    L += ["", f"### {arch['layers_head']}", "", "| Layer | What it is | In git? | Items |", "|---|---|---|---|"]
    for r in arch["layers"]:
        L.append(f"| `{r['code']}` {r['name']} | {r['what']} | {r['git']} | {', '.join(ref(i) for i in r['items'])} |")
    L.append("")
    return L


def arch_html(arch, by):
    """The architecture section. Mirrored by renderArch in shell_template.html: change both together."""
    def box(b):
        p = by[b["items"][0]]
        t = TONE[p["status"]]
        tag = f'<span class="tag">{esc(b["tag"])}</span>' if b.get("tag") else ""
        rest = "".join(chip(by, i, False) for i in b["items"][1:])
        kids = f'<div class="kids">{"".join(box(k) for k in b["kids"])}</div>' if b.get("kids") else ""
        return (f'<div class="an t-{t}"><a class="an-h" href="#{esc(p["id"])}" title="{esc(p["title"])}">'
                f'{mark(p["status"])}<b>{esc(b["name"])}</b>{tag}<em>{esc(p["id"])} · {esc(p["status"])}</em></a>'
                f'<p>{inline(b["line"])}</p>' + (f'<div class="chips">{rest}</div>' if rest else "") + f"{kids}</div>")

    def listed(rows, cls, show=False):
        return (f'<ol class="{cls}">' + "".join(
            f'<li>{inline(r["text"])}<span class="chips">{"".join(chip(by, i, show) for i in r["items"])}</span></li>'
            for r in rows) + "</ol>")

    lanes = []
    for j, ln in enumerate(arch["lanes"], 1):
        out = f'<p class="out">{inline(ln["out"])}</p>' if ln["out"] else ""
        lanes.append(f'<div class="lane"><h4><span class="n">{j}</span>{esc(ln["name"])}<small>{esc(ln["lede"])}'
                     f'</small></h4>{"".join(box(b) for b in ln["nodes"])}{out}</div>')
    rows = "".join(f'<tr><td><code>{esc(r["code"])}</code> {esc(r["name"])}</td><td>{inline(r["what"])}</td>'
                   f'<td>{esc(r["git"])}</td><td><div class="chips">{"".join(chip(by, i) for i in r["items"])}'
                   f"</div></td></tr>" for r in arch["layers"])
    return ('<section class="sec" id="arch"><h2>Architecture</h2>'
            f'<p class="alede">{inline(arch["lede"])}</p>'
            f'<h3 class="sub">{esc(arch["rules_head"])}</h3>{listed(arch["rules"], "rules", True)}'
            f'<h3 class="sub">{esc(arch["map_head"])}</h3><p class="kicker">{inline(arch["map_note"])}</p>'
            f'<div class="arch"><div class="ov">{box(arch["overlay"])}</div><div class="lanes">{"".join(lanes)}</div>'
            f'<div class="doors">{box(arch["doors"])}</div></div>'
            f'<p class="waits">{inline(arch["waits_on"]["lede"])}'
            f'{"".join(chip(by, i) for i in arch["waits_on"]["items"])}</p>'
            f'<h3 class="sub">{esc(arch["flow_head"])}</h3>{listed(arch["flow"], "flow")}'
            f'<h3 class="sub">{esc(arch["layers_head"])}</h3><div class="tablewrap"><table class="t"><thead><tr>'
            '<th>Layer</th><th>What it is</th><th>In git?</th><th>Items</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div></section>")


def goal_tech_md(goal, tech, by):
    """The goal and technology sections as text. Mirrored by goal_html/tech_html and the shell: change all together."""
    def ref(ids):
        return ", ".join(f"{i} ({by[i]['status']})" for i in ids)

    G = ["## The goal", "", goal["lede"], ""]
    for k, h in (("problems", "problems_head"), ("aims", "aims_head"), ("non_goals", "non_goals_head")):
        G += [f"### {goal[h]}", ""]
        G += [f"{j}. {r['text']} ({ref(r['items'])})" for j, r in enumerate(goal[k], 1)]
        G.append("")
    T = ["## Technologies, and why these", "", tech["lede"], ""]
    for r in tech["rows"]:
        T += [f"- **{r['part']}: {r['choice']}.** Why: {r['why']} Chosen over: {r['over']} ({ref(r['items'])})"]
    T += ["", f"### {tech['survey_head']}", "", "| System | Taken | Left | Items |", "|---|---|---|---|"]
    T += [f"| {r['system']} | {r['took']} | {r['left']} | {ref(r['items'])} |" for r in tech["survey"]]
    T += ["", tech["survey_note"], ""]
    return G, T


def goal_html(goal, by):
    def listed(rs):
        return ('<ol class="rules">' + "".join(
            f'<li>{inline(r["text"])}<span class="chips">{"".join(chip(by, i, False) for i in r["items"])}</span></li>'
            for r in rs) + "</ol>")
    cols = "".join(f'<div><h3 class="sub">{esc(goal[h])}</h3>{listed(goal[k])}</div>'
                   for k, h in (("problems", "problems_head"), ("aims", "aims_head"), ("non_goals", "non_goals_head")))
    return (f'<section class="sec" id="goal"><h2>The goal</h2><p class="alede">{inline(goal["lede"])}</p>'
            f'<div class="goalg">{cols}</div></section>')


def tech_html(tech, by):
    cards = "".join(
        f'<div class="tc"><span class="k">{esc(r["part"])}</span><b>{inline(r["choice"])}</b>'
        f'<p><span>Why</span> {inline(r["why"])}</p><p><span>Chosen over</span> {inline(r["over"])}</p>'
        f'<div class="chips">{"".join(chip(by, i, False) for i in r["items"])}</div></div>' for r in tech["rows"])
    rows = "".join(
        f'<tr><td>{esc(r["system"])}</td><td>{inline(r["took"])}</td><td>{inline(r["left"])}</td>'
        f'<td><div class="chips">{"".join(chip(by, i, False) for i in r["items"])}</div></td></tr>'
        for r in tech["survey"])
    return (f'<section class="sec" id="tech"><h2>Technologies</h2><p class="alede">{inline(tech["lede"])}</p>'
            f'<div class="techg">{cards}</div><h3 class="sub">{esc(tech["survey_head"])}</h3>'
            '<div class="tablewrap"><table class="t"><thead><tr><th>System</th><th>Taken</th><th>Left</th>'
            f'<th>Items</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<p class="kicker">{inline(tech["survey_note"])}</p></section>')


def render_md(data):
    items = data["items"]
    ui = data["ui"]
    by, needed_by, tested_for, children = relations(items)
    L = []
    L.append(f"# {data['title']}")
    L.append("")
    L.append(f"As of commit `{data['as_of_commit']}` · built {data['built_at']} · {len(items)} items")
    L.append("")
    L.append(data["about"])
    L.append("")
    G, T = goal_tech_md(data["goal"], data["technology"], by)
    L += G
    L += arch_md(data["architecture"], by)
    L += T
    L.append("## Where we stand")
    L.append("")
    for p in data["where_we_stand"]:
        L.append(f"- {p}")
    L.append("")
    c = counts(items)
    L.append("| Kind | Items | By status |")
    L.append("|---|---|---|")
    for k in KINDS:
        if k in c:
            parts = ", ".join(f"{s} {c[k][s]}" for s in VOCAB[k] if s in c[k])
            L.append(f"| {k} | {sum(c[k].values())} | {parts} |")
    L.append("")
    L.append("## For agents")
    L.append("")
    for p in data["for_agents"]:
        L.append(f"- {p}")
    L.append("")
    L.append("## Open tasks")
    L.append("")
    L.append("| Task | Status | Open to outside agents | Depends on | Tests |")
    L.append("|---|---|---|---|---|")
    for it in items:
        if it["kind"] == "task" and it["status"] != "done":
            L.append(f"| {it['id']} · {it['title']} | {it['status']} | {'yes' if it['open_for_agents'] else 'no'} | "
                     f"{', '.join(it['depends_on']) or '—'} | {', '.join(it['tests']) or '—'} |")
    L.append("")
    for a in data["areas"]:
        its = [it for it in items if it["area"] == a["name"]]
        if not its:
            continue
        L.append(f"## {a['name']}")
        L.append("")
        L.append(a["lede"])
        L.append("")
        for it in its:
            L += md_item(it, needed_by, tested_for, children, ui)
    L.append("---")
    L.append("")
    L.append(f"Generated by build_tracker.py from tracker.json at commit `{data['as_of_commit']}`.")
    return "\n".join(L) + "\n"


def md_item(it, needed_by, tested_for, children, ui):
    L = [f"### {it['id']} · {it['title']}", ""]
    agent = "yes" if it["open_for_agents"] else f"no, local only: {it['local_only_reason']}"
    L.append(f"- **Kind:** {it['kind']} · **Status:** {it['status']} · **Updated:** {it['updated']}")
    L.append(f"- **Open to outside agents:** {agent}")
    rel = [("Part of", [it["parent"]] if it.get("parent") else []), ("Parts and options", children[it["id"]]),
           ("Tests", it["tests"]), ("Depends on", it["depends_on"]), ("Needed by", needed_by[it["id"]]),
           ("Bears on", tested_for[it["id"]])]
    for name, ids in rel:
        if ids:
            L.append(f"- **{name}:** {', '.join(ids)}")
    L.append("")
    L.append("**Summary**")
    L.append("")
    L.append(it["summary"])
    L.append("")
    if it["why"]:
        L += ["**Why**", "", it["why"], ""]
    if it["evidence"]:
        L += ["**Evidence**", "", "| Claim | Value | Kind | Source |", "|---|---|---|---|"]
        for e in it["evidence"]:
            L.append("| " + " | ".join(x.replace("|", "\\|") for x in (e["claim"], e["value"], e["kind"], e["source"]))
                     + " |")
        L.append("")
    if it["assumptions"]:
        L += ["**Assumptions**", ""] + [f"- {a}" for a in it["assumptions"]] + [""]
    L += ["**Falsify**", "", it["falsify"] or ui["no_falsify"], ""]
    if it["discussion"]:
        L += ["**Discussion**", ""] + [f"- **{d['who']}:** {d['gist']} ({d['source']})" for d in it["discussion"]]
        L.append("")
    L += ["**How to help**", "", it["how_to_help"], ""]
    L += ["**Sources**", ""] + [f"- {s['doc']} · {s['section']} · `{s['commit']}`" for s in it["sources"]] + [""]
    return L


# ====================================================================== HTML
CSS = r"""
:root{
  --bg:#eceef5; --surface:#ffffff; --surface-2:#f5f6fa; --ink:#161a2c; --muted:#565d78; --line:#d2d6e4;
  --accent:#3a45a6; --accent-soft:#e3e6f7; --code:#f0f1f7;
  --dec:#0b7656; --pro:#95580a; --opn:#ad2a5a; --blk:#5f45a8;
  --f-display:"Commissioner","Inter",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-body:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --f-mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0c0f1d; --surface:#151a30; --surface-2:#1a2038; --ink:#e6e8f3; --muted:#9aa1c0; --line:#2c3356;
    --accent:#a9b2ff; --accent-soft:#232a4f; --code:#10142a;
    --dec:#4fd2a3; --pro:#f0b25a; --opn:#f47fa9; --blk:#b9a4ff;
    color-scheme:dark;
  }
}
:root[data-theme="dark"]{
    --bg:#0c0f1d; --surface:#151a30; --surface-2:#1a2038; --ink:#e6e8f3; --muted:#9aa1c0; --line:#2c3356;
    --accent:#a9b2ff; --accent-soft:#232a4f; --code:#10142a;
    --dec:#4fd2a3; --pro:#f0b25a; --opn:#f47fa9; --blk:#b9a4ff;
    color-scheme:dark;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
.wrap{max-width:1240px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 56px}
h1,h2,h3{font-family:var(--f-display);text-wrap:balance;margin:0}
p{margin:0}
code,.mono{font-family:var(--f-mono);font-size:.86em;overflow-wrap:anywhere}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.top{display:grid;gap:14px;margin-bottom:28px}
.eyebrow{font-size:.74rem;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600}
h1{font-size:clamp(2rem,5vw,3.1rem);font-weight:700;letter-spacing:-.01em;line-height:1.05}
h1 .gr{font-weight:400;color:var(--muted);font-size:.55em;letter-spacing:0;margin-left:.3em}
.lede{max-width:70ch;font-size:1.02rem}
.stamp{font-family:var(--f-mono);font-size:.76rem;color:var(--muted)}
.toc{display:flex;flex-wrap:wrap;gap:6px}
.toc a{font-size:.78rem;padding:4px 10px;border:1px solid var(--line);border-radius:999px;background:var(--surface);text-decoration:none;color:var(--ink)}
.toc a:hover{border-color:var(--accent);color:var(--accent)}
.sec{margin-top:40px;display:grid;gap:14px}
.sec>h2{font-size:clamp(1.3rem,2.6vw,1.65rem);font-weight:700}
.kicker{color:var(--muted);max-width:72ch}
.note{font-size:.82rem;color:var(--muted)}
.dl{font-size:.64rem;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-right:5px}

/* status: tone, mark shape, border style and the word */
.t-dec{--sc:var(--dec)} .t-pro{--sc:var(--pro)} .t-opn{--sc:var(--opn)} .t-blk{--sc:var(--blk)}
.mk{display:inline-block;width:12px;height:12px;border-radius:50%;border:2px solid var(--sc);flex:none;vertical-align:-1px}
.m-dec{background:var(--sc)}
.m-pro{background:linear-gradient(90deg,var(--sc) 50%,transparent 50%)}
.m-opn{background:transparent}
.m-blk{background:linear-gradient(135deg,transparent 42%,var(--sc) 42%,var(--sc) 58%,transparent 58%)}
.w{color:var(--sc)}

.stand{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:14px;align-items:start}
.stand ul{margin:0;padding-left:1.2em;display:grid;gap:7px}
.tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:9px 11px;display:grid;gap:5px}
.tile b{font-family:var(--f-display);font-size:.95rem;display:flex;justify-content:space-between;gap:8px}
.tile b span{font-family:var(--f-mono);font-size:.82rem;color:var(--muted);font-weight:500}
.sts{display:flex;flex-wrap:wrap;gap:5px 10px;font-size:.74rem;color:var(--muted)}
.sts span{display:inline-flex;align-items:center;gap:4px}
.agents{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;padding:14px 16px;display:grid;gap:8px}
.agents ul{margin:0;padding-left:1.2em;display:grid;gap:6px;font-size:.9rem}

.chip{display:inline-flex;align-items:center;gap:5px;border:1.5px solid var(--sc);border-radius:999px;padding:1px 8px 1px 5px;font-size:.74rem;background:var(--surface);color:var(--ink);text-decoration:none;line-height:1.45;max-width:100%}
.chip.t-pro{border-style:dashed}.chip.t-opn{border-style:dotted;border-width:2px}
.chip span{font-family:var(--f-mono);font-size:.92em;overflow-wrap:anywhere}
.chip em{font-style:normal;font-size:.62rem;letter-spacing:.06em;text-transform:uppercase;font-weight:600;color:var(--sc)}
a.chip:hover{border-color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:5px}

.map{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.mapc{background:var(--surface-2);border:1px solid var(--line);border-radius:8px;padding:11px 12px;display:grid;gap:8px;align-content:start}
.mapc h3{font-size:.92rem}
.mapc h3 a{color:var(--ink);text-decoration:none}
.mapc h3 a:hover{color:var(--accent)}
.frontier{display:grid;gap:6px}
.fr{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) minmax(0,1fr);gap:10px;align-items:start;padding:9px 12px;background:var(--surface);border:1.5px solid var(--sc);border-radius:6px}
.fr.t-pro{border-style:dashed}.fr.t-opn{border-style:dotted;border-width:2px}
.fr .tt{display:grid;gap:3px}
.fr .tt a{font-weight:600;color:var(--ink);text-decoration:none}
.fr .tt a:hover{color:var(--accent)}
.fr .meta{font-size:.72rem;color:var(--muted)}
.fr .meta em{font-style:normal;text-transform:uppercase;letter-spacing:.06em;font-weight:600;color:var(--sc)}
.frh{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) minmax(0,1fr);gap:10px;padding:0 12px;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}

.controls{position:sticky;top:0;z-index:2;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.controls input[type=search],.controls select{font:inherit;font-size:.84rem;padding:6px 9px;border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--ink);min-width:0}
.controls input[type=search]{flex:1 1 220px}
.controls label.ck{display:inline-flex;gap:6px;align-items:center;font-size:.82rem}
.btn{font:inherit;font-size:.82rem;padding:6px 12px;border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--ink);cursor:pointer}
.count{font-size:.8rem;color:var(--muted);font-variant-numeric:tabular-nums}

.area{display:grid;gap:8px;margin-top:26px}
.area>h2{font-size:1.25rem}
.area>.kicker{font-size:.86rem}
.it{background:var(--surface);border:1.5px solid var(--sc);border-radius:6px;min-width:0;scroll-margin-top:70px}
.it.t-pro{border-style:dashed}
.it.t-opn{border-style:dotted;border-width:2px}
.it>summary{list-style:none;cursor:pointer;display:grid;grid-template-columns:auto minmax(0,1fr) auto;column-gap:9px;row-gap:3px;align-items:center;padding:9px 12px}
.it>summary::-webkit-details-marker{display:none}
.it .iid{font-family:var(--f-mono);font-size:.8rem;color:var(--muted);margin-right:6px}
.it .nm{font-weight:600;font-size:.94rem;line-height:1.3}
.it>summary:hover .nm{color:var(--accent)}
.it .pm{font-family:var(--f-mono);color:var(--muted);width:1ch;text-align:center}
.it .pm::before{content:"+"} .it[open] .pm::before{content:"\2212"}
.it .st{grid-column:2/-1;font-size:.68rem;font-weight:600;letter-spacing:.07em;text-transform:uppercase;line-height:1.3;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.it .st .tg{color:var(--muted);letter-spacing:.02em;text-transform:none;font-weight:500;font-size:.74rem}
.ag{font-size:.64rem;letter-spacing:.05em;text-transform:uppercase;font-weight:700;padding:1px 6px;border-radius:4px;border:1px solid var(--line);color:var(--muted)}
.ag.on{color:var(--accent);border-color:var(--accent);background:var(--accent-soft)}
.dt{padding:2px 14px 14px 33px;display:grid;gap:10px;font-size:.87rem;line-height:1.55;min-width:0}
.dt ul,.dt ol{margin:0;padding-left:1.25em;display:grid;gap:4px}
.dt .fld{display:grid;gap:5px}
.dt .fld>.dl{display:block}
.dt .muted{color:var(--muted)}
.rels{display:grid;grid-template-columns:auto minmax(0,1fr);gap:6px 10px;align-items:start;font-size:.8rem}
.rels .dl{padding-top:3px}
.srcs{font-size:.76rem;color:var(--muted);border-top:1px solid var(--line);padding-top:8px;display:grid;gap:3px}
.srcs code{font-size:.92em}
pre.fx{margin:0;padding:10px 12px;background:var(--code);border-radius:6px;overflow-x:auto;font-family:var(--f-mono);font-size:.74rem;line-height:1.55;white-space:pre}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--surface);max-width:100%}
table.t{border-collapse:collapse;width:100%;min-width:480px;font-size:.78rem}
.t th,.t td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;line-height:1.45}
.t th{font-size:.68rem;color:var(--muted);font-weight:600}
.t tbody tr:last-child td{border-bottom:0}
.alede{max-width:80ch;font-size:.97rem;line-height:1.6}
.sub{font-family:var(--f-display);font-size:1.02rem;margin:22px 0 8px}
ol.rules,ol.flow{margin:0;padding-left:1.4em;display:grid;gap:7px;max-width:96ch;font-size:.88rem;line-height:1.5}
ol.rules .chips,ol.flow .chips{display:inline-flex;vertical-align:middle;margin-left:4px;gap:4px}
.arch{display:grid;gap:12px;margin-top:8px}
.lanes{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.lane{display:grid;gap:8px;align-content:start;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px;min-width:0}
.lane h4{margin:0;font-family:var(--f-display);font-size:.98rem;display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 8px}
.lane h4 .n{font-family:var(--f-mono);font-size:.72rem;color:var(--accent)}
.lane h4 small{flex-basis:100%;font-family:var(--f-body,inherit);font-size:.72rem;font-weight:400;color:var(--muted)}
.an{background:var(--surface-2);border:1px solid var(--line);border-left:3px solid var(--sc);border-radius:0 8px 8px 0;padding:7px 9px;display:grid;gap:5px;min-width:0}
.an-h{display:flex;flex-wrap:wrap;align-items:center;gap:4px 6px;color:var(--ink);text-decoration:none;font-size:.86rem;line-height:1.3}
.an-h:hover b,.an-h:focus-visible b{color:var(--accent)}
.an-h em{font-style:normal;font-size:.68rem;color:var(--muted);margin-left:auto}
.an .tag{font-family:var(--f-mono);font-size:.66rem;border:1px solid var(--line);border-radius:4px;padding:0 4px;color:var(--muted)}
.an p{font-size:.77rem;line-height:1.45;color:var(--muted)}
.an .chips{gap:4px}
.kids{display:grid;gap:6px}
.lane .kids{border-left:1px dashed var(--line);padding-left:8px}
.ov,.doors{background:var(--surface);border-radius:10px;padding:2px}
.ov .an,.doors>.an{background:var(--surface)}
.doors .kids{grid-template-columns:repeat(3,minmax(0,1fr))}
.out{font-size:.74rem;color:var(--muted);font-style:italic}
.out::before{content:"\2192\00a0";font-style:normal;color:var(--accent)}
.goalg{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.goalg .sub{margin-top:14px}
.techg{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:10px;margin-top:8px}
.tc{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:11px 12px;display:grid;gap:6px;align-content:start;min-width:0}
.tc .k{font-size:.68rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);font-weight:600}
.tc b{font-family:var(--f-display);font-size:.93rem;line-height:1.35}
.tc p{font-size:.79rem;line-height:1.5}
.tc p span{font-weight:600;color:var(--muted);margin-right:3px}
.waits{display:flex;flex-wrap:wrap;align-items:center;gap:6px;font-size:.82rem;color:var(--muted)}
footer{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);font-size:.78rem;color:var(--muted);display:grid;gap:4px}
@media (max-width:1020px){
  .map,.lanes{grid-template-columns:repeat(2,minmax(0,1fr))}
  .goalg{grid-template-columns:minmax(0,1fr)}
  .stand{grid-template-columns:minmax(0,1fr)}
}
@media (max-width:620px){
  .lanes,.doors .kids{grid-template-columns:minmax(0,1fr)}
  .out::before{content:"\2193\00a0"}
  .map,.tiles{grid-template-columns:minmax(0,1fr)}
  .fr,.frh{grid-template-columns:minmax(0,1fr)}
  .frh{display:none}
  .dt{padding:2px 12px 12px 12px}
  .rels{grid-template-columns:minmax(0,1fr)}
  .controls{position:static}
}
@media (prefers-reduced-motion: reduce){*{scroll-behavior:auto}}
"""

JS = r"""
(function(){
  var items=[].slice.call(document.querySelectorAll('details.it'));
  var text=items.map(function(e){return e.textContent.toLowerCase();});
  var q=document.getElementById('f-q'), k=document.getElementById('f-kind'), s=document.getElementById('f-status'),
      a=document.getElementById('f-area'), o=document.getElementById('f-open'), cnt=document.getElementById('f-count');
  function apply(){
    var words=q.value.toLowerCase().split(/\s+/).filter(Boolean), n=0;
    items.forEach(function(e,i){
      var ok=(!k.value||e.getAttribute('data-kind')===k.value)&&(!s.value||e.getAttribute('data-status')===s.value)&&
             (!a.value||e.getAttribute('data-area')===a.value)&&(!o.checked||e.getAttribute('data-open')==='1')&&
             words.every(function(w){return text[i].indexOf(w)>=0;});
      e.hidden=!ok; if(ok){n++;}
    });
    [].forEach.call(document.querySelectorAll('section.area'),function(sec){
      sec.hidden=!sec.querySelector('details.it:not([hidden])');
    });
    cnt.textContent=n+' of '+items.length+' items';
  }
  [q,k,s,a,o].forEach(function(el){el.addEventListener('input',apply);el.addEventListener('change',apply);});
  document.getElementById('f-reset').addEventListener('click',function(){
    q.value='';k.value='';s.value='';a.value='';o.checked=false;apply();
  });
  var ex=document.getElementById('f-expand'), open=false;
  ex.addEventListener('click',function(){
    open=!open;
    items.forEach(function(d){if(!d.hidden){d.open=open;}});
    ex.textContent=open?'Collapse all':'Expand all';
  });
  function reveal(){
    var id=decodeURIComponent(location.hash.slice(1)); if(!id){return;}
    var t=document.getElementById(id);
    if(t&&t.tagName==='DETAILS'){
      if(t.hidden){q.value='';k.value='';s.value='';a.value='';o.checked=false;apply();}
      t.open=true; t.scrollIntoView({block:'start'});
    }
  }
  window.addEventListener('hashchange',reveal);
  apply(); reveal();
})();
"""


def mark(status):
    return f'<i class="mk m-{TONE[status]}" aria-hidden="true"></i>'


def chip(by, iid, show_status=True):
    it = by[iid]
    t = TONE[it["status"]]
    st = f"<em>{esc(it['status'])}</em>" if show_status else ""
    return (f'<a class="chip t-{t}" href="#{esc(iid)}" title="{esc(it["title"])}">{mark(it["status"])}'
            f'<span>{esc(iid)}</span>{st}</a>')


def render_item(it, by, needed_by, tested_for, children, ui):
    t = TONE[it["status"]]
    agent = ('<span class="ag on">open to agents</span>' if it["open_for_agents"]
             else '<span class="ag">local only</span>')
    head = (f'<summary>{mark(it["status"])}<span><span class="iid">{esc(it["id"])}</span>'
            f'<span class="nm">{esc(it["title"])}</span></span><span class="pm" aria-hidden="true"></span>'
            f'<span class="st"><span class="w">{esc(it["status"])}</span>'
            f'<span class="tg">{esc(it["kind"])} · {esc(it["area"])}</span>{agent}</span></summary>')
    body = [f'<div class="fld"><b class="dl">Summary</b>{md_block(it["summary"])}</div>']
    if it["why"]:
        body.append(f'<div class="fld"><b class="dl">Why</b>{md_block(it["why"])}</div>')
    if it["evidence"]:
        rows = "".join(f"<tr><td>{inline(e['claim'])}</td><td>{inline(e['value'])}</td><td>{esc(e['kind'])}</td>"
                       f"<td>{inline(e['source'])}</td></tr>" for e in it["evidence"])
        body.append('<div class="fld"><b class="dl">Evidence</b><div class="tablewrap"><table class="t"><thead><tr>'
                    '<th>Claim</th><th>Value</th><th>Kind</th><th>Source</th></tr></thead>'
                    f'<tbody>{rows}</tbody></table></div></div>')
    if it["assumptions"]:
        body.append('<div class="fld"><b class="dl">Assumptions</b><ul>'
                    + "".join(f"<li>{inline(a)}</li>" for a in it["assumptions"]) + "</ul></div>")
    fz = md_block(it["falsify"]) if it["falsify"] else f'<p class="muted">{inline(ui["no_falsify"])}</p>'
    body.append(f'<div class="fld"><b class="dl">What would change it</b>{fz}</div>')
    rel = [("Part of", [it["parent"]] if it.get("parent") else []), ("Parts and options", children[it["id"]]),
           ("Tests", it["tests"]), ("Depends on", it["depends_on"]), ("Needed by", needed_by[it["id"]]),
           ("Bears on", tested_for[it["id"]])]
    rel = [(n, ids) for n, ids in rel if ids]
    if rel:
        body.append('<div class="rels">' + "".join(
            f'<b class="dl">{n}</b><div class="chips">{"".join(chip(by, i) for i in ids)}</div>' for n, ids in rel)
            + "</div>")
    if it["discussion"]:
        body.append('<div class="fld"><b class="dl">Discussion</b><ul>' + "".join(
            f"<li><b>{esc(d['who'])}:</b> {inline(d['gist'])} <span class=\"muted\">({inline(d['source'])})</span>"
            f"</li>" for d in it["discussion"]) + "</ul></div>")
    local = "" if it["open_for_agents"] else (f'<p class="muted"><b>Local only:</b> '
                                              f'{inline(it["local_only_reason"])}</p>')
    body.append(f'<div class="fld"><b class="dl">How to help</b>{md_block(it["how_to_help"])}{local}</div>')
    body.append('<div class="srcs"><b class="dl">Sources</b>' + "".join(
        f"<span>{esc(s['doc'])} · {inline(s['section'])} · <code>{esc(s['commit'])}</code></span>"
        for s in it["sources"]) + f"<span>Updated {esc(it['updated'])}</span></div>")
    return (f'<details class="it t-{t}" id="{esc(it["id"])}" data-kind="{esc(it["kind"])}" '
            f'data-status="{esc(it["status"])}" data-area="{slug(it["area"])}" '
            f'data-open="{1 if it["open_for_agents"] else 0}">{head}<div class="dt">{"".join(body)}</div></details>')


def render_html(data):
    items = data["items"]
    ui = data["ui"]
    by, needed_by, tested_for, children = relations(items)
    c = counts(items)
    o = []
    o.append("<title>Anamnesis Project Tracker</title>")
    o.append('<meta name="claude:viewport-fit-sides" content="cover">')
    o.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    o.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    o.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    o.append(FONT_LINK)
    o.append(f"<style>{CSS}</style>")
    o.append('<div class="wrap">')
    o.append('<header class="top">')
    o.append(f'<p class="eyebrow">{esc(ui["eyebrow"])}</p>')
    o.append('<h1>Anamnesis <span class="gr">project tracker</span></h1>')
    o.append(f'<p class="lede">{inline(data["about"])}</p>')
    o.append(f'<p class="stamp">as of commit {esc(data["as_of_commit"])} · built {esc(data["built_at"])} · '
             f'{len(items)} items</p>')
    o.append('<nav class="toc" aria-label="Sections"><a href="#goal">Goal</a><a href="#arch">Architecture</a>'
             '<a href="#tech">Technologies</a><a href="#stand">Where we stand</a><a href="#agents">For agents</a>'
             '<a href="#map">Project map</a><a href="#frontier">Open tasks</a><a href="#items">All items</a></nav>')
    o.append("</header>")
    o.append(goal_html(data["goal"], by))
    o.append(arch_html(data["architecture"], by))
    o.append(tech_html(data["technology"], by))

    # where we stand
    tiles = []
    for k in KINDS:
        if k not in c:
            continue
        sts = "".join(f'<span class="t-{TONE[s]}">{mark(s)}{esc(s)} {c[k][s]}</span>' for s in VOCAB[k] if s in c[k])
        tiles.append(f'<div class="tile"><b>{esc(k)}<span>{sum(c[k].values())}</span></b><div class="sts">{sts}</div>'
                     f"</div>")
    n_open = sum(1 for it in items if it["open_for_agents"])
    o.append('<section class="sec" id="stand"><h2>Where we stand</h2><div class="stand">'
             '<ul>' + "".join(f"<li>{inline(p)}</li>" for p in data["where_we_stand"]) + "</ul>"
             f'<div class="tiles">{"".join(tiles)}</div></div>'
             f'<p class="note">{n_open} of {len(items)} items are open to outside agents. {inline(ui["marks_note"])}'
             '</p></section>')

    # for agents
    col = data["colony"]
    o.append('<section class="sec" id="agents"><h2>For agents</h2><div class="agents"><ul>'
             + "".join(f"<li>{inline(p)}</li>" for p in data["for_agents"]) + "</ul>"
             f'<p class="note">Feedback: {esc(col["site"])} · {esc(col["colony"])} · post <code>{esc(col["post"])}'
             "</code></p></div></section>")

    # project map
    cards = []
    for a in data["areas"]:
        its = [it for it in items if it["area"] == a["name"]]
        if its:
            cards.append(f'<div class="mapc"><h3><a href="#area-{slug(a["name"])}">{esc(a["name"])}</a></h3>'
                         f'<div class="chips">{"".join(chip(by, it["id"], False) for it in its)}</div></div>')
    o.append(f'<section class="sec" id="map"><h2>Project map</h2><p class="kicker">{inline(ui["map_kicker"])}</p>'
             f'<div class="map">{"".join(cards)}</div></section>')

    # open tasks
    rows = []
    for it in items:
        if it["kind"] == "task" and it["status"] != "done":
            t = TONE[it["status"]]
            ag = "open to agents" if it["open_for_agents"] else "local only"
            deps = "".join(chip(by, d) for d in it["depends_on"]) or '<span class="note">none</span>'
            tests = "".join(chip(by, d) for d in it["tests"]) or '<span class="note">none</span>'
            rows.append(f'<div class="fr t-{t}"><div class="tt"><a href="#{esc(it["id"])}">{mark(it["status"])} '
                        f'{esc(it["id"])} · {esc(it["title"])}</a><span class="meta"><em>{esc(it["status"])}</em> · '
                        f'{ag}</span></div><div class="chips">{deps}</div><div class="chips">{tests}</div></div>')
    o.append(f'<section class="sec" id="frontier"><h2>Open tasks</h2><p class="kicker">{inline(ui["tasks_kicker"])}'
             '</p><div class="frontier"><div class="frh"><span>Task</span>'
             f'<span>Depends on</span><span>Tests</span></div>{"".join(rows)}</div></section>')

    # controls and items
    statuses = []
    for k in KINDS:
        for s in VOCAB[k]:
            if s not in statuses and any(it["status"] == s for it in items):
                statuses.append(s)
    o.append('<section class="sec" id="items"><h2>All items</h2>')
    o.append('<div class="controls" role="search">'
             '<input type="search" id="f-q" placeholder="Search ids and text" aria-label="Search">'
             '<select id="f-kind" aria-label="Kind"><option value="">Any kind</option>'
             + "".join(f'<option value="{k}">{k}</option>' for k in KINDS if k in c) + "</select>"
             '<select id="f-status" aria-label="Status"><option value="">Any status</option>'
             + "".join(f'<option value="{s}">{s}</option>' for s in statuses) + "</select>"
             '<select id="f-area" aria-label="Area"><option value="">Any area</option>'
             + "".join(f'<option value="{slug(a["name"])}">{esc(a["name"])}</option>' for a in data["areas"])
             + "</select>"
             '<label class="ck"><input type="checkbox" id="f-open"> open to agents</label>'
             '<button class="btn" id="f-expand" type="button">Expand all</button>'
             '<button class="btn" id="f-reset" type="button">Reset</button>'
             '<span class="count" id="f-count" aria-live="polite"></span></div>')
    for a in data["areas"]:
        its = [it for it in items if it["area"] == a["name"]]
        if not its:
            continue
        o.append(f'<section class="area" id="area-{slug(a["name"])}"><h2>{esc(a["name"])}</h2>'
                 f'<p class="kicker">{inline(a["lede"])}</p>')
        o += [render_item(it, by, needed_by, tested_for, children, ui) for it in its]
        o.append("</section>")
    o.append("</section>")
    o.append(f'<footer><p>Built by build_tracker.py from tracker.json · as of commit {esc(data["as_of_commit"])} · '
             f'built {esc(data["built_at"])}.</p><p>{inline(ui["footer_data"])}</p></footer>')
    o.append("</div>")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    o.append(f'<script type="application/json" id="tracker-data">{blob}</script>')
    o.append(f"<script>{JS}</script>")
    return "\n".join(o) + "\n"


# ====================================================================== shell
SHELL_COMMIT_META = re.compile(r'<meta name="tracker-shell-commit" content="([0-9a-f]{7,40})">')


def shell_fallback(data, commit):
    """What a reader sees with JavaScript off or the data unreachable. Baked in at build time from the data."""
    col = data["colony"]
    link = f' · <a href="{esc(col["url"])}">{esc(col["url"])}</a>' if col.get("url") else ""
    return ('<p>The full dataset is published beside this page as <a href="tracker.public.json">tracker.public.json'
            '</a>, and as plain markdown in <a href="TRACKER.md">TRACKER.md</a>.</p>'
            f'<p class="note">This page shell was built at commit <code>{esc(commit)}</code>; the data files may be '
            'newer.</p>'
            f'<p class="note">Feedback, claims and error reports: {esc(col["site"])} · {esc(col["colony"])} · post '
            f'<code>{esc(col["post"])}</code>{link}</p>')


def render_shell(data, template, commit):
    """Fill the shell template in one pass, so no filled-in value is itself expanded."""
    def js(v):
        return json.dumps(v, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c")
    values = {"CSS": CSS, "FONT_LINK": FONT_LINK, "SHELL_COMMIT": esc(commit),
              "FALLBACK": shell_fallback(data, commit), "KINDS": js(KINDS), "VOCAB": js(VOCAB), "TONE": js(TONE)}

    def fill(m):
        if m.group(1) not in values:
            raise Refused(f"shell template: unknown placeholder @@{m.group(1)}@@")
        return values[m.group(1)]
    out = re.sub(r"@@([A-Z_]+)@@", fill, template)
    if len(SHELL_COMMIT_META.findall(out)) != 1:
        raise Refused("shell template: needs exactly one tracker-shell-commit meta")
    return out


def shell_kept(path, data, template):
    """The commit of the shell.html on disk when a fresh render differs from it only in the commit stamp."""
    if not path.is_file():
        return None
    old = path.read_text(encoding="utf-8")
    m = SHELL_COMMIT_META.search(old)
    if m and render_shell(data, template, m.group(1)) == old:
        return m.group(1)
    return None


# ====================================================================== build
def git_head():
    try:
        r = subprocess.run(["git", "-C", str(DOCS), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                           timeout=20, check=True)
    except (OSError, subprocess.SubprocessError) as e:
        raise Refused(f"cannot read the git commit ({e.__class__.__name__}); pass --commit") from None
    return r.stdout.strip()


def build(data_path, out_dir, commit=None, shell_template=SHELL_TEMPLATE):
    deny = load_deny()
    if not Path(shell_template).is_file():
        raise Refused(f"shell template missing: {shell_template}")
    template = Path(shell_template).read_text(encoding="utf-8")
    raw = Path(data_path).read_text(encoding="utf-8")
    hits = []
    for m in BAD_CHARS.finditer(raw):
        hits.append(f"tracker.json (raw bytes): forbidden character U+{ord(m.group()):04X} at offset {m.start()}")
    data = json.loads(raw)
    validate(data)
    data["as_of_commit"] = commit or git_head()
    data["built_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for path, s in walk_strings(data):
        scan_text(f"tracker.json {path}", s, deny, hits)
    digest_text = (DOCS / DIGEST).read_text(encoding="utf-8")
    all_text = "\n".join(s for _, s in walk_strings(data))
    hits += quote_hits(all_text, digest_text)
    if hits:
        raise Refused("sanitizer refused the data:\n  " + "\n  ".join(hits[:60]))

    stamped = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    md = render_md(data)
    page = render_html(data)
    shell = render_shell(data, template, data["as_of_commit"])
    scan_text("TRACKER.md", md, deny, hits)
    for path, s in walk_strings(json.loads(stamped)):
        scan_text(f"tracker.public.json {path}", s, deny, hits)
    scan_html(page, deny, hits)
    scan_shell(shell, data, deny, hits)
    m = re.search(r'<script type="application/json" id="tracker-data">(.*?)</script>', page, re.S)
    if not m or json.loads(m.group(1)) != data:
        hits.append("tracker.html: embedded dataset does not round-trip")
    if hits:
        raise Refused("sanitizer refused the rendered output:\n  " + "\n  ".join(hits[:60]))

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    kept = shell_kept(out_dir / "shell.html", data, template)
    tmp = Path(tempfile.mkdtemp(prefix=".build-", dir=out_dir))
    try:
        files = {"tracker.html": page, "TRACKER.md": md, "tracker.public.json": stamped}
        if kept is None:
            files["shell.html"] = shell
        for name, text in files.items():
            (tmp / name).write_text(text, encoding="utf-8")
        tmp_data = tmp / "tracker.json"
        tmp_data.write_text(stamped, encoding="utf-8")
        for name in files:
            os.replace(tmp / name, out_dir / name)
        os.replace(tmp_data, Path(data_path))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sizes = {n: len(t.encode()) for n, t in files.items()}
    shell_state = {"changed": kept is None, "commit": data["as_of_commit"] if kept is None else kept,
                   "bytes": len(shell.encode()) if kept is None else (out_dir / "shell.html").stat().st_size}
    return data, sizes, shell_state


# ====================================================================== self-test
def quote_probe(deny):
    """Five words of a quoted line from the private notes that no deny term catches and the digest lacks."""
    dw = " " + " ".join(words((DOCS / DIGEST).read_text(encoding="utf-8"))) + " "
    for q in sorted(owner_quotes()):
        w = words(q)
        for i in range(len(w) - 4):
            run = " ".join(w[i:i + 5])
            if f" {run} " not in dw and not any(rx.search(run) for _, rx in deny):
                return run
    return None


def self_test():
    deny = load_deny()
    plain = next((t for t, _ in deny if re.fullmatch(r"[A-Za-z][A-Za-z ]+", t)), None)
    if plain is None:
        raise Refused("self-test: no plain term in the deny list to plant")
    base = json.loads((HERE / "tracker.json").read_text(encoding="utf-8"))
    zwsp = chr(0x200B)
    cases = []

    def variant(name, mutate, expect_ok, raw_edit=None, shell_edit=None):
        d = json.loads(json.dumps(base))
        mutate(d)
        cases.append((name, d, expect_ok, raw_edit, shell_edit))

    def plant(text):
        def f(d):
            d["items"][0]["summary"] += " " + text
        return f

    variant("clean control", lambda d: None, True)
    variant("deny term planted", plant(plain), False)
    variant("U+200B planted", plant("split" + zwsp + "word"), False)
    escaped = "".join(f"\\u{ord(ch):04x}" for ch in plain)
    variant("deny term planted as JSON escapes", plant("@@ESCAPED@@"), False,
            raw_edit=lambda s: s.replace("@@ESCAPED@@", escaped))
    variant("U+200B planted as a JSON escape", plant("@@ZW@@"), False,
            raw_edit=lambda s: s.replace("@@ZW@@", "split\\u200bword"))
    variant("deny term planted in a key", lambda d: d["items"][0].__setitem__(plain, "x"), False)
    run5 = quote_probe(deny)
    if run5 is None:
        raise Refused("self-test: no five-word run of a quoted line is free of deny terms and absent from the digest")
    variant("five words of a quoted line planted", plant(run5), False)
    # The shell template is published as the page, so a deny term written into it must stop the build too. Planted
    # as visible text after the stylesheet, which is the part the page scan covers.
    variant("deny term planted in the shell template", lambda d: None, False,
            shell_edit=lambda t: t + f"<p>{plain}</p>\n")
    variant("item title planted in the shell template", lambda d: None, False,
            shell_edit=lambda t: t + f"<p>{base['items'][0]['title']}</p>\n")
    # A box pointing at an id that does not exist would make the shell throw and blank the public page.
    variant("unknown id in an architecture box", lambda d: d["architecture"]["lanes"][0]["nodes"][0]["items"]
            .append("ZZ.nonexistent"), False)
    variant("unknown id in a technology row", lambda d: d["technology"]["rows"][0]["items"].append("ZZ.nonexistent"),
            False)
    variant("deny term planted in the architecture", lambda d: d["architecture"].__setitem__(
        "lede", d["architecture"]["lede"] + " " + plain), False)
    template = SHELL_TEMPLATE.read_text(encoding="utf-8")
    ok = True
    with tempfile.TemporaryDirectory(prefix="tracker-selftest-") as td:
        for i, (name, d, expect_ok, raw_edit, shell_edit) in enumerate(cases):
            case = Path(td) / f"case{i}"
            out = case / "out"
            case.mkdir()
            dp = case / "tracker.json"
            s = json.dumps(d, ensure_ascii=False, indent=1)
            if raw_edit:
                s = raw_edit(s)
            dp.write_text(s, encoding="utf-8")
            before = dp.read_bytes()
            sp = case / "shell_template.html"
            sp.write_text(shell_edit(template) if shell_edit else template, encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "--data", str(dp), "--out",
                                str(out), "--commit", "0000000", "--shell-template", str(sp)],
                               capture_output=True, text=True, timeout=120, check=False)
            written = sorted(p.name for p in out.iterdir()) if out.exists() else []
            if expect_ok:
                good = r.returncode == 0 and set(written) >= {"tracker.html", "TRACKER.md", "tracker.public.json",
                                                              "shell.html"}
            else:
                good = r.returncode != 0 and not written and dp.read_bytes() == before
            ok &= good
            first = (r.stderr.strip().splitlines() or [""])
            detail = first[1].strip() if len(first) > 1 else first[0]
            print(f"  {'PASS' if good else 'FAIL'}  {name}: exit {r.returncode}, files written {len(written)}"
                  + ("" if expect_ok else f", refused with: {detail}"))
    print("self-test", "passed" if ok else "FAILED")
    return ok


# ====================================================================== novel text
def norm(s):
    s = s.replace("**", "").replace("`", "").replace("’", "'")
    s = re.sub(r"(?<!\w)\*|\*(?!\w)", "", s)
    s = s.replace("\\|", "|")
    return re.sub(r"\s+", " ", s).strip().lower()


def novel(data_path):
    """Class A: in no public source. Class B: verbatim only in the panel or test notes (not the digest)."""
    digest = norm((DOCS / DIGEST).read_text(encoding="utf-8"))
    notes = " ".join(norm((DOCS / f).read_text(encoding="utf-8")) for f in PUBLIC_SOURCES if f != DIGEST)
    data = json.loads(Path(data_path).read_text(encoding="utf-8"))
    found = {"A": {}, "B": {}}

    def check(where, text):
        for sent in re.split(r"(?<=[.!?;])\s+|\n+", text):
            n = norm(sent).rstrip(".;:!?")
            if not n or not re.search(r"[a-z]", n):
                continue
            if n in digest:
                continue
            cls = "B" if n in notes else "A"
            found[cls].setdefault(sent.strip(), []).append(where)

    for f in ("title", "about"):
        check(f, data[f])
    for k, v in data["ui"].items():
        check(f"ui.{k}", v)
    for i, p in enumerate(data["where_we_stand"]):
        check(f"where_we_stand[{i}]", p)
    for i, p in enumerate(data["for_agents"]):
        check(f"for_agents[{i}]", p)
    for a in data["areas"]:
        check(f"area {a['name']}", a["name"])
        check(f"area {a['name']}", a["lede"])
    for path, v in [x for k in ("goal", "architecture", "technology") for x in walk_strings(data[k], k)]:
        if not re.search(r"(\.<key>|\.items\[\d+\])$", path):
            check(path, v)
    for it in data["items"]:
        iid = it["id"]
        for f in ("title", "summary", "why", "falsify", "how_to_help", "local_only_reason"):
            if it.get(f):
                check(f"{iid}.{f}", it[f])
        for j, a in enumerate(it["assumptions"]):
            check(f"{iid}.assumptions", a)
        for e in it["evidence"]:
            check(f"{iid}.evidence.claim", e["claim"])
            check(f"{iid}.evidence.value", e["value"])
            check(f"{iid}.evidence.source", e["source"])
        for d in it["discussion"]:
            check(f"{iid}.discussion.who", d["who"])
            check(f"{iid}.discussion", d["gist"])
            check(f"{iid}.discussion.source", d["source"])
        for s in it["sources"]:
            # "<digest heading>. Its own sources: <the box's source line>": the joining phrase is fixed, the parts are
            # checked on their own
            for part in s["section"].split(". Its own sources: "):
                check(f"{iid}.sources.section", part)
    heads = {"A": "A. Not found verbatim in any public source (written for the tracker)",
             "B": "B. Verbatim from the panel or test notes, not in the digest (unsanitized sources)"}
    for cls in ("A", "B"):
        print(f"## {heads[cls]}: {len(found[cls])}")
        for sent, where in found[cls].items():
            uniq = sorted(set(where))
            shown = ", ".join(uniq[:6]) + (f" and {len(uniq) - 6} more" if len(uniq) > 6 else "")
            print(f"- [{shown}] {sent}")
    print(f"{len(found['A'])} in class A, {len(found['B'])} in class B; everything else is verbatim from the digest")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(HERE / "tracker.json"))
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--commit")
    ap.add_argument("--shell-template", default=str(SHELL_TEMPLATE))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--novel", action="store_true")
    a = ap.parse_args()
    try:
        if a.self_test:
            sys.exit(0 if self_test() else 1)
        if a.novel:
            novel(a.data)
            return
        data, sizes, shell = build(a.data, a.out, a.commit, a.shell_template)
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(2)
    n = len(data["items"])
    print(f"ok: {n} items, as of {data['as_of_commit']}, built {data['built_at']}")
    for name, size in sizes.items():
        if name != "shell.html":
            print(f"  {name}: {size:,} bytes")
    if shell["changed"]:
        print(f"  shell.html: {shell['bytes']:,} bytes, rewritten at commit {shell['commit']} "
              "(its content changed: republish the page too)")
    else:
        print(f"  shell.html: {shell['bytes']:,} bytes, unchanged since commit {shell['commit']} (not rewritten)")


if __name__ == "__main__":
    main()
