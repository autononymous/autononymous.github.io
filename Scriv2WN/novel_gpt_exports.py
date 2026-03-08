from __future__ import annotations

"""
novel_gpt_exports.py

Drop-in exporter module for GPT-facing novel JSON bundles.

Intended usage from Scriv2WebNovel.py:

    from novel_gpt_exports import SaveGPTExports
    ...
    SaveGPTExports(MANUSCRIPT, JS, indentLevel=3)

This module preserves the legacy prose export expected by paragate_gpt_parse.GPT_Parse,
while also emitting flatter, metadata-richer JSON files that are better for LLM retrieval.
"""

import json as js
import os
import html
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from paragate_gpt_parse import GPT_Parse


JsonDict = Dict[str, Any]


def SaveGPTExports(manuscriptDict: JsonDict,
                   raw_json: Optional[JsonDict] = None,
                   indentLevel: Optional[int] = 2,
                   out_dir: str = "/GPT") -> Dict[str, str]:
    """
    Write a suite of GPT-facing exports.

    Parameters
    ----------
    manuscriptDict:
        The normalized manuscript object returned by InterpretJSON(...), i.e.
        {"Story": {...}, "Metadata": {...}}
    raw_json:
        Optional raw Scrivener-export JSON. If provided, scene/chapter exports will be
        enriched with fields like Synopsis, Summary, Status, Keywords, AuthorNotes, etc.
    indentLevel:
        Pretty-print indent for output JSON.
    out_dir:
        Output directory relative to the current working directory.

    Returns
    -------
    Dict[str, str]
        Mapping of logical export names to written file paths.
    """
    if not isinstance(manuscriptDict, dict) or "Story" not in manuscriptDict:
        raise TypeError("manuscriptDict must be the MANUSCRIPT object returned by InterpretJSON(...)")

    story_dict = manuscriptDict["Story"]
    if not story_dict:
        raise ValueError("manuscriptDict['Story'] is empty.")

    chapter_keys = sorted(story_dict.keys())
    first_story = story_dict[chapter_keys[0]].get("Story", "Story")
    story_name = str(first_story)

    out_root = os.path.join(os.getcwd(), out_dir.strip("/\\"))
    os.makedirs(out_root, exist_ok=True)

    chapter_width = _compute_chapter_width(story_dict.values())
    raw_lookup = _build_raw_lookup(raw_json)

    prose_chapters: List[JsonDict] = []
    chapter_records: List[JsonDict] = []
    scene_records: List[JsonDict] = []

    for key in chapter_keys:
        chapter_entry = story_dict[key]
        if not chapter_entry.get("Written", False):
            continue

        chapter_record, prose_record, scene_rows = _build_chapter_exports(
            chapter_entry=chapter_entry,
            chapter_width=chapter_width,
            raw_lookup=raw_lookup,
        )
        prose_chapters.append(prose_record)
        chapter_records.append(chapter_record)
        scene_records.extend(scene_rows)

    prose_path = os.path.join(out_root, f"{story_name}_GPT.json")
    indexed_path = os.path.join(out_root, f"{story_name}_GPT_index.json")
    chapters_path = os.path.join(out_root, f"{story_name}_GPT_chapters.json")
    scenes_path = os.path.join(out_root, f"{story_name}_GPT_scenes.json")
    manifest_path = os.path.join(out_root, f"{story_name}_GPT_manifest.json")

    _dump_json(prose_path, prose_chapters, indentLevel)

    indexed_obj = GPT_Parse(prose_chapters, source_name=os.path.basename(prose_path))
    _dump_json(indexed_path, indexed_obj, indentLevel)

    chapters_obj = _build_chapter_bundle(story_name, manuscriptDict.get("Metadata", {}), chapter_records)
    scenes_obj = _build_scene_bundle(story_name, scene_records)
    manifest_obj = _build_manifest(
        story_name=story_name,
        metadata=manuscriptDict.get("Metadata", {}),
        prose_path=prose_path,
        indexed_path=indexed_path,
        chapters_path=chapters_path,
        scenes_path=scenes_path,
        chapter_records=chapter_records,
        scene_records=scene_records,
    )

    _dump_json(chapters_path, chapters_obj, indentLevel)
    _dump_json(scenes_path, scenes_obj, indentLevel)
    _dump_json(manifest_path, manifest_obj, indentLevel)

    print(f" > Created GPT exports for {story_name}.")

    return {
        "prose": prose_path,
        "indexed": indexed_path,
        "chapters": chapters_path,
        "scenes": scenes_path,
        "manifest": manifest_path,
    }


# -----------------------------------------------------------------------------
# Builders
# -----------------------------------------------------------------------------


def _build_chapter_exports(chapter_entry: JsonDict,
                           chapter_width: int,
                           raw_lookup: JsonDict) -> Tuple[JsonDict, JsonDict, List[JsonDict]]:
    act = _safe_int(chapter_entry.get("Act"))
    chapter_num = _safe_int(chapter_entry.get("Chapter"))
    chapter_id = _build_chapter_id(act, chapter_num, chapter_width=chapter_width)
    chapter_name = _norm(chapter_entry.get("ChapterName", ""))

    raw_chapter = raw_lookup["chapters_by_act_ch"].get((act, chapter_num), {})

    povs: List[str] = list(chapter_entry.get("POV", []))
    settings: List[JsonDict] = list(chapter_entry.get("Settings", []))
    bodies: List[List[List[Any]]] = list(chapter_entry.get("Body", []))
    ids: List[str] = list(chapter_entry.get("IDs", []))
    wcs: List[int] = list(chapter_entry.get("WCs", []))

    prose_scenes: List[JsonDict] = []
    scene_rows: List[JsonDict] = []
    scene_ids: List[str] = []
    unique_settings: List[JsonDict] = []
    chapter_style_classes: List[str] = []

    created_values: List[str] = []
    modified_values: List[str] = []

    scene_width = max(2, len(str(len(bodies)))) if bodies else 2

    for i, scene in enumerate(bodies):
        scene_num = i + 1
        scene_id = f"{chapter_id}S{str(scene_num).zfill(scene_width)}"
        scene_ids.append(scene_id)

        scene_setting = settings[i] if i < len(settings) else {}
        raw_scene = raw_lookup["scenes_by_verbose_id"].get(ids[i] if i < len(ids) else None, {})
        scene_pov = _norm(povs[i] if i < len(povs) else "Default") or "Default"
        paragraphs = _scene_fragments_to_paragraphs(scene)
        full_text = "\n\n".join(paragraphs)
        style_classes = _scene_style_classes(scene)
        chapter_style_classes.extend(style_classes)

        history = {
            "Created": _norm(_pick_first(raw_scene, "CreatedDate", default=_nested_get(chapter_entry, ["History", "Created"]))),
            "Modified": _norm(_pick_first(raw_scene, "ModifiedDate", default=_nested_get(chapter_entry, ["History", "Modified"]))),
        }
        if history["Created"]:
            created_values.append(history["Created"])
        if history["Modified"]:
            modified_values.append(history["Modified"])

        scene_summary = _norm(_pick_first(raw_scene, "Summary"))
        scene_synopsis = _norm(_pick_first(raw_scene, "Synopsis"))
        scene_author_notes = _norm(_pick_first(raw_scene, "AuthorNotes"))
        scene_keywords = _split_keywords(_pick_first(raw_scene, "Keywords"))
        scene_status = _norm(_pick_first(raw_scene, "Status"))
        scene_label = _norm(_pick_first(raw_scene, "Label"))
        scene_doc_name = _norm(_pick_first(raw_scene, "DocName"))
        scene_uuid = _norm(_pick_first(raw_scene, "UUID"))
        scene_written = bool(full_text.strip())
        word_count = int(wcs[i]) if i < len(wcs) else _count_words(full_text)

        prose_scenes.append({
            "SceneID": scene_id,
            "VerboseID": _norm(ids[i] if i < len(ids) else ""),
            "Perspective": scene_pov,
            "Text": paragraphs,
            "Setting": scene_setting,
            "WordCount": word_count,
            "Summary": scene_summary,
            "Synopsis": scene_synopsis,
            "AuthorNotes": scene_author_notes,
            "Status": scene_status,
            "Label": scene_label,
            "Keywords": scene_keywords,
            "History": history,
            "DocName": scene_doc_name,
            "UUID": scene_uuid,
            "StyleClasses": style_classes,
        })

        flat_scene = {
            "id": scene_id,
            "chapter_id": chapter_id,
            "chapter": chapter_num,
            "chapter_name": chapter_name,
            "act": act,
            "act_name": _norm(chapter_entry.get("ActName", "")),
            "scene_number": scene_num,
            "verbose_id": _norm(ids[i] if i < len(ids) else ""),
            "doc_name": scene_doc_name,
            "uuid": scene_uuid,
            "pov": scene_pov,
            "written": scene_written,
            "word_count": word_count,
            "setting": scene_setting,
            "setting_text": _setting_to_text(scene_setting),
            "history": history,
            "status": scene_status,
            "label": scene_label,
            "keywords": scene_keywords,
            "summary": scene_summary,
            "synopsis": scene_synopsis,
            "author_notes": scene_author_notes,
            "chapter_summary": _norm(chapter_entry.get("Summary", "")),
            "chapter_blurb": _norm(chapter_entry.get("Blurb", "")),
            "style_classes": style_classes,
            "text_blocks": paragraphs,
            "full_text": full_text,
        }
        scene_rows.append(flat_scene)
        _append_unique_setting(unique_settings, scene_setting)

    chapter_record = {
        "id": chapter_id,
        "act": act,
        "act_name": _norm(chapter_entry.get("ActName", "")),
        "chapter": chapter_num,
        "chapter_name": chapter_name,
        "chapter_number_name": _norm(chapter_entry.get("ChapterNumber", "")),
        "story": _norm(chapter_entry.get("Story", "")),
        "written": bool(chapter_entry.get("Written", False)),
        "completion": _norm(chapter_entry.get("Completion", "")),
        "summary": _norm(chapter_entry.get("Summary", "")),
        "blurb": _norm(chapter_entry.get("Blurb", "")),
        "next_publish": _norm(chapter_entry.get("NextPublish", "")),
        "scene_count": len(prose_scenes),
        "word_count": int(sum(wcs)) if wcs else sum(s["word_count"] for s in scene_rows),
        "pov_order": povs,
        "scene_ids": scene_ids,
        "settings": unique_settings,
        "settings_text": [_setting_to_text(s) for s in unique_settings],
        "history": {
            "CreatedEarliest": min(created_values) if created_values else "",
            "ModifiedLatest": max(modified_values) if modified_values else "",
        },
        "raw_metadata": {
            "doc_name": _norm(_pick_first(raw_chapter, "DocName")),
            "verbose_id": _norm(_pick_first(raw_chapter, "VerboseID")),
            "uuid": _norm(_pick_first(raw_chapter, "UUID")),
            "status": _norm(_pick_first(raw_chapter, "Status")),
            "label": _norm(_pick_first(raw_chapter, "Label")),
            "keywords": _split_keywords(_pick_first(raw_chapter, "Keywords")),
            "author_notes": _norm(_pick_first(raw_chapter, "AuthorNotes")),
            "auto_name_part": _norm(_pick_first(raw_chapter, "AutoNamePart")),
            "auto_name_full": _norm(_pick_first(raw_chapter, "AutoNameFull")),
            "is_prologue": _norm(_pick_first(raw_chapter, "IsPrologue")),
        },
        "style_classes": sorted(set(chapter_style_classes)),
    }

    prose_record = {
        "Scenes": prose_scenes,
        "SceneLocation": [[s.get("Setting", {})] for s in prose_scenes],
        "Chapter": chapter_num,
        "Act": act,
        "Chapter Name": chapter_name,
        "ChapterID": chapter_id,
        "Summary": _norm(chapter_entry.get("Summary", "")),
        "Blurb": _norm(chapter_entry.get("Blurb", "")),
        "NextPublish": _norm(chapter_entry.get("NextPublish", "")),
        "POVOrder": povs,
        "WordCount": chapter_record["word_count"],
        "Settings": unique_settings,
    }

    return chapter_record, prose_record, scene_rows


def _build_chapter_bundle(story_name: str,
                          metadata: JsonDict,
                          chapters: List[JsonDict]) -> JsonDict:
    id_to_index = {row["id"]: i for i, row in enumerate(chapters)}
    chapter_to_id = {str(row["chapter"]): row["id"] for row in chapters if row.get("chapter") is not None}
    act_to_ids: Dict[str, List[str]] = {}
    for row in chapters:
        act_to_ids.setdefault(str(row.get("act")), []).append(row["id"])

    return {
        "__meta": {
            "story": story_name,
            "export_type": "chapter_overview",
            "generated_utc": _utc_now(),
            "notes": [
                "Chapter-level retrieval file for summaries, blurbs, settings, POV order, and chapter-to-scene mapping.",
                "Use this file when the question is about chapter purpose, structure, or high-level continuity.",
            ],
            "manuscript_metadata": metadata,
        },
        "__index": {
            "id_to_index": id_to_index,
            "chapter_to_id": chapter_to_id,
            "act_to_ids": act_to_ids,
        },
        "chapters": chapters,
    }


def _build_scene_bundle(story_name: str,
                        scenes: List[JsonDict]) -> JsonDict:
    id_to_index = {row["id"]: i for i, row in enumerate(scenes)}
    chapter_to_scene_ids: Dict[str, List[str]] = {}
    pov_to_scene_ids: Dict[str, List[str]] = {}
    location_to_scene_ids: Dict[str, List[str]] = {}

    for row in scenes:
        chapter_to_scene_ids.setdefault(str(row.get("chapter_id")), []).append(row["id"])
        pov_to_scene_ids.setdefault(str(row.get("pov")), []).append(row["id"])
        location_key = row.get("setting_text", "")
        if location_key:
            location_to_scene_ids.setdefault(location_key, []).append(row["id"])

    return {
        "__meta": {
            "story": story_name,
            "export_type": "scene_flat",
            "generated_utc": _utc_now(),
            "notes": [
                "Primary GPT retrieval file. One row per scene, flattened for semantic search and editorial reasoning.",
                "Includes both scene-level text and attached chapter-level summary/blurb context.",
            ],
        },
        "__index": {
            "id_to_index": id_to_index,
            "chapter_to_scene_ids": chapter_to_scene_ids,
            "pov_to_scene_ids": pov_to_scene_ids,
            "location_to_scene_ids": location_to_scene_ids,
        },
        "scenes": scenes,
    }


def _build_manifest(story_name: str,
                    metadata: JsonDict,
                    prose_path: str,
                    indexed_path: str,
                    chapters_path: str,
                    scenes_path: str,
                    chapter_records: List[JsonDict],
                    scene_records: List[JsonDict]) -> JsonDict:
    return {
        "story": story_name,
        "generated_utc": _utc_now(),
        "metadata": metadata,
        "counts": {
            "chapters": len(chapter_records),
            "scenes": len(scene_records),
            "words": int(sum(ch.get("word_count", 0) for ch in chapter_records)),
        },
        "files": {
            "prose": os.path.basename(prose_path),
            "indexed": os.path.basename(indexed_path),
            "chapters": os.path.basename(chapters_path),
            "scenes": os.path.basename(scenes_path),
        },
        "recommended_usage": {
            "prose": "Best for exact chapter/scene text lookup and quote retrieval.",
            "indexed": "Best for direct chapter ID lookup using A##C## keys.",
            "chapters": "Best for chapter-level summaries, structure, and continuity checks.",
            "scenes": "Best for scene-level reasoning, emotional turns, setting queries, and editorial analysis.",
        },
    }


# -----------------------------------------------------------------------------
# Raw data lookup helpers
# -----------------------------------------------------------------------------


def _build_raw_lookup(raw_json: Optional[JsonDict]) -> JsonDict:
    lookup = {
        "chapters_by_act_ch": {},
        "scenes_by_verbose_id": {},
    }
    if not isinstance(raw_json, dict):
        return lookup

    manuscript = raw_json.get("Manuscript", [])
    if not isinstance(manuscript, list):
        return lookup

    for entry in manuscript:
        if not isinstance(entry, dict):
            continue
        dtype = entry.get("DocType")
        if dtype == "Chapter":
            key = (_safe_int(entry.get("ActNum")), _safe_int(entry.get("ChapterFull")))
            lookup["chapters_by_act_ch"][key] = entry
        elif dtype == "Scene":
            verbose_id = _norm(entry.get("VerboseID", ""))
            if verbose_id:
                lookup["scenes_by_verbose_id"][verbose_id] = entry
    return lookup


# -----------------------------------------------------------------------------
# Text helpers
# -----------------------------------------------------------------------------


def _scene_fragments_to_paragraphs(scene: Iterable[List[Any]]) -> List[str]:
    paragraphs: List[str] = []
    buffer: List[str] = []

    for fragment in scene:
        if not isinstance(fragment, (list, tuple)) or len(fragment) < 3:
            continue
        lineclass = fragment[0]
        text = _norm(fragment[1])
        is_eol = bool(fragment[2])

        if str(lineclass) == "EndOfScene":
            continue

        if text:
            buffer.append(text)

        if is_eol:
            para = "".join(buffer).strip()
            if para:
                paragraphs.append(para)
            buffer = []

    if buffer:
        para = "".join(buffer).strip()
        if para:
            paragraphs.append(para)

    return paragraphs


def _scene_style_classes(scene: Iterable[List[Any]]) -> List[str]:
    classes: List[str] = []
    seen = set()
    for fragment in scene:
        if not isinstance(fragment, (list, tuple)) or not fragment:
            continue
        lineclass = str(fragment[0])
        if lineclass and lineclass != "EndOfScene" and lineclass not in seen:
            classes.append(lineclass)
            seen.add(lineclass)
    return classes


# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------


def _compute_chapter_width(chapters: Iterable[JsonDict]) -> int:
    nums = [_safe_int(ch.get("Chapter")) for ch in chapters]
    nums = [n for n in nums if n is not None]
    return max(2, len(str(max(nums)))) if nums else 2


def _build_chapter_id(act: Optional[int], chapter: Optional[int], *, chapter_width: int) -> str:
    act_str = f"{act:02d}" if act is not None else "??"
    if chapter is None:
        ch_str = "?" * max(2, chapter_width)
    else:
        ch_str = str(chapter).zfill(max(2, chapter_width))
    return f"A{act_str}C{ch_str}"


def _append_unique_setting(target: List[JsonDict], setting: JsonDict) -> None:
    if not isinstance(setting, dict):
        return
    key = js.dumps(setting, sort_keys=True, ensure_ascii=False)
    existing = {js.dumps(row, sort_keys=True, ensure_ascii=False) for row in target}
    if key not in existing:
        target.append(setting)


def _setting_to_text(setting: Any) -> str:
    if not isinstance(setting, dict):
        return ""
    fields = [
        _norm(setting.get("Region", "")),
        _norm(setting.get("Area", "")),
        _norm(setting.get("Location", "")),
        _norm(setting.get("Place", "")),
        _norm(setting.get("Date", "")),
        _norm(setting.get("Time", "")),
    ]
    cleaned = [x for x in fields if x and x not in {"Unspecified", "Unknown"}]
    return " | ".join(cleaned)


def _safe_int(value: Any) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        if isinstance(value, bool):
            return None
        return int(value)
    except Exception:
        return None


def _norm(value: Any) -> str:
    if value is None:
        return ""
    s = html.unescape(str(value))
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s.strip()


def _split_keywords(value: Any) -> List[str]:
    raw = _norm(value)
    if not raw:
        return []
    if "," in raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    if ";" in raw:
        return [x.strip() for x in raw.split(";") if x.strip()]
    return [raw]


def _count_words(text: str) -> int:
    return len([token for token in text.split() if token.strip()])


def _pick_first(mapping: Any, key: str, default: Any = "") -> Any:
    if isinstance(mapping, dict):
        return mapping.get(key, default)
    return default


def _nested_get(mapping: Any, path: List[str], default: Any = "") -> Any:
    cur = mapping
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dump_json(path: str, obj: Any, indentLevel: Optional[int]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        js.dump(obj, f, ensure_ascii=False, indent=indentLevel)
        f.write("\n")
