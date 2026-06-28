#!/usr/bin/env python3
"""
Generate styled PDFs for Meridian Hackathon documents.
Outputs to ./docs/pdfs/
"""

import os
import re
import subprocess
import sys
import shutil
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("docs/pdfs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]

# ── Style ──────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --border: #2e3250;
  --accent: #6c63ff;
  --accent2: #00d4ff;
  --text: #e8eaf6;
  --muted: #8b90b0;
  --code-bg: #12141e;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 13px;
  line-height: 1.75;
  padding: 40px 48px;
  max-width: 960px;
  margin: 0 auto;
}

.doc-header {
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
  border: 1px solid #4338ca;
  border-radius: 12px;
  padding: 28px 32px;
  margin-bottom: 36px;
  display: flex;
  align-items: center;
  gap: 20px;
}
.doc-header .logo {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(90deg, #6c63ff, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}
.doc-header .subtitle {
  font-size: 12px;
  color: #a5b4fc;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.doc-header .badge {
  margin-left: auto;
  background: rgba(99,102,241,0.2);
  border: 1px solid #6366f1;
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 11px;
  color: #a5b4fc;
  white-space: nowrap;
  font-weight: 600;
}
.badge-p1 { background: rgba(108,99,255,0.2); border-color: #6c63ff; color: #a5b4fc; }
.badge-p2 { background: rgba(0,212,255,0.2); border-color: #00d4ff; color: #67e8f9; }
.badge-p3 { background: rgba(0,229,160,0.2); border-color: #00e5a0; color: #6ee7b7; }

h1 {
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(90deg, #c7d2fe, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
h2 {
  font-size: 17px;
  font-weight: 600;
  color: #a5b4fc;
  margin-top: 32px;
  margin-bottom: 12px;
  padding-left: 12px;
  border-left: 3px solid var(--accent);
}
h3 {
  font-size: 14px;
  font-weight: 600;
  color: #c7d2fe;
  margin-top: 20px;
  margin-bottom: 8px;
}
h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
  margin-top: 16px;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

p { margin-bottom: 10px; }
a { color: var(--accent2); text-decoration: none; }
strong { color: #c7d2fe; font-weight: 600; }
em { color: #ffb547; font-style: normal; font-weight: 500; }

ul, ol { padding-left: 20px; margin-bottom: 12px; }
li { margin-bottom: 4px; }
li::marker { color: var(--accent); }

code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11.5px;
  background: var(--code-bg);
  color: #a5f3fc;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #1e3a5f;
}
pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  padding: 16px 18px;
  overflow-x: auto;
  margin: 14px 0;
}
pre code {
  background: none;
  border: none;
  padding: 0;
  color: #e2e8f0;
  font-size: 11px;
  line-height: 1.65;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 12px;
}
thead tr {
  background: linear-gradient(90deg, rgba(99,102,241,0.3), rgba(0,212,255,0.1));
  border-bottom: 1px solid var(--accent);
}
th {
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: #c7d2fe;
  letter-spacing: 0.04em;
}
td {
  padding: 8px 14px;
  border-bottom: 1px solid var(--border);
}
tr:nth-child(even) td { background: rgba(255,255,255,0.02); }

hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 28px 0;
}
blockquote {
  background: rgba(108,99,255,0.1);
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
  padding: 10px 16px;
  margin: 14px 0;
  color: var(--muted);
}

.doc-footer {
  margin-top: 48px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--muted);
}

@media print {
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
"""


# ── Markdown → HTML ────────────────────────────────────────────────────────────
def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(text):
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{escape(m.group(1))}</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text

def md_to_html(text):
    lines = text.split("\n")
    out = []
    in_code = False
    in_table = False
    in_list = False
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code fence
        if line.startswith("```"):
            if not in_code:
                lang = line[3:].strip()
                attr = f' class="language-{lang}"' if lang else ""
                out.append(f"<pre><code{attr}>")
                in_code = True
            else:
                out.append("</code></pre>")
                in_code = False
            i += 1
            continue

        if in_code:
            out.append(escape(line))
            i += 1
            continue

        # HR
        if re.match(r"^[-*]{3,}$", line.strip()):
            if in_list: out.append("</ul>"); in_list = False
            if in_table: out.append("</tbody></table>"); in_table = False
            out.append("<hr>")
            i += 1
            continue

        # Headings
        hm = re.match(r"^(#{1,4})\s+(.+)$", line)
        if hm:
            if in_list: out.append("</ul>"); in_list = False
            if in_table: out.append("</tbody></table>"); in_table = False
            lvl = len(hm.group(1))
            out.append(f"<h{lvl}>{inline(hm.group(2))}</h{lvl}>")
            i += 1
            continue

        # Table header
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|[-| :]+\|$", lines[i+1].strip()):
            if in_list: out.append("</ul>"); in_list = False
            if in_table: out.append("</tbody></table>"); in_table = False
            headers = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append("<table><thead><tr>")
            for h in headers:
                out.append(f"<th>{inline(h)}</th>")
            out.append("</tr></thead><tbody>")
            in_table = True
            i += 2
            continue

        # Table row
        if in_table and "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append("<tr>")
            for c in cells:
                out.append(f"<td>{inline(c)}</td>")
            out.append("</tr>")
            i += 1
            continue
        elif in_table:
            out.append("</tbody></table>")
            in_table = False

        # List items
        lm = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.+)$", line)
        if lm:
            content = inline(lm.group(3))
            if content.startswith("[ ]"):
                content = "☐" + content[3:]
            elif re.match(r"^\[x\]", content, re.I):
                content = "☑" + content[3:]
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{content}</li>")
            i += 1
            continue
        elif in_list:
            out.append("</ul>")
            in_list = False

        # Blockquote
        if line.startswith(">"):
            out.append(f"<blockquote>{inline(line[1:].strip())}</blockquote>")
            i += 1
            continue

        # Blank
        if not line.strip():
            out.append("")
            i += 1
            continue

        # Paragraph
        out.append(f"<p>{inline(line)}</p>")
        i += 1

    if in_list: out.append("</ul>")
    if in_table: out.append("</tbody></table>")
    if in_code: out.append("</code></pre>")

    return "\n".join(out)


def build_html(title, subtitle, badge, badge_class, body_html):
    badge_html = f'<div class="badge {badge_class}">{badge}</div>' if badge else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title} — Meridian</title>
<style>{CSS}</style>
</head>
<body>
<div class="doc-header">
  <div>
    <div class="logo">⬡ Meridian</div>
    <div class="subtitle">{subtitle}</div>
  </div>
  {badge_html}
</div>
{body_html}
<div class="doc-footer">
  <span>Meridian — Intelligent Next-Best Action Platform</span>
  <span>XLV Hackathon · 2026</span>
</div>
</body>
</html>"""


# ── Chrome headless PDF ────────────────────────────────────────────────────────
def find_chrome():
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    for cmd in ["google-chrome", "chromium"]:
        r = subprocess.run(["which", cmd], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout.strip()
    return None

def html_to_pdf(html_path, pdf_path, chrome):
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-software-rasterizer",
        f"--print-to-pdf={pdf_path.absolute()}",
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        str(html_path.absolute()),
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return pdf_path.exists()


# ── Documents ──────────────────────────────────────────────────────────────────
DOCS = [
    {
        "src": "docs/demo_script.md",
        "title": "Demo Script",
        "subtitle": "5-Minute Video Walkthrough",
        "badge": "DEMO · 5 MIN",
        "badge_class": "badge-p3",
        "output": "01_Demo_Script.pdf",
    },
    {
        "src": "docs/ARCHITECTURE.md",
        "title": "System Architecture",
        "subtitle": "Technical Architecture Walkthrough",
        "badge": "ARCHITECTURE",
        "badge_class": "",
        "output": "02_Architecture.pdf",
    },
    {
        "src": "P1_AI_Agents_Lead.md",
        "title": "P1 — AI / Agents Lead",
        "subtitle": "Role Guide & Implementation Spec",
        "badge": "P1 · AI & AGENTS",
        "badge_class": "badge-p1",
        "output": "03_P1_AI_Agents_Lead.pdf",
    },
    {
        "src": "P2_Data_Memory_Lead.md",
        "title": "P2 — Data / Memory Lead",
        "subtitle": "Role Guide & Implementation Spec",
        "badge": "P2 · DATA & MEMORY",
        "badge_class": "badge-p2",
        "output": "04_P2_Data_Memory_Lead.pdf",
    },
    {
        "src": "P3_Frontend_Demo_Lead.md",
        "title": "P3 — Frontend / Demo Lead",
        "subtitle": "Role Guide & Implementation Spec",
        "badge": "P3 · FRONTEND & DEMO",
        "badge_class": "badge-p3",
        "output": "05_P3_Frontend_Demo_Lead.pdf",
    },
]


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    chrome = find_chrome()
    if not chrome:
        print("⚠️  Chrome not found — will produce HTML files instead of PDF.")
        print("   To get PDFs, install Google Chrome and re-run.\n")

    tmp_dir = OUTPUT_DIR / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    generated = []

    for doc in DOCS:
        src = Path(doc["src"])
        if not src.exists():
            print(f"⚠️  Skipping {doc['src']} — not found")
            continue

        print(f"📄  {doc['title']} ...", end=" ", flush=True)
        md_text = src.read_text(encoding="utf-8")
        body = md_to_html(md_text)
        full_html = build_html(
            title=doc["title"],
            subtitle=doc["subtitle"],
            badge=doc["badge"],
            badge_class=doc["badge_class"],
            body_html=body,
        )

        html_path = tmp_dir / (doc["output"].replace(".pdf", ".html"))
        html_path.write_text(full_html, encoding="utf-8")

        if chrome:
            pdf_path = OUTPUT_DIR / doc["output"]
            ok = html_to_pdf(html_path, pdf_path, chrome)
            if ok:
                kb = pdf_path.stat().st_size // 1024
                print(f"✅  {pdf_path} ({kb} KB)")
                generated.append(str(pdf_path))
            else:
                # fall back to HTML
                final = OUTPUT_DIR / doc["output"].replace(".pdf", ".html")
                shutil.copy(html_path, final)
                print(f"⚠️  PDF failed — saved HTML: {final}")
                generated.append(str(final))
        else:
            final = OUTPUT_DIR / doc["output"].replace(".pdf", ".html")
            shutil.copy(html_path, final)
            print(f"📋  Saved HTML: {final}")
            generated.append(str(final))

    shutil.rmtree(tmp_dir, ignore_errors=True)

    print()
    print("─" * 54)
    print(f"✨  Done! {len(generated)} file(s) in: {OUTPUT_DIR.absolute()}")
    for f in generated:
        print(f"    • {f}")


if __name__ == "__main__":
    main()
