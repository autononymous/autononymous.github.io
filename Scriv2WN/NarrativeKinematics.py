# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 15:42:16 2026

@author: rkiss"""
import json
import os
import csv
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from html import escape
import asyncio
import threading
from pathlib import Path
from playwright.async_api import async_playwright

from openai import OpenAI

class StoryNK:
    COLORS = {
        "Action": "#8B0000",
        "Drama": "#3A6EA5",
        "Theme": "#2E8B57",
        "Energy": "#D4AF37",
        "Gravity": "#6A0DAD",
        "Prominence": "#444444",
        "Mass": "#8C564B",
        "ThemeMass": "#228B22",
        "Steady": "#111111",
        "Transient": "#999999",
        "CutRisk": "#AA2222",
    }

    def __init__(
        self,
        Manuscript,
        doReport=False,
        story_name: Optional[str] = None,
        outdir: str = ".",
        factor_mode: str = "last",
        steady_window: int = 7,
        mass_window: int = 5,
        prominence_window: int = 5,
        gravity_weights: Tuple[float, float, float] = (0.4, 0.4, 0.2),
        cut_risk_weights: Tuple[float, float, float] = (0.4, 0.4, 0.2),
        peak_annotate_count: int = 8,
    ):
        self.outdir = outdir
        self.doReport = doReport
        self.factor_mode = factor_mode.lower().strip()
        self.steady_window = self._odd_window(steady_window)
        self.mass_window = self._odd_window(mass_window)
        self.prominence_window = self._odd_window(prominence_window)
        self.gravity_weights = self._normalize_weights(gravity_weights)
        self.cut_risk_weights = self._normalize_weights(cut_risk_weights)
        self.peak_annotate_count = peak_annotate_count

        self.ADTX: List[Dict[str, Any]] = []
        self.story_name = story_name or self._infer_story_name(Manuscript)

        self._ingest_manuscript(Manuscript)
        self._sort_adtx()
        self.compute_all_metrics()

        if self.doReport:
            self.export_report_bundle(self.outdir)

    # ---------------------------------------------------------------------
    # Ingestion
    # ---------------------------------------------------------------------

    def _infer_story_name(self, Manuscript) -> str:
        entries = list(Manuscript.values()) if hasattr(Manuscript, "values") else list(Manuscript)
        if not entries:
            return "Untitled Story"
        first = entries[0]
        if isinstance(first, dict):
            return first.get("Story", "Untitled Story")
        return "Untitled Story"

    def _ingest_manuscript(self, Manuscript) -> None:
        entries = list(Manuscript.values()) if hasattr(Manuscript, "values") else list(Manuscript)
    
        if not entries:
            return
    
        SCENESIZE_THRESHOLD = 350
    
        # Extract positions once
        raw_positions = [self._extract_position(entry) for entry in entries]
    
        # Use only "reasonable" scene sizes to estimate a fallback
        valid_positions = [p for p in raw_positions if p > SCENESIZE_THRESHOLD]
    
        # Median is usually more stable than mean for scene lengths
        if valid_positions:
            fallback_scene_size = float(np.median(valid_positions))
        else:
            # If everything is tiny, fall back to median of all positive values
            positive_positions = [p for p in raw_positions if p > 0]
            fallback_scene_size = float(np.median(positive_positions)) if positive_positions else 1000.0
    
        running_position = 0.0
    
        for i, (entry, raw_pos) in enumerate(zip(entries, raw_positions)):
            action, drama, theme = self._extract_factors(entry)
    
            #effective_pos = raw_pos if raw_pos > SCENESIZE_THRESHOLD else fallback_scene_size
            effective_pos = max(raw_pos, fallback_scene_size * 0.5)
            running_position += effective_pos
    
            row = {
                # Core NK state
                "Index": i + 1,
                "Position": running_position,
                "RawPosition": raw_pos,
                "EffectivePosition": effective_pos,
                "Action": action,
                "Drama": drama,
                "Theme": theme,
    
                # Manuscript metadata
                "Story": entry.get("Story", self.story_name),
                "Act": entry.get("Act", ""),
                "ActName": entry.get("ActName", ""),
                "Chapter": entry.get("Chapter", i + 1),
                "ChapterNumber": entry.get("ChapterNumber", ""),
                "Name": entry.get("Name", f"Unit {i + 1}"),
                "ChapterName": entry.get("ChapterName", entry.get("Name", f"Unit {i + 1}")),
                "Completion": entry.get("Completion", ""),
                "Summary": entry.get("Summary", ""),
                "Blurb": entry.get("Blurb", ""),
                "SceneCount": entry.get("Scenes", 0),
                "POV": entry.get("POV", []),
                "IDs": entry.get("IDs", []),
                "Settings": entry.get("Settings", []),
                "WCs": entry.get("WCs", []),
                "History": entry.get("History", {}),
                "Written": entry.get("Written", True),
    
                # Body-derived helpers
                "Excerpt": self._extract_excerpt(entry),
                "SettingText": self._extract_setting_text(entry),
                "POVText": self._extract_pov_text(entry),
                "ShortLabel": self._build_short_label(entry),
            }
    
            self.ADTX.append(row)

    def _extract_factors(self, entry: Dict[str, Any]) -> Tuple[float, float, float]:
        factors = entry.get("Factors", [])
        if not factors:
            return 0.0, 0.0, 0.0

        if isinstance(factors, (list, tuple)) and len(factors) == 3 and not isinstance(factors[0], (list, tuple)):
            return float(factors[0]), float(factors[1]), float(factors[2])

        triples = [f for f in factors if isinstance(f, (list, tuple)) and len(f) >= 3]
        if not triples:
            return 0.0, 0.0, 0.0

        if self.factor_mode == "mean":
            arr = np.array(triples, dtype=float)
            vals = arr.mean(axis=0)
            return float(vals[0]), float(vals[1]), float(vals[2])

        last = triples[-1]
        return float(last[0]), float(last[1]), float(last[2])

    def _extract_position(self, entry: Dict[str, Any]) -> float:
        wcs = entry.get("WCs", [])
        if isinstance(wcs, (list, tuple)) and len(wcs) > 0:
            return float(wcs[-1])
        return float(entry.get("Position", 0))

    def _extract_excerpt(self, entry: Dict[str, Any], max_chars: int = 180) -> str:
        body = entry.get("Body", [])
        for scene in body:
            for block in scene:
                if isinstance(block, (list, tuple)) and len(block) >= 2:
                    text = str(block[1]).strip()
                    if text and text != " ":
                        text = text.replace("&quot;", "\"").replace("&mdash;", "—").replace("&apos;", "'")
                        return text[:max_chars].strip() + ("…" if len(text) > max_chars else "")
        return ""

    def _extract_setting_text(self, entry: Dict[str, Any]) -> str:
        settings = entry.get("Settings", [])
        if not settings:
            return ""
        first = settings[0]
        if not isinstance(first, dict):
            return ""
        parts = [first.get("Region", ""), first.get("Area", ""), first.get("Location", ""), first.get("Date", "")]
        return " | ".join([p for p in parts if p])

    def _extract_pov_text(self, entry: Dict[str, Any]) -> str:
        pov = entry.get("POV", [])
        if isinstance(pov, list):
            unique = []
            for p in pov:
                if p not in unique:
                    unique.append(p)
            return ", ".join(unique)
        return str(pov)

    def _build_short_label(self, entry: Dict[str, Any]) -> str:
        chapter = entry.get("Chapter", "")
        name = entry.get("ChapterName", entry.get("Name", ""))
        return f"Ch {chapter}: {name}"

    def _sort_adtx(self) -> None:
        self.ADTX.sort(key=lambda row: float(row.get("Position", 0)))
        for i, row in enumerate(self.ADTX):
            row["Index"] = i + 1

    # ---------------------------------------------------------------------
    # Math utilities
    # ---------------------------------------------------------------------

    def _odd_window(self, window: int) -> int:
        window = max(1, int(window))
        return window if window % 2 == 1 else window + 1

    def _normalize_weights(self, weights: Tuple[float, ...]) -> Tuple[float, ...]:
        arr = np.array(weights, dtype=float)
        s = arr.sum()
        if s <= 0:
            arr = np.ones_like(arr) / len(arr)
        else:
            arr = arr / s
        return tuple(float(v) for v in arr)

    def _series(self, key: str) -> np.ndarray:
        return np.array([float(row.get(key, 0.0)) for row in self.ADTX], dtype=float)

    def _write_series(self, key: str, values: Iterable[float]) -> None:
        for row, value in zip(self.ADTX, values):
            row[key] = float(value)

    def _x(self) -> np.ndarray:
        x = self._series("Position").copy()
        if len(x) <= 1:
            return x
        for i in range(1, len(x)):
            if x[i] <= x[i - 1]:
                x[i] = x[i - 1] + 1.0
        return x

    def _minmax_norm(self, values: np.ndarray) -> np.ndarray:
        if len(values) == 0:
            return values
        lo = np.min(values)
        hi = np.max(values)
        if np.isclose(lo, hi):
            return np.zeros_like(values)
        return (values - lo) / (hi - lo)

    def _triangular_kernel(self, window: int) -> np.ndarray:
        window = self._odd_window(window)
        half = window // 2
        kernel = np.array([half + 1 - abs(i - half) for i in range(window)], dtype=float)
        kernel /= kernel.sum()
        return kernel

    def _weighted_moving_average(self, values: np.ndarray, window: int) -> np.ndarray:
        if len(values) == 0:
            return values
        if len(values) == 1:
            return values.copy()
        kernel = self._triangular_kernel(window)
        pad = len(kernel) // 2
        padded = np.pad(values, (pad, pad), mode="edge")
        return np.convolve(padded, kernel, mode="valid")

    def _local_baseline(self, values: np.ndarray, window: int) -> np.ndarray:
        n = len(values)
        if n <= 1:
            return values.copy()

        r = self._odd_window(window) // 2
        baseline = np.zeros_like(values, dtype=float)

        for i in range(n):
            lo = max(0, i - r)
            hi = min(n, i + r + 1)
            neighbors = np.delete(values[lo:hi], i - lo)
            baseline[i] = neighbors.mean() if len(neighbors) else values[i]

        return baseline

    def _derivative(self, values: np.ndarray) -> np.ndarray:
        if len(values) <= 1:
            return np.zeros_like(values)
        return np.gradient(values, self._x())

    def _cumulative_integral(self, values: np.ndarray) -> np.ndarray:
        out = np.zeros(len(values), dtype=float)
        if len(values) <= 1:
            return out
        x = self._x()
        total = 0.0
        for i in range(1, len(values)):
            dx = x[i] - x[i - 1]
            total += 0.5 * (values[i - 1] + values[i]) * dx
            out[i] = total
        return out

    # ---------------------------------------------------------------------
    # NK computations
    # ---------------------------------------------------------------------

    def compute_all_metrics(self) -> None:
        A = self._series("Action")
        D = self._series("Drama")
        T = self._series("Theme")
        E = A + D + T

        # Steady / transient
        As = self._weighted_moving_average(A, self.steady_window)
        Ds = self._weighted_moving_average(D, self.steady_window)
        Ts = self._weighted_moving_average(T, self.steady_window)
        Es = As + Ds + Ts

        At = A - As
        Dt = D - Ds
        Tt = T - Ts
        Et = E - Es

        # Derivatives
        dA = self._derivative(A)
        dD = self._derivative(D)
        dT = self._derivative(T)
        dE = self._derivative(E)

        # Cumulative
        cA = self._cumulative_integral(A)
        cD = self._cumulative_integral(D)
        cT = self._cumulative_integral(T)
        cE = self._cumulative_integral(E)

        # Mass / prominence / gravity
        M = self._weighted_moving_average(E, self.mass_window)
        MT = self._weighted_moving_average(T, self.mass_window)
        B = self._local_baseline(E, self.prominence_window)
        P = E - B

        En = self._minmax_norm(E)
        Mn = self._minmax_norm(M)
        MTn = self._minmax_norm(MT)
        Tn = self._minmax_norm(T)
        Pn = self._minmax_norm(P)

        gE, gM, gT = self.gravity_weights
        G = 100.0 * (gE * En + gM * Mn + gT * MTn)

        cT_w, cG_w, cP_w = self.cut_risk_weights
        Gn = self._minmax_norm(G)
        CutRisk = 100.0 * (
            cT_w * (1.0 - Tn) +
            cG_w * (1.0 - Gn) +
            cP_w * (1.0 - Pn)
        )

        computed = {
            "Energy": E,
            "ActionSteady": As,
            "DramaSteady": Ds,
            "ThemeSteady": Ts,
            "EnergySteady": Es,
            "ActionTransient": At,
            "DramaTransient": Dt,
            "ThemeTransient": Tt,
            "EnergyTransient": Et,
            "dAction": dA,
            "dDrama": dD,
            "dTheme": dT,
            "dEnergy": dE,
            "CumAction": cA,
            "CumDrama": cD,
            "CumTheme": cT,
            "CumEnergy": cE,
            "Mass": M,
            "ThemeMass": MT,
            "Baseline": B,
            "Prominence": P,
            "Gravity": G,
            "CutRisk": CutRisk,
        }

        for key, arr in computed.items():
            self._write_series(key, arr)

    # ---------------------------------------------------------------------
    # Context / annotation helpers
    # ---------------------------------------------------------------------

    def get_peak_rows(self, metric: str = "Gravity", n: int = 8) -> List[Dict[str, Any]]:
        return sorted(self.ADTX, key=lambda r: float(r.get(metric, 0.0)), reverse=True)[:n]

    def get_risky_rows(self, n: int = 8) -> List[Dict[str, Any]]:
        return sorted(self.ADTX, key=lambda r: float(r.get("CutRisk", 0.0)), reverse=True)[:n]

    def chapter_boundaries(self) -> List[Tuple[float, str]]:
        out = []
        seen = set()
        for row in self.ADTX:
            ch = row.get("Chapter")
            if ch not in seen:
                seen.add(ch)
                out.append((float(row.get("Position", 0.0)), f"Ch {ch}"))
        return out

    def chapter_summary_rows(self) -> List[Dict[str, Any]]:
        rows = []
        for row in self.ADTX:
            rows.append({
                "Index": row["Index"],
                "Act": row["Act"],
                "ActName": row["ActName"],
                "Chapter": row["Chapter"],
                "ChapterName": row["ChapterName"],
                "Position": row["Position"],
                "POV": row["POVText"],
                "Setting": row["SettingText"],
                "Scenes": row["SceneCount"],
                "Completion": row["Completion"],
                "Action": row["Action"],
                "Drama": row["Drama"],
                "Theme": row["Theme"],
                "Energy": row["Energy"],
                "Gravity": row["Gravity"],
                "Prominence": row["Prominence"],
                "CutRisk": row["CutRisk"],
                "Summary": row["Summary"],
                "Blurb": row["Blurb"],
                "Excerpt": row["Excerpt"],
            })
        return rows

    # ---------------------------------------------------------------------
    # Graphs
    # ---------------------------------------------------------------------

    def _annotate_top_peaks(self, ax, metric: str = "Gravity", count: Optional[int] = None) -> None:
        count = count or self.peak_annotate_count
        rows = self.get_peak_rows(metric=metric, n=count)

        for row in rows:
            x = float(row["Position"])
            y = float(row[metric])
            label = f"Ch {row['Chapter']} — {row['ChapterName']}"
            ax.annotate(
                label,
                xy=(x, y),
                xytext=(8, 8),
                textcoords="offset points",
                fontsize=8,
                alpha=0.85,
                arrowprops=dict(arrowstyle="-", lw=0.6, alpha=0.5),
            )

    def plot_adt(self, filepath: Optional[str] = None, annotate_peaks: bool = False):
        fig, ax = plt.subplots(figsize=(14, 6))
        x = self._x()

        ax.plot(x, self._series("Action"), color=self.COLORS["Action"], lw=2.1, label="Action")
        ax.plot(x, self._series("Drama"), color=self.COLORS["Drama"], lw=2.1, label="Drama")
        ax.plot(x, self._series("Theme"), color=self.COLORS["Theme"], lw=2.1, label="Theme")
        ax.plot(x, self._series("Energy"), color=self.COLORS["Energy"], lw=2.0, ls="--", label="Energy")

        for xb, lab in self.chapter_boundaries():
            ax.axvline(xb, color="gray", alpha=0.15, lw=0.6)

        if annotate_peaks:
            self._annotate_top_peaks(ax, metric="Energy")

        ax.set_title(f"{self.story_name} — ADT / Energy")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Score")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_energy_decomposition(self, filepath: Optional[str] = None, annotate_peaks: bool = True):
        fig, ax = plt.subplots(figsize=(14, 6))
        x = self._x()

        ax.plot(x, self._series("Energy"), color=self.COLORS["Energy"], lw=2.3, label="Energy")
        ax.plot(x, self._series("EnergySteady"), color=self.COLORS["Steady"], lw=1.9, label="Steady Energy")
        ax.plot(x, self._series("EnergyTransient"), color=self.COLORS["Transient"], lw=1.3, label="Transient Energy")

        for xb, _ in self.chapter_boundaries():
            ax.axvline(xb, color="gray", alpha=0.15, lw=0.6)

        if annotate_peaks:
            self._annotate_top_peaks(ax, metric="Energy")

        ax.set_title(f"{self.story_name} — Energy Decomposition")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Energy")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_gravity_metrics(self, filepath: Optional[str] = None, annotate_peaks: bool = True):
        fig, ax = plt.subplots(figsize=(14, 6))
        x = self._x()

        ax.plot(x, self._series("Gravity"), color=self.COLORS["Gravity"], lw=2.3, label="Narrative Gravity")
        ax.plot(x, self._series("Mass"), color=self.COLORS["Mass"], lw=1.7, label="Narrative Mass")
        ax.plot(x, self._series("ThemeMass"), color=self.COLORS["ThemeMass"], lw=1.7, label="Theme Mass")
        ax.plot(x, self._series("Prominence"), color=self.COLORS["Prominence"], lw=1.4, label="Peak Prominence")

        for xb, _ in self.chapter_boundaries():
            ax.axvline(xb, color="gray", alpha=0.15, lw=0.6)

        if annotate_peaks:
            self._annotate_top_peaks(ax, metric="Gravity")

        ax.set_title(f"{self.story_name} — Narrative Gravity / Mass / Prominence")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Metric")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_cumulative_loads(self, filepath: Optional[str] = None):
        fig, ax = plt.subplots(figsize=(14, 6))
        x = self._x()

        ax.plot(x, self._series("CumAction"), color=self.COLORS["Action"], lw=2.0, label="Cum Action")
        ax.plot(x, self._series("CumDrama"), color=self.COLORS["Drama"], lw=2.0, label="Cum Drama")
        ax.plot(x, self._series("CumTheme"), color=self.COLORS["Theme"], lw=2.0, label="Cum Theme")
        ax.plot(x, self._series("CumEnergy"), color=self.COLORS["Energy"], lw=2.2, label="Cum Energy")

        for xb, _ in self.chapter_boundaries():
            ax.axvline(xb, color="gray", alpha=0.15, lw=0.6)

        ax.set_title(f"{self.story_name} — Cumulative Narrative Load")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Integrated Load")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_cut_risk(self, filepath: Optional[str] = None):
        fig, ax = plt.subplots(figsize=(14, 5))
        x = self._x()

        ax.plot(x, self._series("CutRisk"), color=self.COLORS["CutRisk"], lw=2.1, label="Cut Risk")
        ax.plot(x, self._series("Theme"), color=self.COLORS["Theme"], lw=1.6, alpha=0.8, label="Theme")
        ax.plot(x, self._series("Gravity"), color=self.COLORS["Gravity"], lw=1.6, alpha=0.8, label="Gravity")

        risky = self.get_risky_rows(n=min(8, len(self.ADTX)))
        for row in risky:
            x0 = float(row["Position"])
            y0 = float(row["CutRisk"])
            ax.annotate(
                f"Ch {row['Chapter']}: {row['ChapterName']}",
                xy=(x0, y0),
                xytext=(8, 8),
                textcoords="offset points",
                fontsize=8,
                alpha=0.85,
                arrowprops=dict(arrowstyle="-", lw=0.6, alpha=0.5),
            )

        ax.set_title(f"{self.story_name} — Cut Risk Heuristic")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Cut Risk")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()

        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    # ---------------------------------------------------------------------
    # CSV exports
    # ---------------------------------------------------------------------

    def export_full_csv(self, filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

        rows = self.chapter_summary_rows()
        fields = list(rows[0].keys())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

        return filepath

    def export_top_peaks_csv(self, filepath: str, metric: str = "Gravity", n: int = 15) -> str:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        rows = self.get_peak_rows(metric=metric, n=n)

        fields = [
            "Index", "Act", "ActName", "Chapter", "ChapterName", "Position",
            "POVText", "SettingText", "Action", "Drama", "Theme", "Energy",
            "Mass", "ThemeMass", "Prominence", "Gravity", "CutRisk",
            "Summary", "Blurb", "Excerpt"
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fields})

        return filepath

    def export_cut_risk_csv(self, filepath: str, n: int = 15) -> str:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        rows = self.get_risky_rows(n=n)

        fields = [
            "Index", "Act", "ActName", "Chapter", "ChapterName", "Position",
            "POVText", "SettingText", "Action", "Drama", "Theme", "Energy",
            "Prominence", "Gravity", "CutRisk", "Summary", "Blurb", "Excerpt"
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fields})

        return filepath

    # ---------------------------------------------------------------------
    # PDF report
    # ---------------------------------------------------------------------

    def export_pdf_report(self, filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

        with PdfPages(filepath) as pdf:
            # Cover
            fig = plt.figure(figsize=(8.5, 11))
            fig.suptitle(f"{self.story_name}\nNarrative Kinematics Report", fontsize=18, y=0.97)

            energy = self._series("Energy")
            gravity = self._series("Gravity")

            peak_e = self.get_peak_rows("Energy", 1)[0]
            peak_g = self.get_peak_rows("Gravity", 1)[0]

            lines = [
                f"Units: {len(self.ADTX)}",
                f"Acts represented: {len(set(r['Act'] for r in self.ADTX if r['Act'] != ''))}",
                "",
                f"Mean Action:   {self._series('Action').mean():.2f}",
                f"Mean Drama:    {self._series('Drama').mean():.2f}",
                f"Mean Theme:    {self._series('Theme').mean():.2f}",
                f"Mean Energy:   {energy.mean():.2f}",
                f"Mean Gravity:  {gravity.mean():.2f}",
                "",
                f"Peak Energy:   Ch {peak_e['Chapter']} — {peak_e['ChapterName']}",
                f"Peak Gravity:  Ch {peak_g['Chapter']} — {peak_g['ChapterName']}",
                "",
                "Top Gravity Context:",
                f"Summary: {peak_g.get('Summary', '')}",
                f"Blurb:   {peak_g.get('Blurb', '')}",
                f"Setting: {peak_g.get('SettingText', '')}",
                f"POV:     {peak_g.get('POVText', '')}",
                "",
                "Gravity = normalized blend of Energy, local Mass, and ThemeMass.",
            ]

            fig.text(0.08, 0.90, "\n".join(lines), va="top", fontsize=10.5, family="monospace")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

            # Graph pages
            for fn in (
                self.plot_adt,
                self.plot_energy_decomposition,
                self.plot_gravity_metrics,
                self.plot_cumulative_loads,
                self.plot_cut_risk,
            ):
                fig = fn()
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

            # Top peaks text page
            fig = plt.figure(figsize=(8.5, 11))
            fig.suptitle("Top Narrative Gravity Peaks", fontsize=16, y=0.97)

            blocks = []
            for row in self.get_peak_rows("Gravity", n=min(8, len(self.ADTX))):
                blocks.append(
                    f"Ch {row['Chapter']} — {row['ChapterName']}\n"
                    f"Gravity: {row['Gravity']:.2f} | Energy: {row['Energy']:.2f}\n"
                    f"POV: {row['POVText']}\n"
                    f"Setting: {row['SettingText']}\n"
                    f"Summary: {row['Summary']}\n"
                    f"Blurb: {row['Blurb']}\n"
                    f"Excerpt: {row['Excerpt']}\n"
                )

            fig.text(0.06, 0.94, "\n".join(blocks), va="top", fontsize=8.5)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

            # Cut risk text page
            fig = plt.figure(figsize=(8.5, 11))
            fig.suptitle("Highest Cut-Risk Units", fontsize=16, y=0.97)

            blocks = []
            for row in self.get_risky_rows(n=min(8, len(self.ADTX))):
                blocks.append(
                    f"Ch {row['Chapter']} — {row['ChapterName']}\n"
                    f"CutRisk: {row['CutRisk']:.2f} | Theme: {row['Theme']:.2f} | Gravity: {row['Gravity']:.2f}\n"
                    f"Summary: {row['Summary']}\n"
                    f"Blurb: {row['Blurb']}\n"
                    f"Excerpt: {row['Excerpt']}\n"
                )

            fig.text(0.06, 0.94, "\n".join(blocks), va="top", fontsize=8.5)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        return filepath

    # ---------------------------------------------------------------------
    # Bundle export
    # ---------------------------------------------------------------------

    def export_report_bundle(self, outdir: Optional[str] = None) -> Dict[str, str]:
        outdir = outdir or self.outdir
        os.makedirs(outdir, exist_ok=True)

        stem = self.story_name.lower().replace(" ", "_")

        paths = {
            "full_csv": os.path.join(outdir, f"{stem}_nk_full.csv"),
            "peaks_csv": os.path.join(outdir, f"{stem}_nk_top_peaks.csv"),
            "cut_csv": os.path.join(outdir, f"{stem}_nk_cut_risk.csv"),
            "pdf_report": os.path.join(outdir, f"{stem}_nk_report.pdf"),
            "adt_png": os.path.join(outdir, f"{stem}_nk_adt.png"),
            "energy_png": os.path.join(outdir, f"{stem}_nk_energy.png"),
            "gravity_png": os.path.join(outdir, f"{stem}_nk_gravity.png"),
            "cumulative_png": os.path.join(outdir, f"{stem}_nk_cumulative.png"),
            "cutrisk_png": os.path.join(outdir, f"{stem}_nk_cutrisk.png"),
        }

        self.export_full_csv(paths["full_csv"])
        self.export_top_peaks_csv(paths["peaks_csv"])
        self.export_cut_risk_csv(paths["cut_csv"])
        self.export_pdf_report(paths["pdf_report"])
        self.plot_adt(paths["adt_png"], annotate_peaks=True)
        self.plot_energy_decomposition(paths["energy_png"], annotate_peaks=True)
        self.plot_gravity_metrics(paths["gravity_png"], annotate_peaks=True)
        self.plot_cumulative_loads(paths["cumulative_png"])
        self.plot_cut_risk(paths["cutrisk_png"])

        return paths
    
    def _html(self, value: Any) -> str:
        if value is None:
            return ""
        return escape(str(value))
    
    def _slug(self, text: str) -> str:
        cleaned = []
        for ch in str(text).lower():
            if ch.isalnum():
                cleaned.append(ch)
            elif ch in (" ", "-", "_"):
                cleaned.append("_")
        return "".join(cleaned).strip("_") or "story_nk"
    
    def _summary_dict(self) -> Dict[str, Any]:
        A = self._series("Action")
        D = self._series("Drama")
        T = self._series("Theme")
        E = self._series("Energy")
        G = self._series("Gravity")
        C = self._series("CutRisk")
    
        peak_e = self.get_peak_rows("Energy", 1)[0] if self.ADTX else {}
        peak_g = self.get_peak_rows("Gravity", 1)[0] if self.ADTX else {}
        peak_c = self.get_risky_rows(1)[0] if self.ADTX else {}
    
        return {
            "story": self.story_name,
            "units": len(self.ADTX),
            "start_position": float(self._x()[0]) if len(self.ADTX) else 0.0,
            "end_position": float(self._x()[-1]) if len(self.ADTX) else 0.0,
            "mean_action": float(A.mean()) if len(A) else 0.0,
            "mean_drama": float(D.mean()) if len(D) else 0.0,
            "mean_theme": float(T.mean()) if len(T) else 0.0,
            "mean_energy": float(E.mean()) if len(E) else 0.0,
            "mean_gravity": float(G.mean()) if len(G) else 0.0,
            "mean_cutrisk": float(C.mean()) if len(C) else 0.0,
            "peak_energy": peak_e,
            "peak_gravity": peak_g,
            "peak_cutrisk": peak_c,
        }
    
    def _report_image_paths(self, outdir: str) -> Dict[str, str]:
        stem = self._slug(self.story_name)
        return {
            "adt": os.path.join(outdir, f"{stem}_nk_adt.png"),
            "energy": os.path.join(outdir, f"{stem}_nk_energy.png"),
            "gravity": os.path.join(outdir, f"{stem}_nk_gravity.png"),
            "cumulative": os.path.join(outdir, f"{stem}_nk_cumulative.png"),
            "cutrisk": os.path.join(outdir, f"{stem}_nk_cutrisk.png"),
        }
    
    def _export_graph_images_for_report(self, outdir: str) -> Dict[str, str]:
        os.makedirs(outdir, exist_ok=True)
        paths = self._report_image_paths(outdir)
    
        self.plot_adt(paths["adt"], annotate_peaks=True)
        self.plot_energy_decomposition(paths["energy"], annotate_peaks=True)
        self.plot_gravity_metrics(paths["gravity"], annotate_peaks=True)
        self.plot_cumulative_loads(paths["cumulative"])
        self.plot_cut_risk(paths["cutrisk"])
    
        return paths
    
    def _html_peak_block(self, row: Dict[str, Any], metric: str) -> str:
        return f"""
        <div class="peak-card">
            <div class="peak-title">Ch {self._html(row.get("Chapter", ""))} — {self._html(row.get("ChapterName", ""))}</div>
            <div class="peak-meta">
                <strong>{self._html(metric)}:</strong> {float(row.get(metric, 0.0)):.2f}
                &nbsp; | &nbsp;
                <strong>Energy:</strong> {float(row.get("Energy", 0.0)):.2f}
                &nbsp; | &nbsp;
                <strong>POV:</strong> {self._html(row.get("POVText", ""))}
            </div>
            <div class="peak-meta"><strong>Setting:</strong> {self._html(row.get("SettingText", ""))}</div>
            <div class="peak-summary"><strong>Summary:</strong> {self._html(row.get("Summary", ""))}</div>
            <div class="peak-summary"><strong>Blurb:</strong> {self._html(row.get("Blurb", ""))}</div>
            <div class="peak-excerpt">{self._html(row.get("Excerpt", ""))}</div>
        </div>
        """
    
    def _html_table_rows(self, rows: List[Dict[str, Any]]) -> str:
        cells = []
        for row in rows:
            cells.append(
                f"""
                <tr>
                    <td>{self._html(row.get("Chapter", ""))}</td>
                    <td>{self._html(row.get("ChapterName", ""))}</td>
                    <td>{float(row.get("Action", 0.0)):.1f}</td>
                    <td>{float(row.get("Drama", 0.0)):.1f}</td>
                    <td>{float(row.get("Theme", 0.0)):.1f}</td>
                    <td>{float(row.get("Energy", 0.0)):.1f}</td>
                    <td>{float(row.get("Gravity", 0.0)):.1f}</td>
                    <td>{float(row.get("CutRisk", 0.0)):.1f}</td>
                    <td>{self._html(row.get("POVText", ""))}</td>
                    <td>{self._html(row.get("Summary", ""))}</td>
                </tr>
                """
            )
        return "\n".join(cells)
    
    def build_html_report(
        self,
        html_path: str,
        image_paths: Optional[Dict[str, str]] = None,
        title: Optional[str] = None,
        diagnosis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build a styled HTML report for browser rendering / Playwright PDF export.
        """
        outdir = os.path.dirname(html_path) or "."
        os.makedirs(outdir, exist_ok=True)
    
        if image_paths is None:
            image_paths = self._export_graph_images_for_report(outdir)
    
        summary = self._summary_dict()
        top_gravity = self.get_peak_rows("Gravity", n=min(8, len(self.ADTX)))
        top_energy = self.get_peak_rows("Energy", n=min(6, len(self.ADTX)))
        top_cutrisk = self.get_risky_rows(n=min(8, len(self.ADTX)))
    
        table_rows = self.chapter_summary_rows()
    
        def rel(path: str) -> str:
            return os.path.relpath(path, start=outdir).replace("\\", "/")
    
        html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <title>{self._html(title or f"{self.story_name} — Narrative Kinematics Report")}</title>
    <style>
    @page {{
        size: Letter;
        margin: 0.65in 0.7in 0.75in 0.7in;
    }}
    
    html, body {{
        margin: 0;
        padding: 0;
        background: #ffffff;
        color: #222;
        font-family: "Georgia", "Times New Roman", serif;
    }}
    
    body {{
        font-size: 11pt;
        line-height: 1.45;
    }}
    
    .report {{
        width: 100%;
    }}
    
    .page-break {{
        break-before: page;
        page-break-before: always;
    }}
    
    h1, h2, h3 {{
        margin: 0 0 0.35em 0;
        line-height: 1.2;
    }}
    
    h1 {{
        font-size: 24pt;
    }}
    
    h2 {{
        font-size: 16pt;
        margin-top: 1.2rem;
        border-bottom: 1px solid #ddd;
        padding-bottom: 0.2rem;
    }}
    
    h3 {{
        font-size: 12.5pt;
        margin-top: 1rem;
    }}
    
    p {{
        margin: 0 0 0.7rem 0;
    }}
    
    .small {{
        font-size: 9pt;
        color: #666;
    }}
    
    .meta-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem 1rem;
        margin: 1rem 0 1.2rem 0;
    }}
    
    .meta-card {{
        border: 1px solid #ddd;
        background: #fafafa;
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
    }}
    
    .callout {{
        border-left: 4px solid #3A6EA5;
        background: #f4f8fc;
        padding: 0.8rem 0.9rem;
        border-radius: 0.2rem;
        margin: 1rem 0 1.2rem 0;
    }}
    
    .figure {{
        margin: 1rem 0 1.4rem 0;
        break-inside: avoid;
        page-break-inside: avoid;
    }}
    
    .figure img {{
        display: block;
        width: 100%;
        max-width: 100%;
        height: auto;
        border: 1px solid #ddd;
        box-sizing: border-box;
    }}
    
    .caption {{
        margin-top: 0.35rem;
        font-size: 9.5pt;
        color: #555;
    }}
    
    .peak-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.8rem;
    }}
    
    .peak-card {{
        border: 1px solid #dcdcdc;
        border-radius: 8px;
        padding: 0.75rem 0.85rem;
        break-inside: avoid;
        page-break-inside: avoid;
    }}
    
    .peak-title {{
        font-weight: bold;
        font-size: 12pt;
        margin-bottom: 0.2rem;
    }}
    
    .peak-meta {{
        font-size: 9.5pt;
        color: #555;
        margin-bottom: 0.3rem;
    }}
    
    .peak-summary {{
        margin-top: 0.25rem;
    }}
    
    .peak-excerpt {{
        margin-top: 0.45rem;
        font-style: italic;
        color: #444;
    }}
    
    table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 9.5pt;
    }}
    
    th, td {{
        border: 1px solid #d8d8d8;
        padding: 0.45rem 0.5rem;
        vertical-align: top;
        text-align: left;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}
    
    th {{
        background: #f0f2f5;
    }}
    
    .col-num {{
        width: 6%;
    }}
    
    .col-name {{
        width: 14%;
    }}
    
    .col-score {{
        width: 6%;
    }}
    
    .col-pov {{
        width: 10%;
    }}
    
    .col-summary {{
        width: 34%;
    }}
    </style>
    </head>
    <body>
    <div class="report">
    
        <h1>{self._html(title or f"{self.story_name} — Narrative Kinematics Report")}</h1>
        <p class="small">Generated from manuscript ADT data using the StoryNK model.</p>
    
        <div class="meta-grid">
            <div class="meta-card"><strong>Story</strong><br>{self._html(summary["story"])}</div>
            <div class="meta-card"><strong>Units</strong><br>{summary["units"]}</div>
            <div class="meta-card"><strong>Position Span</strong><br>{summary["start_position"]:,.0f} - {summary["end_position"]:,.0f}</div>
            <div class="meta-card"><strong>Mean Energy</strong><br>{summary["mean_energy"]:.2f}</div>
            <div class="meta-card"><strong>Mean Gravity</strong><br>{summary["mean_gravity"]:.2f}</div>
            <div class="meta-card"><strong>Mean Cut Risk</strong><br>{summary["mean_cutrisk"]:.2f}</div>
        </div>
    
        <div class="callout">
            <strong>Peak Energy:</strong>
            Ch {self._html(summary["peak_energy"].get("Chapter", ""))} —
            {self._html(summary["peak_energy"].get("ChapterName", ""))}
            <br>
            <strong>Peak Gravity:</strong>
            Ch {self._html(summary["peak_gravity"].get("Chapter", ""))} —
            {self._html(summary["peak_gravity"].get("ChapterName", ""))}
            <br>
            <strong>Highest Cut Risk:</strong>
            Ch {self._html(summary["peak_cutrisk"].get("Chapter", ""))} —
            {self._html(summary["peak_cutrisk"].get("ChapterName", ""))}
        </div>
    
        <h2>System Overview</h2>
        <p>
            Action, Drama, and Theme define the primary narrative state. Energy is their sum. Steady-state and transient
            tracks approximate long-wave baseline versus local fluctuation. Narrative Mass, Peak Prominence, and Narrative Gravity
            estimate which regions are merely loud versus which ones are actually load-bearing.
        </p>
    
        <div class="figure">
            <img src="{self._html(rel(image_paths["adt"]))}" alt="ADT plot">
            <div class="caption">Action, Drama, Theme, and Energy across cumulative story position.</div>
        </div>
    
        <div class="figure">
            <img src="{self._html(rel(image_paths["energy"]))}" alt="Energy decomposition">
            <div class="caption">Composite Energy versus steady-state and transient energy behavior.</div>
        </div>
    
        <div class="figure">
            <img src="{self._html(rel(image_paths["gravity"]))}" alt="Gravity metrics">
            <div class="caption">Narrative Gravity, Mass, Theme Mass, and Peak Prominence.</div>
        </div>
    
        <div class="figure">
            <img src="{self._html(rel(image_paths["cumulative"]))}" alt="Cumulative loads">
            <div class="caption">Cumulative action, drama, theme, and energy load.</div>
        </div>
    
        <div class="figure">
            <img src="{self._html(rel(image_paths["cutrisk"]))}" alt="Cut risk plot">
            <div class="caption">Cut-risk heuristic versus theme and gravity.</div>
        </div>
    
        <div class="page-break"></div>
    
        <h2>Top Gravity Peaks</h2>
        <div class="peak-grid">
            {''.join(self._html_peak_block(row, "Gravity") for row in top_gravity)}
        </div>
    
        <div class="page-break"></div>
    
        <h2>Top Energy Peaks</h2>
        <div class="peak-grid">
            {''.join(self._html_peak_block(row, "Energy") for row in top_energy)}
        </div>
    
        <div class="page-break"></div>
    
        <h2>Highest Cut-Risk Units</h2>
        <div class="peak-grid">
            {''.join(self._html_peak_block(row, "CutRisk") for row in top_cutrisk)}
        </div>
        
        {self._html_llm_diagnosis_section(diagnosis)}
    
        <div class="page-break"></div>
    
        <h2>Full Chapter / Unit Table</h2>
        <table>
            <thead>
                <tr>
                    <th class="col-num">Ch</th>
                    <th class="col-name">Chapter</th>
                    <th class="col-score">A</th>
                    <th class="col-score">D</th>
                    <th class="col-score">T</th>
                    <th class="col-score">E</th>
                    <th class="col-score">G</th>
                    <th class="col-score">Cut</th>
                    <th class="col-pov">POV</th>
                    <th class="col-summary">Summary</th>
                </tr>
            </thead>
            <tbody>
                {self._html_table_rows(table_rows)}
            </tbody>
        </table>
    
    </div>
    </body>
    </html>
    """
    
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
    
        return html_path
    
    def export_playwright_pdf_report(
        self,
        pdf_path: str,
        html_path: Optional[str] = None,
        image_paths: Optional[Dict[str, str]] = None,
        title: Optional[str] = None,
        paper: str = "Letter",
        landscape: bool = False,
    ) -> str:
        return self._run_async_in_thread(
            self.export_playwright_pdf_report_async(
                pdf_path=pdf_path,
                html_path=html_path,
                image_paths=image_paths,
                title=title,
                paper=paper,
                landscape=landscape,
            )
        )
    
    async def export_playwright_pdf_report_async(
        self,
        pdf_path: str,
        html_path: Optional[str] = None,
        image_paths: Optional[Dict[str, str]] = None,
        title: Optional[str] = None,
        paper: str = "Letter",
        landscape: bool = False,
        diagnosis: Optional[Dict[str, Any]] = None,
        rebuild_html: bool = True,
    ) -> str:
        outdir = os.path.dirname(pdf_path) or "."
        os.makedirs(outdir, exist_ok=True)
        
        if html_path is None:
            html_path = os.path.join(outdir, f"{self._slug(self.story_name)}_nk_report.html")
        
        if image_paths is None:
            image_paths = self._export_graph_images_for_report(outdir)
        
        if rebuild_html:
            self.build_html_report(
                html_path=html_path,
                image_paths=image_paths,
                title=title,
                diagnosis=diagnosis,
            )
    
        html_file = Path(html_path).resolve().as_uri()
    
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(html_file, wait_until="networkidle")
            await page.emulate_media(media="print")
    
            await page.pdf(
                path=pdf_path,
                format=paper,
                landscape=landscape,
                print_background=True,
                margin={
                    "top": "0.65in",
                    "right": "0.7in",
                    "bottom": "0.75in",
                    "left": "0.7in",
                },
                prefer_css_page_size=True,
            )
    
            await browser.close()
    
        return pdf_path
    
    async def export_html_report_bundle_async(
        self,
        outdir: Optional[str] = None,
        include_llm_diagnosis: bool = False,
        api_key: Optional[str] = None,
        model: str = "gpt-5.4",
        extra_instruction: Optional[str] = None,
    ) -> Dict[str, str]:
        outdir = outdir or self.outdir
        os.makedirs(outdir, exist_ok=True)
    
        stem = self._slug(self.story_name)
    
        image_paths = self._export_graph_images_for_report(outdir)
    
        full_csv = os.path.join(outdir, f"{stem}_nk_full.csv")
        peaks_csv = os.path.join(outdir, f"{stem}_nk_top_peaks.csv")
        cut_csv = os.path.join(outdir, f"{stem}_nk_cut_risk.csv")
        html_report = os.path.join(outdir, f"{stem}_nk_report.html")
        pdf_report = os.path.join(outdir, f"{stem}_nk_report.pdf")
        diagnosis_json = os.path.join(outdir, f"{stem}_nk_llm_diagnosis.json")
    
        self.export_full_csv(full_csv)
        self.export_top_peaks_csv(peaks_csv)
        self.export_cut_risk_csv(cut_csv)
    
        diagnosis = None
        if include_llm_diagnosis:
            diagnosis = self.query_openai_diagnosis(
                api_key=api_key,
                model=model,
                save_json_path=diagnosis_json,
                extra_instruction=extra_instruction,
            )
    
        self.build_html_report(
            html_path=html_report,
            image_paths=image_paths,
            title=f"{self.story_name} — Narrative Kinematics Report",
            diagnosis=diagnosis,
        )
    
        await self.export_playwright_pdf_report_async(
            pdf_path=pdf_report,
            html_path=html_report,
            image_paths=image_paths,
            title=f"{self.story_name} — Narrative Kinematics Report",
            diagnosis=diagnosis,
            rebuild_html=False,
        )
    
        out = {
            "full_csv": full_csv,
            "peaks_csv": peaks_csv,
            "cut_csv": cut_csv,
            "html_report": html_report,
            "pdf_report": pdf_report,
            **image_paths,
        }
    
        if include_llm_diagnosis:
            out["diagnosis_json"] = diagnosis_json
    
        return out
    
    def export_html_report_bundle(
        self,
        outdir: Optional[str] = None,
        include_llm_diagnosis: bool = False,
        api_key: Optional[str] = None,
        model: str = "gpt-5.4",
        extra_instruction: Optional[str] = None,
    ) -> Dict[str, str]:
        return self._run_async_in_thread(
            self.export_html_report_bundle_async(
                outdir=outdir,
                include_llm_diagnosis=include_llm_diagnosis,
                api_key=api_key,
                model=model,
                extra_instruction=extra_instruction,
            )
        )

    def _run_async_in_thread(self, coro):
        """
        Spyder/IPython-safe bridge:
        runs an async coroutine in a separate thread with its own explicit event loop.
        """
        import asyncio
        import threading
    
        result = {"value": None, "error": None}
    
        def runner():
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                result["value"] = loop.run_until_complete(coro)
            except Exception as e:
                result["error"] = e
            finally:
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
                except Exception:
                    pass
                finally:
                    asyncio.set_event_loop(None)
                    loop.close()
    
        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join()
    
        if result["error"] is not None:
            raise result["error"]
    
        return result["value"]
    
    def _llm_safe_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reduce a full ADTX row into a compact JSON-safe payload for model analysis.
        """
        return {
            "index": int(row.get("Index", 0)),
            "chapter": row.get("Chapter", ""),
            "chapter_name": row.get("ChapterName", row.get("Name", "")),
            "act": row.get("Act", ""),
            "act_name": row.get("ActName", ""),
            "position": float(row.get("Position", 0.0)),
            "action": float(row.get("Action", 0.0)),
            "drama": float(row.get("Drama", 0.0)),
            "theme": float(row.get("Theme", 0.0)),
            "energy": float(row.get("Energy", 0.0)),
            "gravity": float(row.get("Gravity", 0.0)),
            "prominence": float(row.get("Prominence", 0.0)),
            "mass": float(row.get("Mass", 0.0)),
            "theme_mass": float(row.get("ThemeMass", 0.0)),
            "cut_risk": float(row.get("CutRisk", 0.0)),
            "pov": row.get("POVText", ""),
            "setting": row.get("SettingText", ""),
            "summary": row.get("Summary", ""),
            "blurb": row.get("Blurb", ""),
            "excerpt": row.get("Excerpt", ""),
        }
    
    
    def build_llm_payload(
        self,
        top_n: int = 12,
        sample_n: int = 12,
    ) -> Dict[str, Any]:
        """
        Build a compact structured payload for LLM diagnosis.
        """
        summary = self._summary_dict()
    
        # Full unit list, reduced
        unit_rows = [self._llm_safe_row(row) for row in self.ADTX]
    
        # Top slices
        top_gravity = [self._llm_safe_row(r) for r in self.get_peak_rows("Gravity", n=min(top_n, len(self.ADTX)))]
        top_energy = [self._llm_safe_row(r) for r in self.get_peak_rows("Energy", n=min(top_n, len(self.ADTX)))]
        top_cut_risk = [self._llm_safe_row(r) for r in self.get_risky_rows(n=min(top_n, len(self.ADTX)))]
    
        # Evenly sampled rows across the whole manuscript
        sampled_units = []
        if len(unit_rows) <= sample_n:
            sampled_units = unit_rows
        else:
            idxs = np.linspace(0, len(unit_rows) - 1, sample_n, dtype=int)
            sampled_units = [unit_rows[i] for i in idxs]
    
        # Chapter / unit summary table
        chapter_table = []
        for row in self.chapter_summary_rows():
            chapter_table.append({
                "index": int(row.get("Index", 0)),
                "chapter": row.get("Chapter", ""),
                "chapter_name": row.get("ChapterName", ""),
                "act": row.get("Act", ""),
                "act_name": row.get("ActName", ""),
                "position": float(row.get("Position", 0.0)),
                "action": float(row.get("Action", 0.0)),
                "drama": float(row.get("Drama", 0.0)),
                "theme": float(row.get("Theme", 0.0)),
                "energy": float(row.get("Energy", 0.0)),
                "gravity": float(row.get("Gravity", 0.0)),
                "prominence": float(row.get("Prominence", 0.0)),
                "cut_risk": float(row.get("CutRisk", 0.0)),
                "pov": row.get("POV", ""),
                "setting": row.get("Setting", ""),
                "summary": row.get("Summary", ""),
                "blurb": row.get("Blurb", ""),
                "excerpt": row.get("Excerpt", ""),
            })
    
        payload = {
            "story_name": self.story_name,
            "unit_count": len(self.ADTX),
            "metrics_summary": summary,
            "gravity_weights": list(self.gravity_weights),
            "cut_risk_weights": list(self.cut_risk_weights),
            "top_gravity": top_gravity,
            "top_energy": top_energy,
            "top_cut_risk": top_cut_risk,
            "sampled_units": sampled_units,
            "chapter_table": chapter_table,
        }
    
        return payload
    
    
    def query_openai_diagnosis(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-5.4",
        save_json_path: Optional[str] = None,
        extra_instruction: Optional[str] = None,
        top_n: int = 12,
        sample_n: int = 12,
    ) -> Dict[str, Any]:
        """
        Query OpenAI for a structured revision diagnosis of the manuscript.
    
        Returns a strict JSON dict.
        """
        client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    
        payload = self.build_llm_payload(top_n=top_n, sample_n=sample_n)
    
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "macro_assessment": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "length_assessment": {"type": "string"},
                        "structural_health": {"type": "string"},
                        "primary_strength": {"type": "string"},
                        "primary_risk": {"type": "string"},
                        "one_paragraph_verdict": {"type": "string"},
                    },
                    "required": [
                        "length_assessment",
                        "structural_health",
                        "primary_strength",
                        "primary_risk",
                        "one_paragraph_verdict",
                    ],
                },
                "strongest_regions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "chapter": {"type": "integer"},
                            "chapter_name": {"type": "string"},
                            "reason": {"type": "string"},
                            "revision_instruction": {"type": "string"},
                        },
                        "required": ["chapter", "chapter_name", "reason", "revision_instruction"],
                    },
                },
                "drag_corridors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "start_chapter": {"type": "integer"},
                            "end_chapter": {"type": "integer"},
                            "problem_type": {"type": "string"},
                            "reason": {"type": "string"},
                            "suggested_fix": {"type": "string"},
                            "confidence": {"type": "number"},
                        },
                        "required": [
                            "start_chapter",
                            "end_chapter",
                            "problem_type",
                            "reason",
                            "suggested_fix",
                            "confidence",
                        ],
                    },
                },
                "cut_candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "chapter": {"type": "integer"},
                            "chapter_name": {"type": "string"},
                            "cut_risk_reason": {"type": "string"},
                            "suggested_action": {
                                "type": "string",
                                "enum": ["keep", "trim", "compress_hard", "merge", "differentiate"],
                            },
                            "what_to_target": {"type": "string"},
                        },
                        "required": [
                            "chapter",
                            "chapter_name",
                            "cut_risk_reason",
                            "suggested_action",
                            "what_to_target",
                        ],
                    },
                },
                "protect_at_all_costs": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
                "chapter_notes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "chapter": {"type": "integer"},
                            "chapter_name": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["protect", "keep", "trim", "compress_hard", "differentiate"],
                            },
                            "note": {"type": "string"},
                        },
                        "required": ["chapter", "chapter_name", "status", "note"],
                    },
                },
                "next_revision_pass": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "final_remarks": {
                    "type": "string"
                }
            },
            "required": [
                "macro_assessment",
                "strongest_regions",
                "drag_corridors",
                "cut_candidates",
                "protect_at_all_costs",
                "chapter_notes",
                "next_revision_pass",
            ],
        }
    
        developer_prompt = (
            "You are a rigorous developmental editor analyzing a narrative using a quantitative "
            "Narrative Kinematics dataset. Use the provided metrics as evidence, but do not treat "
            "them as infallible. Look for: structural peaks, likely drag corridors, low-theme / "
            "high-drama melodrama risk, low-theme / high-action cheap-action risk, overlong spans, "
            "and chapters that should be protected. Prefer blunt, useful revision guidance over praise. "
            "Do not invent chapters or facts not present in the payload."
        )
    
        if extra_instruction:
            developer_prompt += f"\n\nAdditional instruction:\n{extra_instruction}"
    
        user_prompt = (
            "Analyze the following StoryNK payload and return a structured revision diagnosis.\n\n"
            f"{json.dumps(payload, ensure_ascii=False)}"
        )
    
        response = client.responses.create(
            model=model,
            input=[
                {"role": "developer", "content": developer_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "story_nk_diagnosis",
                    "strict": True,
                    "schema": schema,
                }
            },
        )
    
        diagnosis = json.loads(response.output_text)
    
        if save_json_path:
            os.makedirs(os.path.dirname(save_json_path) or ".", exist_ok=True)
            with open(save_json_path, "w", encoding="utf-8") as f:
                json.dump(diagnosis, f, indent=2, ensure_ascii=False)
    
        return diagnosis
        
    def _html_llm_list(self, items: List[str]) -> str:
        if not items:
            return "<p class='small'>None.</p>"
        return "<ul>" + "".join(f"<li>{self._html(item)}</li>" for item in items) + "</ul>"
    
    
    def _html_llm_regions(self, rows: List[Dict[str, Any]], title_key: str = "reason") -> str:
        if not rows:
            return "<p class='small'>None.</p>"
    
        blocks = []
        for row in rows:
            if "chapter" in row:
                heading = f"Ch {row.get('chapter', '')} — {row.get('chapter_name', '')}"
            else:
                heading = f"Ch {row.get('start_chapter', '')}–{row.get('end_chapter', '')}"
    
            meta = []
            if "problem_type" in row:
                meta.append(f"<strong>Problem:</strong> {self._html(row.get('problem_type', ''))}")
            if "confidence" in row:
                try:
                    meta.append(f"<strong>Confidence:</strong> {float(row.get('confidence', 0.0)):.2f}")
                except Exception:
                    pass
            if "suggested_action" in row:
                meta.append(f"<strong>Action:</strong> {self._html(row.get('suggested_action', ''))}")
    
            body_parts = []
            if title_key in row:
                body_parts.append(f"<div><strong>Reason:</strong> {self._html(row.get(title_key, ''))}</div>")
            if "suggested_fix" in row:
                body_parts.append(f"<div><strong>Suggested fix:</strong> {self._html(row.get('suggested_fix', ''))}</div>")
            if "what_to_target" in row:
                body_parts.append(f"<div><strong>Target:</strong> {self._html(row.get('what_to_target', ''))}</div>")
            if "revision_instruction" in row:
                body_parts.append(f"<div><strong>Revision instruction:</strong> {self._html(row.get('revision_instruction', ''))}</div>")
            if "note" in row:
                body_parts.append(f"<div><strong>Note:</strong> {self._html(row.get('note', ''))}</div>")
    
            blocks.append(
                f"""
                <div class="peak-card">
                    <div class="peak-title">{self._html(heading)}</div>
                    <div class="peak-meta">{' &nbsp; | &nbsp; '.join(meta) if meta else ''}</div>
                    {''.join(body_parts)}
                </div>
                """
            )
    
        return "\n".join(blocks)
    
    
    def _html_llm_diagnosis_section(self, diagnosis: Optional[Dict[str, Any]]) -> str:
        if not diagnosis:
            return """
            <h2><img src="/icons/OpenAI-black-monoblossom.png" style="width:100px; padding:40px;"> LLM Revision Diagnosis</h2>
            <p class="small">No LLM diagnosis was attached to this report.</p>
            """
    
        macro = diagnosis.get("macro_assessment", {})
        strongest = diagnosis.get("strongest_regions", [])
        drag = diagnosis.get("drag_corridors", [])
        cut_candidates = diagnosis.get("cut_candidates", [])
        protect = diagnosis.get("protect_at_all_costs", [])
        chapter_notes = diagnosis.get("chapter_notes", [])
        next_pass = diagnosis.get("next_revision_pass", [])
    
        protect_html = self._html_llm_list([f"Chapter {ch}" for ch in protect])
    
        return f"""
        <div class="page-break"></div>
    
        <h2>LLM Revision Diagnosis</h2>
    
        <div class="callout">
            <div><strong>Length assessment:</strong> {self._html(macro.get("length_assessment", ""))}</div>
            <div><strong>Structural health:</strong> {self._html(macro.get("structural_health", ""))}</div>
            <div><strong>Primary strength:</strong> {self._html(macro.get("primary_strength", ""))}</div>
            <div><strong>Primary risk:</strong> {self._html(macro.get("primary_risk", ""))}</div>
        </div>
    
        <p>{self._html(macro.get("one_paragraph_verdict", ""))}</p>
    
        <h3>Protect at All Costs</h3>
        {protect_html}
    
        <h3>Strongest Regions</h3>
        <div class="peak-grid">
            {self._html_llm_regions(strongest, title_key="reason")}
        </div>
    
        <h3>Drag Corridors</h3>
        <div class="peak-grid">
            {self._html_llm_regions(drag, title_key="reason")}
        </div>
    
        <h3>Cut Candidates</h3>
        <div class="peak-grid">
            {self._html_llm_regions(cut_candidates, title_key="cut_risk_reason")}
        </div>
    
        <h3>Chapter-by-Chapter Notes</h3>
        <div class="peak-grid">
            {self._html_llm_regions(chapter_notes, title_key="note")}
        </div>
    
        <h3>Next Revision Pass</h3>
        {self._html_llm_list(next_pass)}
        """
            