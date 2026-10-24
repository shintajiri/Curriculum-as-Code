#!/usr/bin/env python3
"""Generate derived documents from a Curriculum-as-Code YAML file.

Outputs (into OUT_DIR)
  syllabus/<course id>.md   the DP-related section of each syllabus: goals, DP correspondence, assessments
  curriculum_map.html       courses x DP matrix with level words (self-contained HTML)
  curriculum_map.csv        the same matrix as CSV (UTF-8 with BOM, opens cleanly in Excel)

Every output is stamped with the programme version and generation time, so a reader can tell which
source it came from. Do not edit the outputs; edit the YAML and regenerate.

Usage : python3 tools/generate.py curriculum.yaml out/
"""
import csv, datetime, html, os, sys

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def dp_name(v):
    return v["name"] if isinstance(v, dict) else str(v)


def write_syllabus(course, dp_defs, stamp, out_dir):
    cid = course["id"]
    lines = [f"# {course['name']}（{cid}）", "", f"<!-- generated from curriculum source {stamp}. Do not edit; edit the YAML. -->", ""]
    meta = [f"{k}: {course[k]}" for k in ("year", "term", "credits") if k in course]
    if meta:
        lines += ["、".join(meta), ""]
    lines += ["## 到達目標", ""]
    for g, text in course["goals"].items():
        lines.append(f"- **{g}** {text}")
    lines += ["", "## ディプロマ・ポリシーとの対応", "", "| DP | 名称 | 水準 |", "|---|---|---|"]
    for dp, level in course["dp"].items():
        lines.append(f"| {dp} | {dp_name(dp_defs.get(dp, '?'))} | {level} |")
    lines += ["", "## 評価方法", "", "| 方法 | 配分 | 対応する到達目標 |", "|---|---:|---|"]
    for a in course["assessments"]:
        lines.append(f"| {a['method']} | {a['weight']:g}% | {', '.join(a['goals'])} |")
    lines.append("")
    path = os.path.join(out_dir, "syllabus", f"{cid}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def write_map(courses, dp_defs, stamp, out_dir, prog_name):
    dps = list(dp_defs.keys())
    # CSV (UTF-8 with BOM)
    csv_path = os.path.join(out_dir, "curriculum_map.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "year"] + [f"{d} {dp_name(dp_defs[d])}" for d in dps])
        for c in courses:
            w.writerow([c["id"], c["name"], c.get("year", "")] + [c["dp"].get(d, "") for d in dps])
    # HTML
    th = "".join(f"<th title=\"{html.escape(dp_name(dp_defs[d]))}\">{d}<br><small>{html.escape(dp_name(dp_defs[d]))}</small></th>" for d in dps)
    rows = []
    for c in courses:
        cells = "".join(f"<td class=\"lv {html.escape(str(c['dp'].get(d, '')))}\">{html.escape(str(c['dp'].get(d, '')))}</td>" for d in dps)
        rows.append(f"<tr><td>{html.escape(c['id'])}</td><td>{html.escape(c['name'])}</td><td>{c.get('year', '')}</td>{cells}</tr>")
    doc = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>カリキュラムマップ {html.escape(prog_name)}</title>
<style>
body{{font-family:system-ui,sans-serif;margin:24px;color:#1a1a1a}} table{{border-collapse:collapse}}
th,td{{border:1px solid #bbb;padding:6px 10px;text-align:center}} td:nth-child(2){{text-align:left}}
th{{background:#0d2b5e;color:#fff;font-weight:600}} th small{{display:block;font-weight:400;font-size:11px;max-width:12em}}
.lv:empty{{background:#fff}} .lv{{background:#eef3fb}} .lv.発展{{background:#0d2b5e;color:#fff}} .lv.展開{{background:#9fb3d9}}
.stamp{{color:#666;font-size:12px;margin-top:12px}}
</style></head><body>
<h1>カリキュラムマップ：{html.escape(prog_name)}</h1>
<table><thead><tr><th>科目ID</th><th>科目名</th><th>年次</th>{th}</tr></thead><tbody>{''.join(rows)}</tbody></table>
<p class="stamp">generated from curriculum source {html.escape(stamp)}. 生成物は編集しない。正本（YAML）を直して生成し直す。</p>
</body></html>"""
    html_path = os.path.join(out_dir, "curriculum_map.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return csv_path, html_path


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    src, out_dir = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    prog = doc.get("programme") or {}
    stamp = f"version {prog.get('version', '?')} at {datetime.datetime.now().isoformat(timespec='minutes')}"
    dp_defs = doc["dp_definitions"]
    courses = doc["courses"]
    os.makedirs(out_dir, exist_ok=True)
    made = [write_syllabus(c, dp_defs, stamp, out_dir) for c in courses]
    made += list(write_map(courses, dp_defs, stamp, out_dir, prog.get("name", "")))
    for p in made:
        print("wrote", p)


if __name__ == "__main__":
    main()
