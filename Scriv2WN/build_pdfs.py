import sys
import asyncio
import threading
from pathlib import Path
from typing import Optional, List

from playwright.async_api import async_playwright


_DEFAULT_PRINT_CSS = r"""
/* =========================================================
   Scriv2WN – Raw Chapter Print Stylesheet (print-first)
   Targets:
   div.HeaderParagate, div.HeaderFirebrand
   h1.PDF_CTitle, h2.PDF_CSub, h3.PDF_Snum
   div.SceneCody, div.SceneKatiya, div.SceneTitus
   p.BodyCody, p.BodyKatiya, p.BodyTitus
   (Also styles div.StoryHeader because it exists in the raw HTML)
   ========================================================= */

:root{
  /* Print palette (kept subtle so it doesn't look like a rave in PDFs) */
  --paper: #ffffff;
  --ink: #111111;
  --muted: #5f6368;
  --faint: #9aa0a6;
  --rule: #d8dadd;

  /* POV accents (used sparingly: small rules, scene badges) */
  --cody:   #2a6df4; /* cool/modern */
  --katiya: #b07a1f; /* brass/warrior */
  --titus:  #a61b2b; /* ember */

  /* Layout */
  --page-margin-y: 18mm;
  --page-margin-x: 16mm;
  --measure: 66ch;          /* readable line length */
  --leading: 1.48;          /* line height */
  --para-gap: 0.85em;
  --para-indent: 1.5em;

  /* Type */
  --font-body: ui-serif, "Iowan Old Style", "Palatino Linotype", Palatino, "Georgia", serif;
  --font-head: ui-serif, "Iowan Old Style", "Palatino Linotype", Palatino, "Georgia", serif;
}

/* ---------- Hard reset (gentle) ---------- */
html, body { margin: 0; padding: 0; }
img { max-width: 100%; height: auto; }
* { box-sizing: border-box; }
p { margin: 0; }
em { font-style: italic; }

/* ---------- PRINT ---------- */
@media print {
  @page {
    margin: var(--page-margin-y) var(--page-margin-x);
  }

  body{
    background: var(--paper);
    color: var(--ink);
    font-family: var(--font-body);
    font-size: 11.25pt;
    line-height: var(--leading);
    text-rendering: geometricPrecision;
    -webkit-font-smoothing: antialiased;
    font-kerning: normal;
  }

  /* Keep the text column readable even on letter-sized pages */
  body > *{
    max-width: var(--measure);
    margin-left: auto;
    margin-right: auto;
  }

  /* Prevent lonely lines */
  p{ orphans: 3; widows: 3; }

  /* ===== Story header (logos) ===== */
  div.StoryHeader{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 14mm;
    margin: 0 0 8mm 0;
    padding: 0 0 6mm 0;
    border-bottom: 1px solid var(--rule);
  }
  div.StoryHeader img{
    height: 14mm;
    width: auto;
    object-fit: contain;
    /* Your images are the "inv" versions in the sample,
       so invert them back for print readability on white paper. */
    filter: invert(1);
  }

  /* ===== Chapter header blocks ===== */
  div.HeaderParagate,
  div.HeaderFirebrand{
    text-align: center;
    margin: 10mm auto 8mm auto;
    padding: 0 0 6mm 0;
    border-bottom: 1px solid var(--rule);
    break-before: page; /* each chapter starts clean */
  }

  h1.PDF_CTitle{
    font-family: var(--font-head);
    font-size: 18pt;
    font-weight: 650;
    letter-spacing: 0.06em;
    margin: 0;
  }

  h2.PDF_CSub{
    font-family: var(--font-head);
    font-size: 12.5pt;
    font-weight: 500;
    font-style: italic;
    color: var(--muted);
    margin: 2.5mm 0 0 0;
  }

  /* ===== Scene blocks ===== */
  div.SceneCody,
  div.SceneKatiya,
  div.SceneTitus{
    margin: 7mm auto 0 auto;
    padding-top: 5mm;
    border-top: 1px solid var(--rule);
  }

  /* Scene number badge */
  h3.PDF_Snum{
    display: inline-block;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 9.5pt;
    font-weight: 650;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin: 0 10px 0 0;
    padding: 2px 7px;
    border: 1px solid var(--rule);
    border-radius: 999px;
    vertical-align: baseline;
  }

  /* POV tint on the badge border (subtle but helpful) */
  div.SceneCody  h3.PDF_Snum{ border-color: color-mix(in srgb, var(--cody) 35%, var(--rule)); }
  div.SceneKatiya h3.PDF_Snum{ border-color: color-mix(in srgb, var(--katiya) 35%, var(--rule)); }
  div.SceneTitus h3.PDF_Snum{ border-color: color-mix(in srgb, var(--titus) 35%, var(--rule)); }

  /* ===== Paragraphs ===== */
  p.BodyCody,
  p.BodyKatiya,
  p.BodyTitus{
    margin: 0 0 var(--para-gap) 0;
    text-indent: var(--para-indent);
  }

  /* First paragraph after the scene badge should NOT indent
     (your HTML is: <h3 ...></h3><p ...>First line...</p>) */
  h3.PDF_Snum + p.BodyCody,
  h3.PDF_Snum + p.BodyKatiya,
  h3.PDF_Snum + p.BodyTitus{
    text-indent: 0;
    display: inline; /* keeps the badge + first sentence feeling intentional */
  }

  /* After the first paragraph, return to block flow */
  h3.PDF_Snum + p + p{
    display: block;
  }

  /* Optional: tiny POV side-rule to help scanning (very light) */
  div.SceneCody  p.BodyCody,
  div.SceneKatiya p.BodyKatiya,
  div.SceneTitus p.BodyTitus{
    padding-left: 0.9em;
    border-left: 2px solid transparent;
  }
  div.SceneCody  p.BodyCody{ border-left-color: color-mix(in srgb, var(--cody) 22%, transparent); }
  div.SceneKatiya p.BodyKatiya{ border-left-color: color-mix(in srgb, var(--katiya) 22%, transparent); }
  div.SceneTitus p.BodyTitus{ border-left-color: color-mix(in srgb, var(--titus) 22%, transparent); }
}

/* ---------- SCREEN (optional, for quick previewing the fragments) ---------- */
@media screen {
  body{
    background: #0f1115;
    color: #e7e7ea;
    font-family: var(--font-body);
    line-height: 1.6;
    padding: 22px 12px;
  }
  body > *{
    max-width: 78ch;
    margin-left: auto;
    margin-right: auto;
  }

  div.StoryHeader{
    display:flex;
    justify-content:center;
    align-items:center;
    gap: 20px;
    margin: 0 0 22px 0;
    padding: 0 0 16px 0;
    border-bottom: 1px solid rgba(231,231,234,0.14);
  }
  div.StoryHeader img{ height: 52px; filter: none; }

  div.HeaderParagate,
  div.HeaderFirebrand{
    text-align:center;
    margin: 22px 0 18px 0;
    padding: 0 0 14px 0;
    border-bottom: 1px solid rgba(231,231,234,0.14);
  }

  h1.PDF_CTitle{ margin:0; font-size: 1.55rem; letter-spacing: 0.05em; }
  h2.PDF_CSub{ margin: 6px 0 0 0; color: rgba(231,231,234,0.72); font-style: italic; }

  div.SceneCody, div.SceneKatiya, div.SceneTitus{
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid rgba(231,231,234,0.12);
  }

  h3.PDF_Snum{
    display:inline-block;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    font-size: 0.8rem;
    letter-spacing: 0.12em;
    padding: 2px 8px;
    border-radius: 999px;
    border: 1px solid rgba(231,231,234,0.18);
    color: rgba(231,231,234,0.72);
    margin: 0 10px 0 0;
  }

  p.BodyCody, p.BodyKatiya, p.BodyTitus{
    margin: 0 0 0.9em 0;
    text-indent: 1.4em;
  }
  h3.PDF_Snum + p.BodyCody,
  h3.PDF_Snum + p.BodyKatiya,
  h3.PDF_Snum + p.BodyTitus{ text-indent: 0; display: inline; }

  div.SceneCody  p.BodyCody{ border-left: 2px solid color-mix(in srgb, var(--cody) 45%, transparent); padding-left: 0.9em; }
  div.SceneKatiya p.BodyKatiya{ border-left: 2px solid color-mix(in srgb, var(--katiya) 45%, transparent); padding-left: 0.9em; }
  div.SceneTitus p.BodyTitus{ border-left: 2px solid color-mix(in srgb, var(--titus) 45%, transparent); padding-left: 0.9em; }
}
"""


def _wrap_fragment(fragment_html: str, base_href: str, css_text: str) -> str:
    # Your chapter HTMLs are fragments (no <html>/<head>), so wrap them.
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <base href="{base_href}">
  <style>{css_text}</style>
</head>
<body>
{fragment_html}
</body>
</html>
"""


async def build_pdfs_from_html_dir_async(
    html_dir: str | Path,
    out_dir: str | Path,
    paper: str = "Letter",
    css_path: Optional[str | Path] = None,
    include_page_numbers: bool = True,
) -> List[Path]:
    html_dir = Path(html_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    css_text = _DEFAULT_PRINT_CSS if not css_path else Path(css_path).read_text(encoding="utf-8")

    chapter_files = [
        p for p in html_dir.glob("*.html")
        if not p.name.startswith("_") and p.stem.isdigit()
    ]
    chapter_files.sort(key=lambda p: int(p.stem))

    if not chapter_files:
        raise FileNotFoundError(f"No numeric chapter HTML files found in: {html_dir}")

    base_href = html_dir.resolve().as_uri() + "/"

    header_template = "<div></div>"
    footer_template = (
        "<div style='font-size:9px;width:100%;padding:0 10mm;color:#666;"
        "display:flex;justify-content:flex-end;'>"
        "Page <span class='pageNumber'></span> / <span class='totalPages'></span>"
        "</div>"
    )

    written: List[Path] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for html_path in chapter_files:
            fragment = html_path.read_text(encoding="utf-8", errors="ignore")
            full_html = _wrap_fragment(fragment, base_href=base_href, css_text=css_text)

            await page.set_content(full_html, wait_until="load")
            await page.emulate_media(media="print")

            out_pdf = out_dir / f"{html_path.stem}.pdf"
            await page.pdf(
                path=str(out_pdf),
                format=paper,
                print_background=True,
                margin={"top": "18mm", "right": "16mm", "bottom": "18mm", "left": "16mm"},
                display_header_footer=include_page_numbers,
                header_template=header_template if include_page_numbers else None,
                footer_template=footer_template if include_page_numbers else None,
            )
            written.append(out_pdf)

        await browser.close()

    return written

def _run_coro_blocking(coro):
    """
    Runs an async coroutine and blocks until complete.
    Works even if there's already a running loop (Jupyter/IPython), by using a thread.
    On Windows, forces a Proactor loop so subprocess (Playwright driver) works.
    """

    def run_in_fresh_loop():
        # Force Proactor loop on Windows so asyncio subprocess works.
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            try:
                loop.close()
            except Exception:
                pass

    # If no loop is running in this thread, just run directly.
    try:
        asyncio.get_running_loop()
        loop_running = True
    except RuntimeError:
        loop_running = False

    if not loop_running:
        return run_in_fresh_loop()

    # If a loop *is* running (Jupyter etc.), run in a separate thread.
    result = {}
    error = {}

    def runner():
        try:
            result["value"] = run_in_fresh_loop()
        except Exception as e:
            error["exc"] = e

    t = threading.Thread(target=runner, daemon=False)
    t.start()
    t.join()

    if "exc" in error:
        raise error["exc"]
    return result.get("value")


def build_pdfs_from_html_dir(
    html_dir: str | Path,
    out_dir: str | Path,
    paper: str = "Letter",
    css_path: Optional[str | Path] = None,
    include_page_numbers: bool = True,
) -> List[Path]:
    """
    Sync wrapper around the async implementation.
    Keep calling this from SavePDF() exactly like before.
    """
    return _run_coro_blocking(
        build_pdfs_from_html_dir_async(
            html_dir=html_dir,
            out_dir=out_dir,
            paper=paper,
            css_path=css_path,
            include_page_numbers=include_page_numbers,
        )
    )