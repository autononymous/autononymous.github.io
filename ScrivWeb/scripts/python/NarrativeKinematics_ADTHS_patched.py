# -*- coding: utf-8 -*-
"""
Narrative Kinematics (ADTHS/M)

A revised StoryNK toolkit that expands the old ADTM model to support:
- Action, Drama, Theme, Heart, Sensuality, and Magnitude (M)
- Denotative, Connotative, and Total Energy
- Weighted layered energy plots (ADT bottom, H/S top)
- Premise alignment / force tracking
- HTML + PDF report export
- LLM-oriented aggregate payloads for downstream diagnosis

The public surface is intentionally similar to the older module so that
Scriv2WebNovel can keep instantiating StoryNK and calling
export_html_report_bundle() with minimal or no changes.
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
import threading
from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from playwright.async_api import async_playwright

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

import warnings
warnings.filterwarnings("ignore")


class StoryNK:
    COLORS = {
        "Action": "#c00000",
        "Drama": "#1f4e79",
        "Theme": "#38761d",
        "Heart": "#d4aa00",
        "Sensuality": "#ff66b3",
        "Magnitude": "#222222",
        "Denotative": "#555555",
        "Connotative": "#a64d79",
        "Total": "#000000",
        "Coupling": "#bbbbbb",
        "PremiseForce": "#444444",
        "PremiseLoad": "#7e57c2",
        "Mass": "#8c564b",
        "ThemeMass": "#2e8b57",
        "ConnotativeMass": "#b565a7",
        "Prominence": "#666666",
        "Gravity": "#6a0dad",
        "Steady": "#111111",
        "Transient": "#999999",
        "Compression": "#aa2222",
        "Indispensable": "#2f6f3e",
        "Conversion": "#8b5cf6",
        "Novelty": "#cc7a00",
        "CutRisk": "#aa2222",
    }

    def __init__(
        self,
        Manuscript,
        doReport: bool = False,
        story_name: Optional[str] = None,
        outdir: str = ".",
        factor_mode: str = "last",
        steady_window: int = 7,
        mass_window: int = 5,
        prominence_window: int = 5,
        gravity_weights: Sequence[float] = (0.4, 0.4, 0.2),
        cut_risk_weights: Optional[Sequence[float]] = None,
        compression_weights: Sequence[float] = (0.30, 0.25, 0.20, 0.20, 0.05),
        indispensability_weights: Sequence[float] = (0.35, 0.30, 0.20, 0.15),
        connotative_weights: Tuple[float, float] = (0.75, 0.25),
        total_energy_weights: Tuple[float, float] = (0.65, 0.35),
        coupling: float = 0.55,
        conversion_window: int = 7,
        peak_annotate_count: int = 8,
        field_distribution_bins: int = 12,
    ):
        self.outdir = str(outdir)
        self.doReport = bool(doReport)
        self.story_name = story_name or self._infer_story_name(Manuscript)

        self.factor_mode = factor_mode.lower().strip()
        self.steady_window = self._odd_window(steady_window)
        self.mass_window = self._odd_window(mass_window)
        self.prominence_window = self._odd_window(prominence_window)
        self.gravity_weights = self._normalize_weights(gravity_weights)
        self.compression_weights = self._normalize_weights(compression_weights)
        if cut_risk_weights is not None:
            legacy = tuple(float(v) for v in self._normalize_weights(cut_risk_weights))
            if len(legacy) == 3:
                self.compression_weights = self._normalize_weights((legacy[0], legacy[1], 0.15, 0.10, legacy[2]))
            else:
                self.compression_weights = self._normalize_weights(legacy)
        self.cut_risk_weights = self.compression_weights  # backward-compatible alias
        self.indispensability_weights = self._normalize_weights(indispensability_weights)
        self.connotative_weights = self._normalize_weights(connotative_weights)
        self.total_energy_weights = self._normalize_weights(total_energy_weights)
        self.coupling = float(coupling)
        self.conversion_window = self._odd_window(conversion_window)
        self.peak_annotate_count = int(peak_annotate_count)
        self.field_distribution_bins = max(6, int(field_distribution_bins))

        self.ADTX: List[Dict[str, Any]] = []
        self._ingest_manuscript(Manuscript)
        self._sort_adtx()
        self.compute_all_metrics()

        if self.doReport:
            self.export_report_bundle(self.outdir)

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def _infer_story_name(self, manuscript) -> str:
        entries = list(manuscript.values()) if hasattr(manuscript, "values") else list(manuscript)
        if not entries:
            return "Untitled Story"
        first = entries[0]
        if isinstance(first, dict):
            return str(first.get("Story", "Untitled Story"))
        return "Untitled Story"

    def _ingest_manuscript(self, manuscript) -> None:
        entries = list(manuscript.values()) if hasattr(manuscript, "values") else list(manuscript)
        if not entries:
            return

        raw_positions = [self._extract_position(entry) for entry in entries]
        fallback = self._estimate_fallback_scene_size(raw_positions)
        running_position = 0.0

        for i, (entry, raw_pos) in enumerate(zip(entries, raw_positions), start=1):
            action, drama, theme, heart, sensuality = self._extract_factors(entry)
            magnitude_raw = self._extract_magnitude(entry)
            magnitude = self._normalize_magnitude_value(magnitude_raw) if magnitude_raw is not None else 0.0

            effective_pos = max(float(raw_pos), fallback * 0.5)
            running_position += effective_pos

            row = {
                "Index": i,
                "Position": running_position,
                "RawPosition": float(raw_pos),
                "EffectivePosition": effective_pos,
                "Action": action,
                "Drama": drama,
                "Theme": theme,
                "Heart": heart,
                "Sensuality": sensuality,
                "Magnitude": magnitude,
                "MagnitudeRaw": float(magnitude_raw) if magnitude_raw is not None else 0.0,
                "HasMagnitude": magnitude_raw is not None,
                "Story": entry.get("Story", self.story_name),
                "Act": entry.get("Act", ""),
                "ActName": entry.get("ActName", ""),
                "Chapter": entry.get("Chapter", i),
                "ChapterNumber": entry.get("ChapterNumber", ""),
                "Name": entry.get("Name", f"Unit {i}"),
                "ChapterName": entry.get("ChapterName", entry.get("Name", f"Unit {i}")),
                "Completion": entry.get("Completion", ""),
                "Summary": entry.get("Summary", ""),
                "Blurb": entry.get("Blurb", ""),
                "SceneCount": entry.get("Scenes", 0),
                "POV": entry.get("POV", []),
                "IDs": entry.get("IDs", []),
                "Settings": entry.get("Settings", []),
                "WCs": entry.get("WCs", []),
                "History": entry.get("History", {}),
                "Written": bool(entry.get("Written", True)),
                "Excerpt": self._extract_excerpt(entry),
                "SettingText": self._extract_setting_text(entry),
                "POVText": self._extract_pov_text(entry),
                "ShortLabel": self._build_short_label(entry),
            }
            self.ADTX.append(row)

    def _estimate_fallback_scene_size(self, positions: Sequence[float]) -> float:
        valid = [float(p) for p in positions if float(p) > 350]
        if valid:
            return float(np.median(valid))
        positive = [float(p) for p in positions if float(p) > 0]
        if positive:
            return float(np.median(positive))
        return 1000.0

    def _extract_factors(self, entry: Dict[str, Any]) -> Tuple[float, float, float, float, float]:
        for key in ("NK_Params", "Factors"):
            quints = self._collect_factor_quints(entry.get(key))
            if quints:
                return self._reduce_factor_quints(quints)

        direct = self._factor_quint_from_mapping(entry)
        if direct is not None:
            return direct

        return 0.0, 0.0, 0.0, 0.0, 0.0

    def _extract_magnitude(self, entry: Dict[str, Any]) -> Optional[float]:
        for key in ("NK_Params", "Factors"):
            mags = self._collect_magnitudes(entry.get(key))
            if mags:
                return float(mags[-1]) if self.factor_mode == "last" else float(np.mean(mags))

        direct = self._magnitude_from_mapping(entry)
        return float(direct) if direct is not None else None

    def _collect_factor_quints(self, value: Any) -> List[Tuple[float, float, float, float, float]]:
        if value is None:
            return []

        if isinstance(value, dict):
            direct = self._factor_quint_from_mapping(value)
            if direct is not None:
                return [direct]

            out: List[Tuple[float, float, float, float, float]] = []
            for nested_key in ("NK_Params", "nk_params", "Factors", "factors", "factor", "scores"):
                if nested_key in value:
                    out.extend(self._collect_factor_quints(value.get(nested_key)))
            return out

        if isinstance(value, (list, tuple)):
            if len(value) >= 5 and all(self._is_number(v) for v in value[:5]):
                return [tuple(float(v) for v in value[:5])]  # type: ignore[return-value]
            if len(value) >= 3 and all(self._is_number(v) for v in value[:3]):
                # legacy ADTM triple -> ADTHS quint with H/S defaults 0
                return [(float(value[0]), float(value[1]), float(value[2]), 0.0, 0.0)]
            out: List[Tuple[float, float, float, float, float]] = []
            for item in value:
                out.extend(self._collect_factor_quints(item))
            return out

        return []

    def _reduce_factor_quints(self, quints: List[Tuple[float, float, float, float, float]]) -> Tuple[float, float, float, float, float]:
        if not quints:
            return 0.0, 0.0, 0.0, 0.0, 0.0
        if self.factor_mode == "mean":
            arr = np.array(quints, dtype=float)
            vals = arr.mean(axis=0)
            return tuple(float(v) for v in vals)
        return tuple(float(v) for v in quints[-1])

    def _factor_quint_from_mapping(self, obj: Dict[str, Any]) -> Optional[Tuple[float, float, float, float, float]]:
        action = self._pick_numeric(obj, ["Action", "action", "A", "a", "A_cal", "a_cal", "A_raw", "a_raw"])
        drama = self._pick_numeric(obj, ["Drama", "drama", "D", "d", "D_cal", "d_cal", "D_raw", "d_raw"])
        theme = self._pick_numeric(obj, ["Theme", "theme", "T", "t", "T_cal", "t_cal", "T_raw", "t_raw"])
        heart = self._pick_numeric(obj, ["Heart", "heart", "H", "h", "H_cal", "h_cal", "H_raw", "h_raw", "Moe", "moe"])
        sensuality = self._pick_numeric(obj, ["Sensuality", "sensuality", "S", "s", "S_cal", "s_cal", "S_raw", "s_raw", "Somatic", "somatic"])

        if action is None or drama is None or theme is None:
            return None
        return float(action), float(drama), float(theme), float(heart or 0.0), float(sensuality or 0.0)

    def _collect_magnitudes(self, value: Any) -> List[float]:
        if value is None:
            return []
        if isinstance(value, dict):
            direct = self._magnitude_from_mapping(value)
            if direct is not None:
                return [float(direct)]
            out: List[float] = []
            for nested_key in ("NK_Params", "nk_params", "Factors", "factors", "factor", "scores"):
                if nested_key in value:
                    out.extend(self._collect_magnitudes(value.get(nested_key)))
            return out
        if isinstance(value, (list, tuple)):
            if len(value) >= 6 and self._is_number(value[5]):
                return [float(value[5])]
            if len(value) >= 4 and self._is_number(value[3]) and len(value) < 6:
                # legacy ADTM [A, D, T, M]
                return [float(value[3])]
            out: List[float] = []
            for item in value:
                out.extend(self._collect_magnitudes(item))
            return out
        return []

    def _magnitude_from_mapping(self, obj: Dict[str, Any]) -> Optional[float]:
        return self._pick_numeric(
            obj,
            [
                "Magnitude", "magnitude", "M", "m",
                "Alignment", "alignment",
                "Vector", "vector", "V", "v",
                "PremiseMagnitude", "premise_magnitude",
                "PremiseAlignment", "premise_alignment",
                "MagnitudeRaw", "magnitude_raw",
            ],
        )

    def _normalize_magnitude_value(self, value: float) -> float:
        val = float(value)
        abs_val = abs(val)
        if abs_val <= 1.25:
            out = val
        elif abs_val <= 10.5:
            out = val / 10.0
        elif abs_val <= 100.5:
            out = val / 100.0
        else:
            out = max(-1.0, min(1.0, val))
        return max(-1.0, min(1.0, out))

    def _pick_numeric(self, obj: Dict[str, Any], keys: Sequence[str]) -> Optional[float]:
        for key in keys:
            if key in obj and self._is_number(obj[key]):
                return float(obj[key])
        return None

    @staticmethod
    def _is_number(value: Any) -> bool:
        if isinstance(value, bool):
            return False
        try:
            float(value)
            return True
        except Exception:
            return False

    def _extract_position(self, entry: Dict[str, Any]) -> float:
        wcs = entry.get("WCs", [])
        if isinstance(wcs, (list, tuple)) and wcs:
            return float(wcs[-1])
        return float(entry.get("Position", 0.0))

    def _extract_excerpt(self, entry: Dict[str, Any], max_chars: int = 180) -> str:
        body = entry.get("Body", [])
        for scene in body:
            for block in scene:
                if isinstance(block, (list, tuple)) and len(block) >= 2:
                    text = str(block[1]).strip()
                    if text and text != " ":
                        text = text.replace("&quot;", '"').replace("&mdash;", "—").replace("&apos;", "'")
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
            unique: List[str] = []
            for p in pov:
                if p not in unique:
                    unique.append(str(p))
            return ", ".join(unique)
        return str(pov)

    def _build_short_label(self, entry: Dict[str, Any]) -> str:
        chapter = entry.get("Chapter", "")
        name = entry.get("ChapterName", entry.get("Name", ""))
        return f"Ch {chapter}: {name}"

    def _sort_adtx(self) -> None:
        self.ADTX.sort(key=lambda row: float(row.get("Position", 0.0)))
        for i, row in enumerate(self.ADTX, start=1):
            row["Index"] = i

    # ------------------------------------------------------------------
    # Math utilities
    # ------------------------------------------------------------------

    def _odd_window(self, window: int) -> int:
        window = max(1, int(window))
        return window if window % 2 == 1 else window + 1

    def _normalize_weights(self, weights: Sequence[float]) -> Tuple[float, ...]:
        arr = np.array(weights, dtype=float)
        if arr.size == 0:
            return (1.0,)
        total = float(arr.sum())
        if total <= 0:
            arr = np.ones_like(arr) / len(arr)
        else:
            arr = arr / total
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
        lo = float(np.min(values))
        hi = float(np.max(values))
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

    def _reverse_weighted_moving_average(self, values: np.ndarray, window: int) -> np.ndarray:
        if len(values) == 0:
            return values
        return self._weighted_moving_average(values[::-1], window)[::-1]

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

    # ------------------------------------------------------------------
    # Metric computation
    # ------------------------------------------------------------------


    def compute_all_metrics(self) -> None:
        A = self._series("Action")
        D = self._series("Drama")
        T = self._series("Theme")
        H = self._series("Heart")
        S = self._series("Sensuality")
        M = self._series("Magnitude")

        alpha_h, beta_s = self.connotative_weights
        w_d, w_c = self.total_energy_weights

        den_raw = A + D + T
        den = den_raw / 3.0
        con = alpha_h * H + beta_s * S
        premise_force = T * M
        premise_load = np.abs(premise_force)

        Aw = w_d * (A / 3.0)
        Dw = w_d * (D / 3.0)
        Tw = w_d * (T / 3.0)
        Hw = w_c * alpha_h * H
        Sw = w_c * beta_s * S
        den_boundary = Aw + Dw + Tw
        stack = den_boundary + Hw + Sw
        coupling_gap = self.coupling * (den * con / 100.0)
        total = stack + coupling_gap

        den_steady = self._weighted_moving_average(den, self.steady_window)
        con_steady = self._weighted_moving_average(con, self.steady_window)
        total_steady = self._weighted_moving_average(total, self.steady_window)
        premise_steady = self._weighted_moving_average(premise_force, self.steady_window)

        den_trans = den - den_steady
        con_trans = con - con_steady
        total_trans = total - total_steady
        premise_trans = premise_force - premise_steady

        total_mass = self._weighted_moving_average(total, self.mass_window)
        theme_mass = self._weighted_moving_average(T, self.mass_window)
        con_mass = self._weighted_moving_average(con, self.mass_window)
        premise_mass = self._weighted_moving_average(premise_load, self.mass_window)
        baseline = self._local_baseline(total, self.prominence_window)
        prominence = total - baseline

        En = self._minmax_norm(total)
        Mn = self._minmax_norm(total_mass)
        Tn = self._minmax_norm(theme_mass)
        g0, g1, g2 = self.gravity_weights
        gravity = 100.0 * (g0 * En + g1 * Mn + g2 * Tn)

        dA = self._derivative(A) / 100.0
        dD = self._derivative(D) / 100.0
        dT = self._derivative(T) / 100.0
        dH = self._derivative(H) / 100.0
        dS = self._derivative(S) / 100.0
        dM = self._derivative(M)
        state_speed = np.sqrt(dA**2 + dD**2 + dT**2 + dH**2 + dS**2 + dM**2)
        novelty_seed = 0.55 * self._minmax_norm(np.abs(total_trans) + 0.75 * np.abs(premise_trans)) + 0.45 * self._minmax_norm(state_speed)
        novelty = 100.0 * novelty_seed

        setup_signal = T + 0.70 * H + 0.30 * S
        setup_mass = self._weighted_moving_average(setup_signal, self.conversion_window)
        payoff_seed = 0.55 * den + 0.25 * premise_load + 0.20 * gravity
        future_payoff = self._reverse_weighted_moving_average(payoff_seed, self.conversion_window)
        conversion_strength = 100.0 * self._minmax_norm(np.sqrt(np.maximum(setup_mass, 0.0) * np.maximum(future_payoff, 0.0)))
        payoff_link = conversion_strength.copy()

        iw = list(self.indispensability_weights)
        if len(iw) < 4:
            iw = list(self._normalize_weights((0.35, 0.30, 0.20, 0.15)))
        i0, i1, i2, i3 = iw[:4]
        indispensability = 100.0 * (
            i0 * self._minmax_norm(premise_load) +
            i1 * self._minmax_norm(gravity) +
            i2 * self._minmax_norm(payoff_link) +
            i3 * self._minmax_norm(total)
        )

        cw = list(self.compression_weights)
        if len(cw) < 5:
            cw = list(self._normalize_weights((0.30, 0.25, 0.20, 0.20, 0.05)))
        c0, c1, c2, c3, c4 = cw[:5]
        compression_base = (
            c0 * (1.0 - self._minmax_norm(den)) +
            c1 * (1.0 - self._minmax_norm(gravity)) +
            c2 * (1.0 - self._minmax_norm(novelty)) +
            c3 * (1.0 - self._minmax_norm(payoff_link)) +
            c4 * (1.0 - self._minmax_norm(premise_load))
        )
        compression_opportunity = 100.0 * np.clip(
            compression_base - 0.16 * self._minmax_norm(con) - 0.10 * self._minmax_norm(H) - 0.12 * self._minmax_norm(indispensability),
            0.0,
            1.0,
        )

        cheap_action = 100.0 * self._minmax_norm(A * (1.0 - self._minmax_norm(T)))
        cheap_drama = 100.0 * self._minmax_norm(D * (1.0 - self._minmax_norm(T)))
        hollow_sensuality = 100.0 * self._minmax_norm(S * (1.0 - self._minmax_norm(H)) * (1.0 - self._minmax_norm(T)))
        cut_risk = compression_opportunity.copy()

        cumulative_den = self._cumulative_integral(den)
        cumulative_con = self._cumulative_integral(con)
        cumulative_total = self._cumulative_integral(total)
        cumulative_premise = self._cumulative_integral(premise_force)

        computed = {
            "DenotativeEnergyRaw": den_raw,
            "DenotativeEnergy": den,
            "ConnotativeEnergy": con,
            "PremiseForce": premise_force,
            "PremiseLoad": premise_load,
            "ActionWeighted": Aw,
            "DramaWeighted": Dw,
            "ThemeWeighted": Tw,
            "HeartWeighted": Hw,
            "SensualityWeighted": Sw,
            "DenotativeBoundary": den_boundary,
            "WeightedStack": stack,
            "CouplingGap": coupling_gap,
            "TotalEnergy": total,
            "DenotativeSteady": den_steady,
            "ConnotativeSteady": con_steady,
            "TotalSteady": total_steady,
            "PremiseForceSteady": premise_steady,
            "DenotativeTransient": den_trans,
            "ConnotativeTransient": con_trans,
            "TotalTransient": total_trans,
            "PremiseForceTransient": premise_trans,
            "Mass": total_mass,
            "ThemeMass": theme_mass,
            "ConnotativeMass": con_mass,
            "PremiseMass": premise_mass,
            "Baseline": baseline,
            "Prominence": prominence,
            "Gravity": gravity,
            "Novelty": novelty,
            "SetupMass": setup_mass,
            "FuturePayoff": future_payoff,
            "ConversionStrength": conversion_strength,
            "PayoffLink": payoff_link,
            "CompressionOpportunity": compression_opportunity,
            "StructuralIndispensability": indispensability,
            "CheapAction": cheap_action,
            "CheapDrama": cheap_drama,
            "HollowSensuality": hollow_sensuality,
            "CutRisk": cut_risk,
            "dDenotative": self._derivative(den),
            "dConnotative": self._derivative(con),
            "dTotal": self._derivative(total),
            "dPremiseForce": self._derivative(premise_force),
            "CumDenotative": cumulative_den,
            "CumConnotative": cumulative_con,
            "CumTotal": cumulative_total,
            "CumPremiseForce": cumulative_premise,
        }

        for key, values in computed.items():
            self._write_series(key, values)


    def get_peak_rows(self, metric: str = "Gravity", n: int = 8) -> List[Dict[str, Any]]:
        return sorted(self.ADTX, key=lambda r: float(r.get(metric, 0.0)), reverse=True)[:n]

    def get_risky_rows(self, n: int = 8) -> List[Dict[str, Any]]:
        return sorted(self.ADTX, key=lambda r: float(r.get("CompressionOpportunity", r.get("CutRisk", 0.0))), reverse=True)[:n]

    def get_indispensable_rows(self, n: int = 8) -> List[Dict[str, Any]]:
        return sorted(self.ADTX, key=lambda r: float(r.get("StructuralIndispensability", 0.0)), reverse=True)[:n]

    def act_magnitude_rows(self) -> List[Dict[str, Any]]:
        buckets: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for row in self.ADTX:
            key = (str(row.get("Act", "")), str(row.get("ActName", "")))
            buckets.setdefault(key, []).append(row)
        out: List[Dict[str, Any]] = []
        for (act, act_name), rows in buckets.items():
            mags = np.array([float(r.get("Magnitude", 0.0)) for r in rows], dtype=float)
            forces = np.array([float(r.get("PremiseForce", 0.0)) for r in rows], dtype=float)
            out.append({
                "act": act,
                "act_name": act_name,
                "start_chapter": rows[0].get("Chapter", ""),
                "end_chapter": rows[-1].get("Chapter", ""),
                "mean_magnitude": float(mags.mean()) if len(mags) else 0.0,
                "mean_premise_force": float(forces.mean()) if len(forces) else 0.0,
                "start_magnitude": float(mags[0]) if len(mags) else 0.0,
                "end_magnitude": float(mags[-1]) if len(mags) else 0.0,
                "delta_magnitude": float(mags[-1] - mags[0]) if len(mags) else 0.0,
            })
        return out

    def chapter_boundaries(self) -> List[Tuple[float, str]]:
        out: List[Tuple[float, str]] = []
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
                "Heart": row["Heart"],
                "Sensuality": row["Sensuality"],
                "Magnitude": row.get("Magnitude", 0.0),
                "DenotativeEnergy": row.get("DenotativeEnergy", 0.0),
                "ConnotativeEnergy": row.get("ConnotativeEnergy", 0.0),
                "TotalEnergy": row.get("TotalEnergy", 0.0),
                "PremiseForce": row.get("PremiseForce", 0.0),
                "PremiseLoad": row.get("PremiseLoad", 0.0),
                "Gravity": row.get("Gravity", 0.0),
                "Prominence": row.get("Prominence", 0.0),
                "Novelty": row.get("Novelty", 0.0),
                "PayoffLink": row.get("PayoffLink", 0.0),
                "ConversionStrength": row.get("ConversionStrength", 0.0),
                "CompressionOpportunity": row.get("CompressionOpportunity", 0.0),
                "StructuralIndispensability": row.get("StructuralIndispensability", 0.0),
                "CutRisk": row.get("CutRisk", 0.0),
                "Summary": row["Summary"],
                "Blurb": row["Blurb"],
                "Excerpt": row["Excerpt"],
            })
        return rows



    def _summary_dict(self) -> Dict[str, Any]:
        A = self._series("Action")
        D = self._series("Drama")
        T = self._series("Theme")
        H = self._series("Heart")
        S = self._series("Sensuality")
        M = self._series("Magnitude")
        E_d = self._series("DenotativeEnergy")
        E_c = self._series("ConnotativeEnergy")
        E_t = self._series("TotalEnergy")
        PF = self._series("PremiseForce")
        PL = self._series("PremiseLoad")
        G = self._series("Gravity")
        X = self._series("ConversionStrength")
        CO = self._series("CompressionOpportunity")
        SI = self._series("StructuralIndispensability")

        peak_total = self.get_peak_rows("TotalEnergy", 1)[0] if self.ADTX else {}
        peak_gravity = self.get_peak_rows("Gravity", 1)[0] if self.ADTX else {}
        peak_premise = self.get_peak_rows("PremiseLoad", 1)[0] if self.ADTX else {}
        peak_heart = self.get_peak_rows("Heart", 1)[0] if self.ADTX else {}
        peak_sensuality = self.get_peak_rows("Sensuality", 1)[0] if self.ADTX else {}
        peak_conversion = self.get_peak_rows("ConversionStrength", 1)[0] if self.ADTX else {}
        peak_compression = self.get_risky_rows(1)[0] if self.ADTX else {}
        peak_indispensable = self.get_indispensable_rows(1)[0] if self.ADTX else {}

        act_rows = self.act_magnitude_rows()

        return {
            "story": self.story_name,
            "units": len(self.ADTX),
            "start_position": float(self._x()[0]) if len(self.ADTX) else 0.0,
            "end_position": float(self._x()[-1]) if len(self.ADTX) else 0.0,
            "mean_action": float(A.mean()) if len(A) else 0.0,
            "mean_drama": float(D.mean()) if len(D) else 0.0,
            "mean_theme": float(T.mean()) if len(T) else 0.0,
            "mean_heart": float(H.mean()) if len(H) else 0.0,
            "mean_sensuality": float(S.mean()) if len(S) else 0.0,
            "mean_magnitude": float(M.mean()) if len(M) else 0.0,
            "mean_denotative": float(E_d.mean()) if len(E_d) else 0.0,
            "mean_connotative": float(E_c.mean()) if len(E_c) else 0.0,
            "mean_total": float(E_t.mean()) if len(E_t) else 0.0,
            "mean_premise_force": float(PF.mean()) if len(PF) else 0.0,
            "mean_premise_load": float(PL.mean()) if len(PL) else 0.0,
            "mean_gravity": float(G.mean()) if len(G) else 0.0,
            "mean_conversion": float(X.mean()) if len(X) else 0.0,
            "mean_compression": float(CO.mean()) if len(CO) else 0.0,
            "mean_cutrisk": float(CO.mean()) if len(CO) else 0.0,
            "mean_indispensability": float(SI.mean()) if len(SI) else 0.0,
            "peak_total": peak_total,
            "peak_gravity": peak_gravity,
            "peak_premise": peak_premise,
            "peak_heart": peak_heart,
            "peak_sensuality": peak_sensuality,
            "peak_conversion": peak_conversion,
            "peak_compression": peak_compression,
            "peak_cutrisk": peak_compression,
            "peak_indispensable": peak_indispensable,
            "act_magnitude_rows": act_rows,
            "connotative_weights": list(self.connotative_weights),
            "total_energy_weights": list(self.total_energy_weights),
            "coupling": self.coupling,
        }


    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def _annotate_top_peaks(self, ax, metric: str, count: Optional[int] = None) -> None:
        count = count or self.peak_annotate_count
        for row in self.get_peak_rows(metric=metric, n=min(count, len(self.ADTX))):
            x0 = float(row["Position"])
            y0 = float(row.get(metric, 0.0))
            label = f"Ch {row['Chapter']} — {row['ChapterName']}"
            ax.annotate(label, xy=(x0, y0), xytext=(8, 8), textcoords="offset points", fontsize=8, alpha=0.85,
                        arrowprops=dict(arrowstyle="-", lw=0.6, alpha=0.5))

    def _add_chapter_lines(self, ax) -> None:
        for xb, _ in self.chapter_boundaries():
            ax.axvline(xb, color="gray", alpha=0.15, lw=0.6)

    def plot_adths(self, filepath: Optional[str] = None, annotate_peaks: bool = False):
        fig, ax = plt.subplots(figsize=(14, 6))
        x = self._x()
        for key, color in (("Action", self.COLORS["Action"]), ("Drama", self.COLORS["Drama"]),
                           ("Theme", self.COLORS["Theme"]), ("Heart", self.COLORS["Heart"]),
                           ("Sensuality", self.COLORS["Sensuality"])):
            ax.plot(x, self._series(key), color=color, lw=2.0, label=key)
        self._add_chapter_lines(ax)
        if annotate_peaks:
            self._annotate_top_peaks(ax, "TotalEnergy")
        ax.set_title(f"{self.story_name} — ADTHS Fields")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Score (0–100)")
        ax.grid(alpha=0.25)
        ax.legend(ncol=3)
        fig.tight_layout()
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_heart_vs_sensuality(self, filepath: Optional[str] = None):
        fig, ax = plt.subplots(figsize=(14, 5))
        x = self._x()
        ax.plot(x, self._series("Heart"), color=self.COLORS["Heart"], lw=2.1, label="Heart")
        ax.plot(x, self._series("Sensuality"), color=self.COLORS["Sensuality"], lw=2.1, label="Sensuality")
        self._add_chapter_lines(ax)
        ax.set_title(f"{self.story_name} — Heart vs Sensuality")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Score (0–100)")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_energy_superposition(self, filepath: Optional[str] = None, annotate_peaks: bool = False):
        fig, ax = plt.subplots(figsize=(14, 6))
        x = self._x()
        ax.plot(x, self._series("DenotativeEnergy"), color=self.COLORS["Denotative"], lw=2.2, label="Denotative Energy")
        ax.plot(x, self._series("ConnotativeEnergy"), color=self.COLORS["Connotative"], lw=2.2, label="Connotative Energy")
        ax.plot(x, self._series("TotalEnergy"), color=self.COLORS["Total"], lw=2.4, label="Total Energy")
        ax.plot(x, self._series("TotalSteady"), color=self.COLORS["Steady"], lw=1.5, ls="--", alpha=0.8, label="Total Steady")
        self._add_chapter_lines(ax)
        if annotate_peaks:
            self._annotate_top_peaks(ax, "TotalEnergy")
        ax.set_title(f"{self.story_name} — Denotative / Connotative / Total Energy")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Energy")
        ax.grid(alpha=0.25)
        ax.legend(ncol=2)
        fig.tight_layout()
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_alignment(self, filepath: Optional[str] = None, annotate_peaks: bool = True):
        fig, ax1 = plt.subplots(figsize=(14, 6))
        x = self._x()
        ax1.plot(x, self._series("PremiseForce"), color=self.COLORS["PremiseForce"], lw=2.2, label="Premise Force (T×M)")
        ax1.plot(x, self._series("PremiseLoad"), color=self.COLORS["PremiseLoad"], lw=1.6, alpha=0.9, label="Premise Load |T×M|")
        ax1.axhline(0.0, color="#666666", lw=0.8, alpha=0.3)
        self._add_chapter_lines(ax1)
        if annotate_peaks:
            self._annotate_top_peaks(ax1, "PremiseLoad")
        ax1.set_title(f"{self.story_name} — Magnitude / Premise Alignment")
        ax1.set_xlabel("Position (cumulative word count)")
        ax1.set_ylabel("Premise Force / Load")
        ax1.grid(alpha=0.25)

        ax2 = ax1.twinx()
        ax2.plot(x, self._series("Magnitude"), color=self.COLORS["Magnitude"], lw=1.6, ls=":", label="Magnitude (M)")
        ax2.set_ylabel("Magnitude / Alignment")
        ax2.set_ylim(-1.05, 1.05)
        ax2.axhline(0.0, color=self.COLORS["Magnitude"], lw=0.8, alpha=0.25)

        l1, lab1 = ax1.get_legend_handles_labels()
        l2, lab2 = ax2.get_legend_handles_labels()
        ax1.legend(l1 + l2, lab1 + lab2, loc="upper left")
        fig.tight_layout()
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_weighted_layers(self, filepath: Optional[str] = None):
        fig, ax = plt.subplots(figsize=(14, 7))
        x = self._x()
        A = self._series("ActionWeighted")
        D = self._series("DramaWeighted")
        T = self._series("ThemeWeighted")
        H = self._series("HeartWeighted")
        S = self._series("SensualityWeighted")
        stack = self._series("WeightedStack")
        total = self._series("TotalEnergy")
        boundary = self._series("DenotativeBoundary")

        ax.stackplot(
            x, A, D, T, H, S,
            labels=["Action", "Drama", "Theme", "Heart", "Sensuality"],
            colors=[self.COLORS["Action"], self.COLORS["Drama"], self.COLORS["Theme"], self.COLORS["Heart"], self.COLORS["Sensuality"]],
            alpha=0.82,
        )
        ax.fill_between(x, stack, total, color=self.COLORS["Coupling"], alpha=0.18, label="Coupling gap")
        ax.plot(x, boundary, color=self.COLORS["Denotative"], lw=2.2, ls="--", label="Denotative Energy")
        ax.plot(x, total, color=self.COLORS["Total"], lw=2.6, label="Total Energy")
        self._add_chapter_lines(ax)
        ax.set_title(f"{self.story_name} — Weighted ADTHS Layers")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Weighted energy contribution")
        ax.grid(alpha=0.25)
        ax.legend(loc="upper left", ncol=2)
        fig.tight_layout()
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    def plot_cumulative(self, filepath: Optional[str] = None):
        fig, ax = plt.subplots(figsize=(14, 6))
        x = self._x()
        ax.plot(x, self._series("CumDenotative"), color=self.COLORS["Denotative"], lw=2.0, label="Cum Denotative")
        ax.plot(x, self._series("CumConnotative"), color=self.COLORS["Connotative"], lw=2.0, label="Cum Connotative")
        ax.plot(x, self._series("CumTotal"), color=self.COLORS["Total"], lw=2.3, label="Cum Total")
        ax.plot(x, self._series("CumPremiseForce"), color=self.COLORS["PremiseLoad"], lw=1.8, ls=":", label="Cum Premise Force")
        self._add_chapter_lines(ax)
        ax.set_title(f"{self.story_name} — Cumulative Narrative Load")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Integrated load")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig


    def plot_cut_risk(self, filepath: Optional[str] = None):
        fig, ax = plt.subplots(figsize=(14, 5.5))
        x = self._x()
        ax.plot(x, self._series("CompressionOpportunity"), color=self.COLORS["Compression"], lw=2.1, label="Compression Opportunity")
        ax.plot(x, self._series("StructuralIndispensability"), color=self.COLORS["Indispensable"], lw=2.1, label="Structural Indispensability")
        ax.plot(x, self._series("ConversionStrength"), color=self.COLORS["Conversion"], lw=1.6, alpha=0.9, ls="--", label="Conversion Strength")
        self._add_chapter_lines(ax)
        for row in self.get_risky_rows(n=min(6, len(self.ADTX))):
            x0 = float(row["Position"])
            y0 = float(row.get("CompressionOpportunity", 0.0))
            ax.annotate(f"Ch {row['Chapter']}: {row['ChapterName']}", xy=(x0, y0), xytext=(8, 8), textcoords="offset points",
                        fontsize=8, alpha=0.85, arrowprops=dict(arrowstyle="-", lw=0.6, alpha=0.5))
        ax.set_title(f"{self.story_name} — Revision Opportunity Grid")
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel("Revision diagnostic")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig


    def plot_field_distribution(self, field: str, filepath: Optional[str] = None):
        field = field.strip()
        if field not in {"Action", "Drama", "Theme", "Heart", "Sensuality"}:
            raise ValueError(f"Unsupported field distribution plot for: {field}")

        values = self._series(field)
        t = self._x()
        color = self.COLORS[field]

        mean_val = float(np.mean(values)) if len(values) else 0.0
        median_val = float(np.median(values)) if len(values) else 0.0
        std_val = float(np.std(values, ddof=0)) if len(values) else 0.0
        centered = values - mean_val
        m2 = float(np.mean(centered ** 2)) if len(values) else 0.0
        m3 = float(np.mean(centered ** 3)) if len(values) else 0.0
        skew_val = 0.0 if m2 == 0 else float(m3 / (m2 ** 1.5))

        fig = plt.figure(figsize=(14, 8))
        ax_hist = fig.add_axes([0.06, 0.12, 0.14, 0.76])
        ax = fig.add_axes([0.22, 0.12, 0.74, 0.76], sharey=ax_hist)

        ax.plot(t, values, color=color, linewidth=2.6)
        ax.set_ylim(0, 100)
        ax.set_xlabel("Position (cumulative word count)")
        ax.set_ylabel(f"{field} score (0–100)")
        ax.set_title(f"{self.story_name} — {field} Field with Marginal Distribution")
        ax.grid(True, alpha=0.25)
        ax.axhline(mean_val, color=color, linestyle="--", linewidth=1.8, alpha=0.9, label=f"Mean = {mean_val:.1f}")
        ax.axhline(median_val, color=color, linestyle=":", linewidth=1.8, alpha=0.9, label=f"Median = {median_val:.1f}")
        stats = f"μ = {mean_val:.1f}\nσ = {std_val:.1f}\nskew = {skew_val:+.2f}"
        ax.text(0.985, 0.965, stats, transform=ax.transAxes, ha="right", va="top", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85, edgecolor="#bbbbbb"))

        counts, edges = np.histogram(values, bins=self.field_distribution_bins, range=(0, 100), density=True)
        centers = 0.5 * (edges[:-1] + edges[1:])
        heights = np.diff(edges)
        ax_hist.barh(centers, -counts, height=heights * 0.92, color=color, alpha=0.28, edgecolor=color, linewidth=1.0)
        kernel = np.array([1, 2, 3, 2, 1], dtype=float)
        kernel /= kernel.sum()
        smooth_counts = np.convolve(counts, kernel, mode="same")
        ax_hist.plot(-smooth_counts, centers, color=color, linewidth=2.2)
        ax_hist.set_ylim(0, 100)
        ax_hist.set_xlim(-max(max(counts) * 1.35 if len(counts) else 0.02, 0.02), 0)
        ax_hist.axhline(mean_val, color=color, linestyle="--", linewidth=1.5, alpha=0.9)
        ax_hist.axhline(median_val, color=color, linestyle=":", linewidth=1.5, alpha=0.9)
        ax_hist.set_xticks([])
        ax_hist.set_yticks([])
        for spine in ("top", "right", "bottom"):
            ax_hist.spines[spine].set_visible(False)

        ax.legend(loc="lower right")
        if filepath:
            fig.savefig(filepath, dpi=200, bbox_inches="tight")
        return fig

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def export_full_csv(self, filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        rows = self.chapter_summary_rows()
        fields = list(rows[0].keys()) if rows else []
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
            "POVText", "SettingText", "Action", "Drama", "Theme", "Heart", "Sensuality", "Magnitude",
            "DenotativeEnergy", "ConnotativeEnergy", "TotalEnergy", "PremiseForce", "PremiseLoad",
            "Mass", "ThemeMass", "ConnotativeMass", "PremiseMass", "Prominence", "Gravity",
            "Novelty", "PayoffLink", "ConversionStrength", "CompressionOpportunity", "StructuralIndispensability", "CutRisk",
            "Summary", "Blurb", "Excerpt",
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
            "POVText", "SettingText", "Action", "Drama", "Theme", "Heart", "Sensuality", "Magnitude",
            "DenotativeEnergy", "ConnotativeEnergy", "TotalEnergy", "PremiseForce", "PremiseLoad",
            "Prominence", "Gravity", "Novelty", "PayoffLink", "ConversionStrength", "CompressionOpportunity", "StructuralIndispensability", "CutRisk", "Summary", "Blurb", "Excerpt",
        ]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in fields})
        return filepath

    def _slug(self, text: str) -> str:
        cleaned = []
        for ch in str(text).lower():
            if ch.isalnum():
                cleaned.append(ch)
            elif ch in (" ", "-", "_"):
                cleaned.append("_")
        return "".join(cleaned).strip("_") or "story_nk"

    def _report_image_paths(self, outdir: str) -> Dict[str, str]:
        stem = self._slug(self.story_name)
        return {
            "adths": os.path.join(outdir, f"{stem}_nk_adths.png"),
            "heart_sensuality": os.path.join(outdir, f"{stem}_nk_hs.png"),
            "energy": os.path.join(outdir, f"{stem}_nk_energy.png"),
            "alignment": os.path.join(outdir, f"{stem}_nk_alignment.png"),
            "weighted": os.path.join(outdir, f"{stem}_nk_weighted.png"),
            "cumulative": os.path.join(outdir, f"{stem}_nk_cumulative.png"),
            "cutrisk": os.path.join(outdir, f"{stem}_nk_cutrisk.png"),
        }

    def _export_graph_images_for_report(self, outdir: str) -> Dict[str, str]:
        os.makedirs(outdir, exist_ok=True)
        paths = self._report_image_paths(outdir)
        self.plot_adths(paths["adths"], annotate_peaks=True)
        self.plot_heart_vs_sensuality(paths["heart_sensuality"])
        self.plot_energy_superposition(paths["energy"], annotate_peaks=True)
        self.plot_alignment(paths["alignment"], annotate_peaks=True)
        self.plot_weighted_layers(paths["weighted"])
        self.plot_cumulative(paths["cumulative"])
        self.plot_cut_risk(paths["cutrisk"])
        return paths

    def _html(self, value: Any) -> str:
        return "" if value is None else escape(str(value))

    def _html_peak_block(self, row: Dict[str, Any], metric: str) -> str:
        return f"""
        <div class="peak-card">
            <div class="peak-title">Ch {self._html(row.get('Chapter', ''))} — {self._html(row.get('ChapterName', ''))}</div>
            <div class="peak-meta">
                <strong>{self._html(metric)}:</strong> {float(row.get(metric, 0.0)):.2f}
                &nbsp;|&nbsp;<strong>Total:</strong> {float(row.get('TotalEnergy', 0.0)):.2f}
                &nbsp;|&nbsp;<strong>Den:</strong> {float(row.get('DenotativeEnergy', 0.0)):.2f}
                &nbsp;|&nbsp;<strong>Con:</strong> {float(row.get('ConnotativeEnergy', 0.0)):.2f}
                &nbsp;|&nbsp;<strong>M:</strong> {float(row.get('Magnitude', 0.0)):+.2f}
            </div>
            <div class="peak-meta"><strong>POV:</strong> {self._html(row.get('POVText', ''))}</div>
            <div class="peak-meta"><strong>Setting:</strong> {self._html(row.get('SettingText', ''))}</div>
            <div class="peak-summary"><strong>Summary:</strong> {self._html(row.get('Summary', ''))}</div>
            <div class="peak-summary"><strong>Blurb:</strong> {self._html(row.get('Blurb', ''))}</div>
            <div class="peak-excerpt">{self._html(row.get('Excerpt', ''))}</div>
        </div>
        """

    def _html_table_rows(self, rows: List[Dict[str, Any]]) -> str:
        cells = []
        for row in rows:
            cells.append(f"""
            <tr>
                <td>{self._html(row.get('Chapter', ''))}</td>
                <td>{self._html(row.get('ChapterName', ''))}</td>
                <td>{self._html(row.get('POV', ''))}</td>
                <td>{float(row.get('Action', 0.0)):.1f}</td>
                <td>{float(row.get('Drama', 0.0)):.1f}</td>
                <td>{float(row.get('Theme', 0.0)):.1f}</td>
                <td>{float(row.get('Heart', 0.0)):.1f}</td>
                <td>{float(row.get('Sensuality', 0.0)):.1f}</td>
                <td>{float(row.get('Magnitude', 0.0)):+.2f}</td>
                <td>{float(row.get('DenotativeEnergy', 0.0)):.1f}</td>
                <td>{float(row.get('ConnotativeEnergy', 0.0)):.1f}</td>
                <td>{float(row.get('TotalEnergy', 0.0)):.1f}</td>
                <td>{float(row.get('PremiseForce', 0.0)):+.1f}</td>
                <td>{float(row.get('Gravity', 0.0)):.1f}</td>
                <td>{float(row.get('ConversionStrength', 0.0)):.1f}</td>
                <td>{float(row.get('CompressionOpportunity', row.get('CutRisk', 0.0))):.1f}</td>
                <td>{float(row.get('StructuralIndispensability', 0.0)):.1f}</td>
            </tr>
            """)
        return "\n".join(cells)

    def _html_llm_list(self, items: List[str]) -> str:
        if not items:
            return "<p class='small'>None.</p>"
        return "<ul>" + "".join(f"<li>{self._html(item)}</li>" for item in items) + "</ul>"

    def _html_llm_regions(self, rows: List[Dict[str, Any]], title_key: str = "reason") -> str:
        if not rows:
            return "<p class='small'>None.</p>"
        blocks = []
        for row in rows:
            heading = f"Ch {row.get('chapter', '')} — {row.get('chapter_name', '')}" if 'chapter' in row else f"Ch {row.get('start_chapter', '')}–{row.get('end_chapter', '')}"
            meta = []
            if 'problem_type' in row:
                meta.append(f"<strong>Problem:</strong> {self._html(row.get('problem_type', ''))}")
            if 'suggested_action' in row:
                meta.append(f"<strong>Action:</strong> {self._html(row.get('suggested_action', ''))}")
            body = []
            if title_key in row:
                body.append(f"<div><strong>{self._html(title_key.replace('_', ' ').title())}:</strong> {self._html(row.get(title_key, ''))}</div>")
            if 'suggested_fix' in row:
                body.append(f"<div><strong>Suggested fix:</strong> {self._html(row.get('suggested_fix', ''))}</div>")
            if 'revision_instruction' in row:
                body.append(f"<div><strong>Revision instruction:</strong> {self._html(row.get('revision_instruction', ''))}</div>")
            if 'note' in row and title_key != 'note':
                body.append(f"<div><strong>Note:</strong> {self._html(row.get('note', ''))}</div>")
            blocks.append(f"""
            <div class="peak-card">
                <div class="peak-title">{self._html(heading)}</div>
                <div class="peak-meta">{' &nbsp;|&nbsp; '.join(meta) if meta else ''}</div>
                {''.join(body)}
            </div>
            """)
        return "\n".join(blocks)

    def _html_llm_diagnosis_section(self, diagnosis: Optional[Dict[str, Any]]) -> str:
        if not diagnosis:
            return "<h2 id='LLM'>LLM Revision Diagnosis</h2><p class='small'>No LLM diagnosis was attached to this report.</p>"
        macro = diagnosis.get("macro_assessment", {})
        strongest = diagnosis.get("strongest_regions", [])
        drag = diagnosis.get("drag_corridors", [])
        turns = diagnosis.get("premise_turns", [])
        cuts = diagnosis.get("cut_candidates", [])
        chapter_notes = diagnosis.get("chapter_notes", [])
        next_pass = diagnosis.get("next_revision_pass", [])
        return f"""
        <div class="page-break"></div>
        <h2 id="LLM">LLM Revision Diagnosis</h2>
        <div class="callout">
            <div><strong>Structural health:</strong> {self._html(macro.get('structural_health', ''))}</div>
            <div><strong>Connotative health:</strong> {self._html(macro.get('connotative_health', ''))}</div>
            <div><strong>Premise alignment:</strong> {self._html(macro.get('premise_alignment_health', ''))}</div>
            <div><strong>Primary strength:</strong> {self._html(macro.get('primary_strength', ''))}</div>
            <div><strong>Primary risk:</strong> {self._html(macro.get('primary_risk', ''))}</div>
        </div>
        <p>{self._html(macro.get('one_paragraph_verdict', ''))}</p>
        <h3>Strongest Regions</h3>
        <div class="peak-grid">{self._html_llm_regions(strongest, title_key='reason')}</div>
        <h3>Drag Corridors</h3>
        <div class="peak-grid">{self._html_llm_regions(drag, title_key='reason')}</div>
        <h3>Premise Turns</h3>
        <div class="peak-grid">{self._html_llm_regions(turns, title_key='reason')}</div>
        <h3>Cut Candidates</h3>
        <div class="peak-grid">{self._html_llm_regions(cuts, title_key='cut_risk_reason')}</div>
        <h3>Chapter Notes</h3>
        <div class="peak-grid">{self._html_llm_regions(chapter_notes, title_key='assessment')}</div>
        <h3>Next Revision Pass</h3>
        {self._html_llm_list(next_pass)}
        """

    def build_html_report(
        self,
        html_path: str,
        image_paths: Optional[Dict[str, str]] = None,
        title: Optional[str] = None,
        diagnosis: Optional[Dict[str, Any]] = None,
    ) -> str:
        outdir = os.path.dirname(html_path) or "."
        os.makedirs(outdir, exist_ok=True)
        if image_paths is None:
            image_paths = self._export_graph_images_for_report(outdir)

        summary = self._summary_dict()
        top_total = self.get_peak_rows("TotalEnergy", n=min(8, len(self.ADTX)))
        top_premise = self.get_peak_rows("PremiseLoad", n=min(8, len(self.ADTX)))
        top_cut = self.get_risky_rows(n=min(8, len(self.ADTX)))
        table_rows = self.chapter_summary_rows()

        def rel(path: str) -> str:
            return os.path.relpath(path, start=outdir).replace("\\", "/")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{self._html(title or f'{self.story_name} — Narrative Kinematics Report')}</title>
<style>
@page {{ size: Letter; margin: 0.65in 0.7in 0.75in 0.7in; }}
html, body {{ margin: 0; padding: 0; background: #fff; color: #222; font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.45; }}
h1, h2, h3 {{ page-break-after: avoid; break-after: avoid-page; }}
h1 {{ font-size: 24pt; margin: 0 0 0.15in 0; }}
h2 {{ font-size: 16pt; margin: 0.28in 0 0.12in 0; border-bottom: 1px solid #ddd; padding-bottom: 0.05in; }}
h3 {{ font-size: 12.5pt; margin: 0.20in 0 0.08in 0; }}
p, ul {{ margin: 0.08in 0; }}
.small {{ font-size: 9pt; color: #555; }}
hr {{ border: 0; border-top: 1px solid #ddd; margin: 0.12in 0; }}
.meta-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.12in; margin: 0.12in 0 0.18in 0; }}
.meta-card, .callout, .peak-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 0.10in 0.12in; background: #fafafa; }}
.figure {{ margin: 0.16in 0 0.22in 0; page-break-inside: avoid; break-inside: avoid; }}
.figure img {{ width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px; }}
.caption {{ font-size: 9pt; color: #555; margin-top: 0.04in; }}
.peak-grid {{ display: grid; grid-template-columns: 1fr; gap: 0.12in; }}
.peak-title {{ font-weight: bold; font-size: 11.5pt; }}
.peak-meta {{ font-size: 9.5pt; color: #555; margin-top: 0.03in; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.8pt; table-layout: fixed; }}
th, td {{ border: 1px solid #ddd; padding: 0.05in 0.05in; vertical-align: top; }}
thead th {{ background: #f3f3f3; }}
.page-break {{ page-break-before: always; break-before: page; }}
a {{ color: #000; text-decoration: none; }}
</style>
</head>
<body>
<h1>{self._html(title or f'{self.story_name} — Narrative Kinematics Report')}</h1>
<p class="small">ADTHS/M report. Magnitude (M) tracks premise alignment; Denotative Energy comes from ADT; Connotative Energy comes from weighted H/S; Total Energy includes coupling. Revision diagnostics distinguish Compression Opportunity from Structural Indispensability.</p>
<hr>
<ul>
<li>01.&ensp;<a href="#Overview">System Overview</a></li>
<li>02.&ensp;<a href="#ADTHS">ADTHS Fields</a></li>
<li>03.&ensp;<a href="#ALIGN">Magnitude / Premise Alignment</a></li>
<li>04.&ensp;<a href="#WEIGHTED">Weighted Energy Layers</a></li>
<li>05.&ensp;<a href="#TOTAL">Top Total-Energy Peaks</a></li>
<li>06.&ensp;<a href="#PREMISE">Largest Premise Loads</a></li>
<li>07.&ensp;<a href="#CUT">Compression Candidates</a></li>
<li>08.&ensp;<a href="#IND">Most Indispensable Units</a></li>
<li>09.&ensp;<a href="#LLM">LLM Revision Analysis</a></li>
<li>10.&ensp;<a href="#TABLE">Full Chapter Table</a></li>
</ul>
<hr>
<div class="meta-grid">
  <div class="meta-card"><strong>Story</strong><br>{self._html(summary['story'])}</div>
  <div class="meta-card"><strong>Units</strong><br>{summary['units']}</div>
  <div class="meta-card"><strong>Position Span</strong><br>{summary['start_position']:,.0f} - {summary['end_position']:,.0f}</div>
  <div class="meta-card"><strong>Mean Denotative</strong><br>{summary['mean_denotative']:.2f}</div>
  <div class="meta-card"><strong>Mean Connotative</strong><br>{summary['mean_connotative']:.2f}</div>
  <div class="meta-card"><strong>Mean Total</strong><br>{summary['mean_total']:.2f}</div>
  <div class="meta-card"><strong>Mean Heart</strong><br>{summary['mean_heart']:.2f}</div>
  <div class="meta-card"><strong>Mean Sensuality</strong><br>{summary['mean_sensuality']:.2f}</div>
  <div class="meta-card"><strong>Mean Magnitude</strong><br>{summary['mean_magnitude']:+.3f}</div>
  <div class="meta-card"><strong>Mean Conversion</strong><br>{summary['mean_conversion']:.2f}</div>
  <div class="meta-card"><strong>Mean Indispensability</strong><br>{summary['mean_indispensability']:.2f}</div>
</div>
<div class="callout">
  <strong>Peak Total:</strong> Ch {self._html(summary['peak_total'].get('Chapter', ''))} — {self._html(summary['peak_total'].get('ChapterName', ''))}<br>
  <strong>Peak Gravity:</strong> Ch {self._html(summary['peak_gravity'].get('Chapter', ''))} — {self._html(summary['peak_gravity'].get('ChapterName', ''))}<br>
  <strong>Peak Premise Load:</strong> Ch {self._html(summary['peak_premise'].get('Chapter', ''))} — {self._html(summary['peak_premise'].get('ChapterName', ''))}<br>
  <strong>Peak Heart:</strong> Ch {self._html(summary['peak_heart'].get('Chapter', ''))} — {self._html(summary['peak_heart'].get('ChapterName', ''))}<br>
  <strong>Peak Sensuality:</strong> Ch {self._html(summary['peak_sensuality'].get('Chapter', ''))} — {self._html(summary['peak_sensuality'].get('ChapterName', ''))}<br>
  <strong>Peak Conversion:</strong> Ch {self._html(summary['peak_conversion'].get('Chapter', ''))} — {self._html(summary['peak_conversion'].get('ChapterName', ''))}<br>
  <strong>Most Indispensable:</strong> Ch {self._html(summary['peak_indispensable'].get('Chapter', ''))} — {self._html(summary['peak_indispensable'].get('ChapterName', ''))}
</div>
<h2 id="Overview">System Overview</h2>
<p>Action, Drama, and Theme define the denotative field. Heart and Sensuality define the connotative field. Magnitude (M) is premise alignment in [-1, 1]. Denotative Energy = (A + D + T)/3. Connotative Energy = αH + βS. Total Energy = weighted Denotative + weighted Connotative + coupling bonus. Premise Force = T×M. Narrative Gravity estimates which regions are genuinely load-bearing rather than merely loud.</p>
<h2 id="ADTHS">ADTHS Fields</h2>
<div class="figure"><img src="{self._html(rel(image_paths['adths']))}" alt="ADTHS fields"><div class="caption">Action, Drama, Theme, Heart, and Sensuality over cumulative story position.</div></div>
<div class="figure"><img src="{self._html(rel(image_paths['heart_sensuality']))}" alt="Heart vs Sensuality"><div class="caption">Heart and Sensuality isolated.</div></div>
<div class="figure"><img src="{self._html(rel(image_paths['energy']))}" alt="Energy superposition"><div class="caption">Denotative, Connotative, and Total Energy, with total steady-state.</div></div>
<h2 id="ALIGN">Magnitude / Premise Alignment</h2>
<div class="figure"><img src="{self._html(rel(image_paths['alignment']))}" alt="Alignment"><div class="caption">Premise Force and Load against Magnitude.</div></div>
<h2 id="WEIGHTED">Weighted Energy Layers</h2>
<div class="figure"><img src="{self._html(rel(image_paths['weighted']))}" alt="Weighted layers"><div class="caption">Weighted ADT on bottom, H/S on top, dashed Denotative Energy boundary, black Total Energy line, and coupling-gap band.</div></div>
<div class="figure"><img src="{self._html(rel(image_paths['cumulative']))}" alt="Cumulative loads"><div class="caption">Cumulative denotative, connotative, total, and premise progression.</div></div>
<div class="figure"><img src="{self._html(rel(image_paths['cutrisk']))}" alt="Cut risk"><div class="caption">Compression Opportunity, Structural Indispensability, and Conversion Strength.</div></div>
<div class="page-break"></div>
<h2 id="TOTAL">Top Total-Energy Peaks</h2>
<div class="peak-grid">{''.join(self._html_peak_block(row, 'TotalEnergy') for row in top_total)}</div>
<div class="page-break"></div>
<h2 id="PREMISE">Largest Premise Loads</h2>
<div class="peak-grid">{''.join(self._html_peak_block(row, 'PremiseLoad') for row in top_premise)}</div>
<div class="page-break"></div>
<h2 id="CUT">Compression Candidates</h2>
<div class="peak-grid">{''.join(self._html_peak_block(row, 'CompressionOpportunity') for row in top_cut)}</div>
<div class="page-break"></div>
<h2 id="IND">Most Indispensable Units</h2>
<div class="peak-grid">{''.join(self._html_peak_block(row, 'StructuralIndispensability') for row in self.get_indispensable_rows(n=min(8, len(self.ADTX))))}</div>
{self._html_llm_diagnosis_section(diagnosis)}
<div class="page-break"></div>
<h2 id="TABLE">Full Chapter / Unit Table</h2>
<table>
<thead>
<tr>
<th>Ch</th><th>Chapter</th><th>A</th><th>D</th><th>T</th><th>H</th><th>S</th><th>M</th><th>Den</th><th>Con</th><th>Total</th><th>PF</th><th>G</th><th>X</th><th>Comp</th><th>Ind</th><th>POV</th><th>Summary</th>
</tr>
</thead>
<tbody>
{self._html_table_rows(table_rows)}
</tbody>
</table>
</body>
</html>
"""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        return html_path

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
            self.build_html_report(html_path=html_path, image_paths=image_paths, title=title, diagnosis=diagnosis)
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
                margin={"top": "0.65in", "right": "0.7in", "bottom": "0.75in", "left": "0.7in"},
                prefer_css_page_size=True,
            )
            await browser.close()
        return pdf_path

    def export_playwright_pdf_report(self, *args, **kwargs) -> str:
        return self._run_async_in_thread(self.export_playwright_pdf_report_async(*args, **kwargs))

    def export_report_bundle(self, outdir: Optional[str] = None) -> Dict[str, str]:
        outdir = outdir or self.outdir
        os.makedirs(outdir, exist_ok=True)
        stem = self._slug(self.story_name)
        paths = {
            "full_csv": os.path.join(outdir, f"{stem}_nk_full.csv"),
            "peaks_csv": os.path.join(outdir, f"{stem}_nk_top_peaks.csv"),
            "cut_csv": os.path.join(outdir, f"{stem}_nk_revision_candidates.csv"),
            "html_report": os.path.join(outdir, f"{stem}_nk_report.html"),
            "pdf_report": os.path.join(outdir, f"{stem}_nk_report.pdf"),
        }
        self.export_full_csv(paths["full_csv"])
        self.export_top_peaks_csv(paths["peaks_csv"], metric="TotalEnergy")
        self.export_cut_risk_csv(paths["cut_csv"])
        image_paths = self._export_graph_images_for_report(outdir)
        paths.update(image_paths)
        self.build_html_report(paths["html_report"], image_paths=image_paths, title=f"{self.story_name} — Narrative Kinematics Report")
        try:
            self.export_playwright_pdf_report(paths["pdf_report"], html_path=paths["html_report"], image_paths=image_paths,
                                              title=f"{self.story_name} — Narrative Kinematics Report", rebuild_html=False)
        except Exception:
            paths["pdf_report"] = ""
        return paths

    def export_html_report_bundle(self, outdir: Optional[str] = None, include_llm_diagnosis: bool = False,
                                  api_key: Optional[str] = None, model: str = "gpt-5.4",
                                  extra_instruction: Optional[str] = None) -> Dict[str, str]:
        return self._run_async_in_thread(
            self.export_html_report_bundle_async(
                outdir=outdir,
                include_llm_diagnosis=include_llm_diagnosis,
                api_key=api_key,
                model=model,
                extra_instruction=extra_instruction,
            )
        )

    async def export_html_report_bundle_async(self, outdir: Optional[str] = None, include_llm_diagnosis: bool = False,
                                              api_key: Optional[str] = None, model: str = "gpt-5.4",
                                              extra_instruction: Optional[str] = None) -> Dict[str, str]:
        outdir = outdir or self.outdir
        os.makedirs(outdir, exist_ok=True)
        stem = self._slug(self.story_name)
        image_paths = self._export_graph_images_for_report(outdir)
        full_csv = os.path.join(outdir, f"{stem}_nk_full.csv")
        peaks_csv = os.path.join(outdir, f"{stem}_nk_top_peaks.csv")
        cut_csv = os.path.join(outdir, f"{stem}_nk_revision_candidates.csv")
        html_report = os.path.join(outdir, f"{stem}_nk_report.html")
        pdf_report = os.path.join(outdir, f"{stem}_nk_report.pdf")
        diagnosis_json = os.path.join(outdir, f"{stem}_nk_llm_diagnosis.json")

        self.export_full_csv(full_csv)
        self.export_top_peaks_csv(peaks_csv, metric="TotalEnergy")
        self.export_cut_risk_csv(cut_csv)

        diagnosis = None
        if include_llm_diagnosis:
            diagnosis = self.query_openai_diagnosis(
                api_key=api_key,
                model=model,
                save_json_path=diagnosis_json,
                extra_instruction=extra_instruction,
            )

        self.build_html_report(html_report, image_paths=image_paths, title=f"{self.story_name} — Narrative Kinematics Report", diagnosis=diagnosis)
        try:
            await self.export_playwright_pdf_report_async(pdf_report, html_path=html_report, image_paths=image_paths,
                                                          title=f"{self.story_name} — Narrative Kinematics Report",
                                                          diagnosis=diagnosis, rebuild_html=False)
        except Exception:
            pdf_report = ""
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

    # ------------------------------------------------------------------
    # LLM payload / diagnosis
    # ------------------------------------------------------------------

    def _llm_safe_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
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
            "heart": float(row.get("Heart", 0.0)),
            "sensuality": float(row.get("Sensuality", 0.0)),
            "magnitude": float(row.get("Magnitude", 0.0)),
            "denotative_energy": float(row.get("DenotativeEnergy", 0.0)),
            "connotative_energy": float(row.get("ConnotativeEnergy", 0.0)),
            "total_energy": float(row.get("TotalEnergy", 0.0)),
            "premise_force": float(row.get("PremiseForce", 0.0)),
            "premise_load": float(row.get("PremiseLoad", 0.0)),
            "gravity": float(row.get("Gravity", 0.0)),
            "prominence": float(row.get("Prominence", 0.0)),
            "cheap_action": float(row.get("CheapAction", 0.0)),
            "cheap_drama": float(row.get("CheapDrama", 0.0)),
            "hollow_sensuality": float(row.get("HollowSensuality", 0.0)),
            "novelty": float(row.get("Novelty", 0.0)),
            "payoff_link": float(row.get("PayoffLink", 0.0)),
            "conversion_strength": float(row.get("ConversionStrength", 0.0)),
            "compression_opportunity": float(row.get("CompressionOpportunity", row.get("CutRisk", 0.0))),
            "structural_indispensability": float(row.get("StructuralIndispensability", 0.0)),
            "cut_risk": float(row.get("CutRisk", 0.0)),
            "pov": row.get("POVText", ""),
            "setting": row.get("SettingText", ""),
            "summary": row.get("Summary", ""),
            "blurb": row.get("Blurb", ""),
            "excerpt": row.get("Excerpt", ""),
        }

    def _heuristic_rows(self, key: str, n: int = 8) -> List[Dict[str, Any]]:
        return sorted(self.ADTX, key=lambda r: float(r.get(key, 0.0)), reverse=True)[:n]

    def build_llm_payload(self, top_n: int = 12, sample_n: int = 12) -> Dict[str, Any]:
        summary = self._summary_dict()
        unit_rows = [self._llm_safe_row(row) for row in self.ADTX]
        if len(unit_rows) <= sample_n:
            sampled = unit_rows
        else:
            idxs = np.linspace(0, len(unit_rows) - 1, sample_n, dtype=int)
            sampled = [unit_rows[i] for i in idxs]
        return {
            "story_name": self.story_name,
            "unit_count": len(self.ADTX),
            "scale_notes": {
                "action_drama_theme_heart_sensuality": "0-100 scalar magnitudes",
                "magnitude": "normalized to [-1, 1]; legacy Vector/V accepted and remapped to Magnitude/M",
                "denotative_energy": "(A + D + T) / 3",
                "connotative_energy": f"{self.connotative_weights[0]:.3f}*H + {self.connotative_weights[1]:.3f}*S",
                "total_energy": "weighted denotative + weighted connotative + coupling bonus",
                "premise_force": "T × M",
            },
            "weights": {
                "connotative_weights": list(self.connotative_weights),
                "total_energy_weights": list(self.total_energy_weights),
                "coupling": self.coupling,
                "gravity_weights": list(self.gravity_weights),
                "compression_weights": list(self.compression_weights),
                "indispensability_weights": list(self.indispensability_weights),
            },
            "metrics_summary": summary,
            "top_total": [self._llm_safe_row(r) for r in self.get_peak_rows("TotalEnergy", n=min(top_n, len(self.ADTX)))],
            "top_denotative": [self._llm_safe_row(r) for r in self.get_peak_rows("DenotativeEnergy", n=min(top_n, len(self.ADTX)))],
            "top_heart": [self._llm_safe_row(r) for r in self.get_peak_rows("Heart", n=min(top_n, len(self.ADTX)))],
            "top_sensuality": [self._llm_safe_row(r) for r in self.get_peak_rows("Sensuality", n=min(top_n, len(self.ADTX)))],
            "top_premise": [self._llm_safe_row(r) for r in self.get_peak_rows("PremiseLoad", n=min(top_n, len(self.ADTX)))],
            "top_cut_risk": [self._llm_safe_row(r) for r in self.get_risky_rows(n=min(top_n, len(self.ADTX)))],
            "top_indispensable": [self._llm_safe_row(r) for r in self.get_indispensable_rows(n=min(top_n, len(self.ADTX)))],
            "act_magnitude_rows": self.act_magnitude_rows(),
            "top_cheap_action": [self._llm_safe_row(r) for r in self._heuristic_rows("CheapAction", n=min(top_n, len(self.ADTX)))],
            "top_cheap_drama": [self._llm_safe_row(r) for r in self._heuristic_rows("CheapDrama", n=min(top_n, len(self.ADTX)))],
            "top_hollow_sensuality": [self._llm_safe_row(r) for r in self._heuristic_rows("HollowSensuality", n=min(top_n, len(self.ADTX)))],
            "sampled_units": sampled,
            "chapter_table": [self._llm_safe_row(r) for r in self.ADTX],
        }

    def query_openai_diagnosis(self, api_key: Optional[str] = None, model: str = "gpt-5.4",
                               save_json_path: Optional[str] = None, extra_instruction: Optional[str] = None,
                               top_n: int = 12, sample_n: int = 12) -> Dict[str, Any]:
        if OpenAI is None:
            raise ImportError("openai.OpenAI is unavailable. Install or upgrade the OpenAI Python package before calling query_openai_diagnosis().")

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
                        "structural_health": {"type": "string"},
                        "connotative_health": {"type": "string"},
                        "premise_alignment_health": {"type": "string"},
                        "primary_strength": {"type": "string"},
                        "primary_risk": {"type": "string"},
                        "one_paragraph_verdict": {"type": "string"},
                    },
                    "required": [
                        "structural_health", "connotative_health", "premise_alignment_health",
                        "primary_strength", "primary_risk", "one_paragraph_verdict",
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
                        },
                        "required": ["start_chapter", "end_chapter", "problem_type", "reason", "suggested_fix"],
                    },
                },
                "premise_turns": {
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
                "cut_candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "chapter": {"type": "integer"},
                            "chapter_name": {"type": "string"},
                            "cut_risk_reason": {"type": "string"},
                            "suggested_action": {"type": "string", "enum": ["keep", "trim", "compress_hard", "merge", "differentiate"]},
                            "note": {"type": "string"},
                        },
                        "required": ["chapter", "chapter_name", "cut_risk_reason", "suggested_action", "note"],
                    },
                },
                "chapter_notes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "chapter": {"type": "integer"},
                            "chapter_name": {"type": "string"},
                            "assessment": {"type": "string"},
                            "note": {"type": "string"},
                        },
                        "required": ["chapter", "chapter_name", "assessment", "note"],
                    },
                },
                "next_revision_pass": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "macro_assessment", "strongest_regions", "drag_corridors", "premise_turns",
                "cut_candidates", "chapter_notes", "next_revision_pass",
            ],
        }

        developer_prompt = (
            "You are a rigorous developmental editor analyzing a narrative using a quantitative Narrative Kinematics dataset. "
            "Action, Drama, and Theme are denotative fields. Heart and Sensuality are connotative fields. Magnitude (M) is premise alignment in [-1,1]. "
            "Denotative Energy = (A + D + T)/3. Connotative Energy = weighted H/S. Total Energy includes weighted denotative, weighted connotative, and a coupling bonus. "
            "Use the metrics as evidence, not as dogma. Prefer blunt revision guidance. Look for: true structural peaks, drag corridors, premise drift, cheap action, cheap heat, hollow sensuality, and chapters that feel affectively sticky but structurally underpaid. "
            "When writing chapter notes, keep the assessment and the revision note distinct."
        )
        if extra_instruction:
            developer_prompt += f"\n\nAdditional instruction:\n{extra_instruction}"

        user_prompt = (
            "Analyze the following StoryNK ADTHS/M payload and return a structured revision diagnosis. "
            "Focus on where the story is strongest, where it drags, where connotative energy is doing the heavy lifting, where premise alignment matters most, and what the next revision pass should target.\n\n"
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

    # ------------------------------------------------------------------
    # Async bridge
    # ------------------------------------------------------------------

    def _run_async_in_thread(self, coro):
        result = {"value": None, "error": None}

        def runner():
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                result["value"] = loop.run_until_complete(coro)
            except Exception as exc:  # pragma: no cover
                result["error"] = exc
            finally:
                try:
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
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
