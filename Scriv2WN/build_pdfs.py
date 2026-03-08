import sys
import asyncio
import threading
from pathlib import Path
from typing import Optional, List

from playwright.async_api import async_playwright


_DEFAULT_PRINT_CSS = r"""
/* =========================================================
   Scriv2WN – Print Stylesheet (Two Modes)
   ---------------------------------------------------------
   Modes:
     body[data-mode="chapter"]  -> single-chapter PDF (no forced chapter page breaks)
     body[data-mode="book"]     -> multi-chapter / full-book PDF (chapters start new pages)
   ---------------------------------------------------------
   Targets:
     div.StoryHeader
     div.HeaderParagate, div.HeaderFirebrand
     h1.PDF_CTitle, h2.PDF_CSub, h3.PDF_Snum
     div.SceneCody, div.SceneKatiya, div.SceneTitus
     p.BodyCody, p.BodyKatiya, p.BodyTitus
   ========================================================= */

/* ---------- Page setup ---------- */
@page{
  size: Letter;

  /* More breathing room top/bottom */
  margin: 1.15in 0.85in 1.10in 0.85in;
}

/* ---------- Variables ---------- */
:root{
  /* Typography */
  --TextSize: 11.25pt;
  --LineHeight: 1.48;
  --Measure: 66ch;

  /* Color */
  --Ink: #111;
  --Muted: #5f6368;
  --Rule: #d8dadd;

  /* Rhythm */
  --ParaGap: 0.85em;
  --Indent: 1.5em;

  /* Fonts */
  --CodyTitle: "Oxanium", "Bahnschrift", Arial, sans-serif;
  --CodyText:  "Roboto Flex", "Bahnschrift", Arial, sans-serif;
  --CodySize:  calc(var(--TextSize) - 0.25pt);

  --KatiyaTitle: "Cormorant Unicase", "Palatino Linotype", Palatino, Georgia, serif;
  --KatiyaText:  "Cormorant Infant",  "Palatino Linotype", Palatino, Georgia, serif;
  --KatiyaSize:  var(--TextSize);

  --TitusTitle: "Cormorant Unicase", "Palatino Linotype", Palatino, Georgia, serif;
  --TitusText:  "Cormorant Infant",  "Palatino Linotype", Palatino, Georgia, serif;
  --TitusSize:  var(--TextSize);
}

/* ---------- Minimal reset + print niceties ---------- */
*{ box-sizing: border-box; }
html, body{ margin: 0; padding: 0; }
img{ max-width: 100%; height: auto; }
p{ margin: 0; }
em{ font-style: italic; }

body{
  color: var(--Ink);
  font-size: var(--TextSize);
  line-height: var(--LineHeight);
  font-kerning: normal;
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
  hyphens: auto;
}

/* Keep content readable (centered measure) */
body > *{
  max-width: var(--Measure);
  margin-left: auto;
  margin-right: auto;
}

/* Prevent lonely lines */
p{ orphans: 3; widows: 3; }

/* Avoid awkward breaks around headings */
h1, h2, h3{ break-after: avoid; }

/* ---------- Mode switch defaults ---------- */
/* Default to "chapter" if the attribute is missing */
body:not([data-mode]){ --MODE: chapter; }

/* ---------- Story Header (logos) ---------- */
div.StoryHeader{
  margin-top: 0.25in;
  margin-bottom: 0.55in;
  padding-bottom: 0.25in;
  border-bottom: 1px solid var(--Rule);
  text-align: center;

  /* Do NOT force a page break after this */
  break-after: auto;
}

img.Namesake{
  width: 80%;
  max-width: 6.0in;
  display: block;
  margin: 0 auto 0.15in auto;

  /* Your sample uses *_inv.png (for dark mode), so invert back for print */
  filter: invert(0);
}

img.AuthorName{
  width: 34%;
  max-width: 3.0in;
  display: block;
  margin: 0 auto;

  filter: invert(0);
}

/* ---------- Chapter Header Blocks ---------- */
div.HeaderParagate,
div.HeaderFirebrand{
  text-align: center;
  margin: 0.35in auto 0.30in auto;
  padding-bottom: 0.20in;
  border-bottom: 1px solid var(--Rule);

  /* IMPORTANT: do NOT strand the header at the bottom */
  break-inside: avoid;
  break-after: avoid;
}

/* Mode: BOOK => each chapter header starts on a new page,
   BUT NOT if it immediately follows StoryHeader (first chapter in the doc). */
body[data-mode="book"] > div.HeaderParagate,
body[data-mode="book"] > div.HeaderFirebrand{
  break-before: page;
}
body[data-mode="book"] > div.StoryHeader + div.HeaderParagate,
body[data-mode="book"] > div.StoryHeader + div.HeaderFirebrand{
  break-before: auto;
}

/* Mode: CHAPTER => never force chapter page breaks */
body[data-mode="chapter"] > div.HeaderParagate,
body[data-mode="chapter"] > div.HeaderFirebrand{
  break-before: auto;
}

/* Title / subtitle */
h1.PDF_CTitle{
  margin: 0;
  font-size: 18pt;
  font-weight: 650;
  letter-spacing: 0.07em;
  color: var(--Ink);
}
h2.PDF_CSub{
  margin: 0.12in 0 0 0;
  font-size: 12.5pt;
  font-weight: 500;
  font-style: italic;
  color: var(--Muted);
  white-space: nowrap;
}

/* Optional: choose chapter header font based on which header div is used */
div.HeaderParagate h1.PDF_CTitle,
div.HeaderParagate h2.PDF_CSub{
  font-family: var(--CodyTitle);
}
div.HeaderFirebrand h1.PDF_CTitle,
div.HeaderFirebrand h2.PDF_CSub{
  font-family: var(--TitusTitle);
}

/* ---------- Scene Blocks ---------- */
/* Key change: DO NOT "avoid-page" on scenes. Let them flow naturally. */
div.SceneCody,
div.SceneKatiya,
div.SceneTitus{
  margin: 0.22in auto 0 auto;
  padding-top: 0.18in;
  border-top: 1px solid var(--Rule);

  break-inside: auto;          /* allow splitting across pages */
}

/* ---------- Center-set scene numbers ---------- */
h3.PDF_Snum{
  display: block;
  width: 100%;
  text-align: center;

  margin: 0 0 0.16in 0;
  padding: 0;

  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 9.5pt;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: var(--Muted);

  /* Keep the number with the next paragraph */
  break-after: avoid;
}

/* Optional: subtle lines flanking the number */
h3.PDF_Snum::before,
h3.PDF_Snum::after{
  content: "";
  display: inline-block;
  vertical-align: middle;
  width: 18%;
  border-top: 1px solid var(--Rule);
  margin: 0 0.14in;
}

/* Ensure the first paragraph stays with the scene number */
h3.PDF_Snum + p.BodyCody,
h3.PDF_Snum + p.BodyKatiya,
h3.PDF_Snum + p.BodyTitus{
  break-before: avoid;
  text-indent: 0; /* reads clean after a centered break marker */
}

/* ---------- Paragraph styles ---------- */
p.BodyCody,
p.BodyKatiya,
p.BodyTitus{
  margin: 0 0 var(--ParaGap) 0;
  text-indent: var(--Indent);
}

/* First paragraph after a scene number: no indent (already set above) */
h3.PDF_Snum + p.BodyCody,
h3.PDF_Snum + p.BodyKatiya,
h3.PDF_Snum + p.BodyTitus{
  text-indent: 0;
}

/* Cody POV */
p.BodyCody{
  font-family: var(--CodyText);
  font-size: var(--CodySize);
  font-weight: 300;
}

/* Katiya POV */
p.BodyKatiya{
  font-family: var(--KatiyaText);
  font-size: var(--KatiyaSize);
  font-weight: 400;
}

/* Titus POV */
p.BodyTitus{
  font-family: var(--TitusText);
  font-size: var(--TitusSize);
  font-weight: 400;
}

/* ---------- Screen preview (optional) ---------- */
@media screen{
  body{
    background: #0f1115;
    color: #e7e7ea;
    padding: 22px 12px;
    line-height: 1.6;
  }
  body > *{ max-width: 78ch; }

  div.StoryHeader{
    border-bottom: 1px solid rgba(231,231,234,0.14);
  }
  img.Namesake, img.AuthorName{
    filter: none;
  }

  div.HeaderParagate,
  div.HeaderFirebrand{
    border-bottom: 1px solid rgba(231,231,234,0.14);
  }

  h2.PDF_CSub{ color: rgba(231,231,234,0.72); }

  div.SceneCody, div.SceneKatiya, div.SceneTitus{
    border-top: 1px solid rgba(231,231,234,0.12);
  }

  h3.PDF_Snum{
    color: rgba(231,231,234,0.72);
  }
  h3.PDF_Snum::before,
  h3.PDF_Snum::after{
    border-top-color: rgba(231,231,234,0.18);
  }
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
              format="Letter",
              print_background=True,
              prefer_css_page_size=True,

              # IMPORTANT: give footer room (match or exceed your @page margins)
              margin={"top": "1.15in", "right": "0.85in", "bottom": "1.10in", "left": "0.85in"},

              display_header_footer=True,
              header_template="<div></div>",
              footer_template="""
                <div style="width:100%; font-size:9px; padding:0 0.85in; color:#666;
                            display:flex; justify-content:center;">
                Page <span class="pageNumber"></span> / <span class="totalPages"></span>
                </div>
              """,
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