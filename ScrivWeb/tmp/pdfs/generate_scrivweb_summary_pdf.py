from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import inch

ROOT = Path(r"C:\Users\rkiss\OneDrive\Documents\GitHub\autononymous.github.io\ScrivWeb")
out_pdf = ROOT / "output" / "pdf" / "scrivweb_app_summary.pdf"
out_pdf.parent.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=21,
    textColor=colors.HexColor("#1f2937"),
    spaceAfter=8,
)

style_h = ParagraphStyle(
    "HeadingCustom",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11.5,
    leading=13,
    textColor=colors.HexColor("#111827"),
    spaceBefore=4,
    spaceAfter=3,
)

style_body = ParagraphStyle(
    "BodyCustom",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.4,
    leading=11.6,
    textColor=colors.HexColor("#111827"),
    spaceAfter=2,
)

style_bullet = ParagraphStyle(
    "BulletCustom",
    parent=style_body,
    leftIndent=12,
    firstLineIndent=0,
    spaceBefore=0,
    spaceAfter=1.5,
)

style_number = ParagraphStyle(
    "NumberCustom",
    parent=style_body,
    leftIndent=14,
    firstLineIndent=-10,
    spaceBefore=0,
    spaceAfter=1.5,
)

what_it_is = (
    "ScrivWeb (titled <b>Scriv2WN</b> in <code>index.html</code>) is a static web reader for serialized fiction, "
    "with story-specific theming, chapter navigation, and extras. "
    "It renders chapter JSON and style config from local repo data files directly in the browser."
)

who_for = (
    "Primary persona: online readers of the Firebrand/Paragate stories, with additional mode flags for reviewer/editor/author workflows."
)

features = [
    "URL-driven loading of story, mode, and chapter via query params (<code>?story=...&mode=...&chapter=...</code>).",
    "On-demand chapter fetch + in-session caching from <code>data/sectioned/&lt;story&gt;/&lt;act&gt;/&lt;chapter&gt;.json</code>.",
    "TOC panel with release-aware chapter gating/locks by access level (Reader, Reviewer, Special, Author).",
    "Scroll-driven theme interpolation (POV-aware colors/backgrounds) using CSS custom properties.",
    "Reader controls for font size, line height, justification, image headers, and datetime headers.",
    "Extras system that loads announcements JSON and story-specific extras HTML into side panels.",
    "Local persistence of chapter position and reader preferences in per-story <code>localStorage</code> keys.",
]

architecture = [
    "Client app: <code>index.html</code> + <code>main.js</code> (compiled from <code>main.ts</code>) manage rendering, theming, navigation, and UI state.",
    "Core runtime components in <code>main.ts</code>: <code>LocalStorageAndSrcVars</code>, <code>StoryConfig</code>, <code>TableOfContents</code>, <code>ChapterBinder</code>, <code>ThemeDriver</code>, and <code>StoryExtrasWindow</code>.",
    "Primary data flow: browser fetches <code>data/StoryConfig.json</code> -> <code>data/TOC/TOC_*.json</code> -> section files under <code>data/sectioned/</code>; extras come from <code>data/Announcements.json</code> and <code>extra/extras_*.html</code>.",
    "Supporting pipeline: <code>scripts/python/Scriv2WebNovel.py</code> generates <code>data/output</code>, <code>data/sectioned</code>, <code>data/TOC</code>, GPT exports, and PDF HTML/PDF build artifacts.",
    "Backend/API service for live processing: <b>Not found in repo.</b>",
]

run_steps = [
    "Serve the repo root over local HTTP (the app uses <code>fetch()</code> for JSON/HTML assets). Exact server command: <b>Not found in repo.</b>",
    "Open <code>index.html</code> in that server context (example path: <code>/index.html?story=Paragate</code>).",
    "Optional URL params: <code>story</code>, <code>chapter</code>, and <code>mode</code> (reader/reviewer/editor/author aliases are parsed in <code>main.ts</code>).",
    "If editing TypeScript, recompile <code>main.ts</code> to <code>main.js</code>; exact compile command/tooling bootstrap: <b>Not found in repo.</b>",
]

story = []
story.append(Paragraph("ScrivWeb App Summary", style_title))

story.append(Paragraph("What it is", style_h))
story.append(Paragraph(what_it_is, style_body))

story.append(Paragraph("Who it's for", style_h))
story.append(Paragraph(who_for, style_body))

story.append(Paragraph("What it does", style_h))
feature_items = [ListItem(Paragraph(item, style_bullet), leftIndent=0) for item in features]
story.append(ListFlowable(feature_items, bulletType="bullet", leftIndent=12, bulletFontName="Helvetica", bulletFontSize=8.5, bulletOffsetY=1))

story.append(Spacer(1, 2))
story.append(Paragraph("How it works (repo evidence)", style_h))
arch_items = [ListItem(Paragraph(item, style_bullet), leftIndent=0) for item in architecture]
story.append(ListFlowable(arch_items, bulletType="bullet", leftIndent=12, bulletFontName="Helvetica", bulletFontSize=8.5, bulletOffsetY=1))

story.append(Spacer(1, 2))
story.append(Paragraph("How to run (minimal)", style_h))
for i, item in enumerate(run_steps, start=1):
    story.append(Paragraph(f"{i}. {item}", style_number))

story.append(Spacer(1, 3))
story.append(Paragraph("Evidence scope: repository files only (no external assumptions).", ParagraphStyle(
    "Foot",
    parent=style_body,
    fontSize=8.3,
    leading=10,
    textColor=colors.HexColor("#4b5563")
)))

doc = SimpleDocTemplate(
    str(out_pdf),
    pagesize=letter,
    leftMargin=0.58 * inch,
    rightMargin=0.58 * inch,
    topMargin=0.52 * inch,
    bottomMargin=0.52 * inch,
)

doc.build(story)
print(str(out_pdf))
