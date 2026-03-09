"""
paragate_gpt_parse.py

Importable converter for Paragate_GPT-style JSON exports.

Primary API:
    out_obj = GPT_Parse(input_json_obj)

Where input_json_obj is the *already-parsed* JSON object (a Python list/dict),
and out_obj is the converted object shaped like:

{
  "__meta": {...},
  "__index": {...},
  "chapters": [...]
}

Design goals:
- No file I/O (you handle loading/saving in your main program).
- HTML entity decoding for nicer text (optional).
- Normalizes scene Text fields to List[str] and Perspective to a non-empty string.
- Builds compact lookup tables for fast chapter retrieval.
"""

from __future__ import annotations

import html as _html
import unicodedata as _unicodedata
from typing import Any, Dict, List, Optional, Tuple, Union


JsonType = Union[Dict[str, Any], List[Any]]


def GPT_Parse(
    input_json_obj: JsonType,
    *,
    source_name: str = "in-memory",
    unescape_html_entities: bool = True,
    trim_trailing_blank_lines: bool = True,
    include_entries: bool = True,
) -> Dict[str, Any]:
    """
    Convert a Paragate_GPT JSON object into an indexed + decoded format.

    Parameters
    ----------
    input_json_obj:
        Parsed JSON object (Python list/dict). Accepts either:
          - A list of chapter dicts, OR
          - A dict containing a 'chapters' list (we will rebuild indices).
    source_name:
        Used only for metadata.
    unescape_html_entities:
        If True, applies html.unescape() to all strings (e.g., &apos; -> ').
    trim_trailing_blank_lines:
        If True, removes trailing blank/whitespace-only lines at the end of each scene Text[].
        (Internal blank lines are preserved.)
    include_entries:
        If True, include __index["entries"] (human-auditable per-chapter rows).
        If False, omit entries to shrink size; lookup maps still provided.

    Returns
    -------
    Dict[str, Any]:
        Converted JSON object with keys: "__meta", "__index", "chapters".
    """
    decoded = _decode_strings(input_json_obj, do_unescape=unescape_html_entities)

    chapters = _extract_chapters(decoded)
    normalized_chapters, chapter_width = _normalize_chapters(
        chapters,
        trim_empty=trim_trailing_blank_lines,
    )

    index_obj = _build_index(normalized_chapters, chapter_width=chapter_width, include_entries=include_entries)

    out_obj: Dict[str, Any] = {
        "__meta": {
            "source": source_name,
            "notes": [
                "This file wraps the original chapter array under key 'chapters' and adds a compact index for fast lookup.",
                "Indices are 0-based into chapters[].",
                "Prefer id lookup (A##C##) if you ever renumber chapters or add interludes.",
            ],
            "how_to_retrieve": {
                "python_examples": [
                    "ch = out['chapters'][ out['__index']['id_to_index']['A02C33'] ]",
                    "all_lines = [line for sc in ch['Scenes'] for line in sc['Text']]",
                    "scene2_lines = ch['Scenes'][1]['Text']",
                ],
                "jq_examples": [
                    ".chapters[ (.__index.id_to_index[\"A02C33\"]) ]",
                    ".chapters[] | select(.Chapter==33) | .Scenes[].Text[]",
                ],
            },
        },
        "__index": index_obj,
        "chapters": normalized_chapters,
    }

    return out_obj


# ----------------------------
# Internals
# ----------------------------

def _extract_chapters(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict) and isinstance(obj.get("chapters"), list):
        raw_chapters = obj["chapters"]
    elif isinstance(obj, list):
        raw_chapters = obj
    else:
        raise TypeError(
            "input_json_obj must be a list of chapters OR a dict containing a 'chapters' list."
        )

    chapters: List[Dict[str, Any]] = []
    for ch in raw_chapters:
        if isinstance(ch, dict):
            chapters.append(ch)
        else:
            # Coerce non-dict chapter entries into a minimal shape rather than exploding
            chapters.append({"Act": None, "Chapter": None, "Chapter Name": "", "Scenes": []})
    return chapters


def _decode_strings(obj: Any, *, do_unescape: bool) -> Any:
    """
    Recursively decode HTML entities in all strings and normalize unicode/newlines.
    """
    if isinstance(obj, str):
        s = obj
        if do_unescape:
            s = _html.unescape(s)
        s = _unicodedata.normalize("NFC", s)
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        return s
    if isinstance(obj, list):
        return [_decode_strings(x, do_unescape=do_unescape) for x in obj]
    if isinstance(obj, dict):
        return {k: _decode_strings(v, do_unescape=do_unescape) for k, v in obj.items()}
    return obj


def _normalize_chapters(
    chapters: List[Dict[str, Any]],
    *,
    trim_empty: bool,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Ensure each chapter has Scenes as list[dict], each scene has Text as list[str], etc.
    Also returns dynamic chapter id width based on max chapter number (min 2).
    """
    normalized: List[Dict[str, Any]] = []
    chapter_nums: List[int] = []

    for ch in chapters:
        ch_out = dict(ch)

        scenes = ch_out.get("Scenes", [])
        if not isinstance(scenes, list):
            scenes = []

        scenes_out: List[Dict[str, Any]] = []
        for s in scenes:
            if isinstance(s, dict):
                scenes_out.append(_ensure_scene_shape(s, trim_empty=trim_empty))
        ch_out["Scenes"] = scenes_out

        act, chapnum, _name = _get_chapter_fields(ch_out)
        if chapnum is not None:
            chapter_nums.append(chapnum)

        normalized.append(ch_out)

    # Dynamic width for "C##" part, supports chapter >= 100 cleanly
    if chapter_nums:
        width = max(2, len(str(max(chapter_nums))))
    else:
        width = 2

    return normalized, width


def _ensure_scene_shape(scene: Dict[str, Any], *, trim_empty: bool) -> Dict[str, Any]:
    out = dict(scene)

    # Perspective
    p = out.get("Perspective", "Default")
    if p is None or str(p).strip() == "":
        out["Perspective"] = "Default"
    else:
        out["Perspective"] = str(p)

    # Text -> list[str]
    txt = out.get("Text", [])
    if isinstance(txt, str):
        txt_list = txt.split("\n")
    elif isinstance(txt, list):
        txt_list = ["" if t is None else str(t) for t in txt]
    else:
        txt_list = [str(txt)]

    if trim_empty:
        txt_list = _trim_trailing_blank_lines(txt_list)

    out["Text"] = txt_list
    return out


def _trim_trailing_blank_lines(lines: List[str]) -> List[str]:
    out = list(lines)
    while out and (not str(out[-1]).strip()):
        out.pop()
    return out


def _as_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        if isinstance(x, bool):
            return None
        return int(x)
    except Exception:
        return None


def _get_chapter_fields(ch: Dict[str, Any]) -> Tuple[Optional[int], Optional[int], str]:
    act = _as_int(ch.get("Act", ch.get("act")))
    chapnum = _as_int(ch.get("Chapter", ch.get("chapter")))
    name = (
        ch.get("Chapter Name")
        or ch.get("ChapterName")
        or ch.get("chapter_name")
        or ""
    )
    return act, chapnum, str(name)


def _build_id(act: Optional[int], chapnum: Optional[int], *, chapter_width: int) -> str:
    act_str = f"{act:02d}" if act is not None else "??"
    if chapnum is None:
        ch_str = "?" * max(2, chapter_width)
    else:
        ch_str = str(chapnum).zfill(max(2, chapter_width))
    return f"A{act_str}C{ch_str}"


def _compress_consecutive(values: List[str]) -> List[str]:
    out: List[str] = []
    prev: Optional[str] = None
    for v in values:
        if v != prev:
            out.append(v)
            prev = v
    return out


def _build_index(
    chapters: List[Dict[str, Any]],
    *,
    chapter_width: int,
    include_entries: bool,
) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    id_to_index: Dict[str, int] = {}
    act_ch_to_index: Dict[str, int] = {}
    chapter_to_indices: Dict[str, List[int]] = {}

    for idx, ch in enumerate(chapters):
        act, chapnum, name = _get_chapter_fields(ch)
        cid = _build_id(act, chapnum, chapter_width=chapter_width)

        scenes = ch.get("Scenes", []) or []
        perspectives = []
        for s in scenes:
            if isinstance(s, dict):
                perspectives.append(str(s.get("Perspective", "Default")))
        perspectives_order = _compress_consecutive(perspectives) if perspectives else ["Default"]

        if include_entries:
            entries.append({
                "id": cid,
                "act": act,
                "chapter": chapnum,
                "name": name,
                "index": idx,
                "scene_count": len(scenes),
                "perspectives_order": perspectives_order,
            })

        id_to_index[cid] = idx
        if act is not None and chapnum is not None:
            act_ch_to_index[f"{act}:{chapnum}"] = idx
        if chapnum is not None:
            chapter_to_indices.setdefault(str(chapnum), []).append(idx)

    index_obj: Dict[str, Any] = {
        "id_to_index": id_to_index,
        "act_ch_to_index": act_ch_to_index,
        "chapter_to_indices": chapter_to_indices,
    }
    if include_entries:
        index_obj["entries"] = entries

    return index_obj
