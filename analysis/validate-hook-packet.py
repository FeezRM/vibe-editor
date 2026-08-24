#!/usr/bin/env python3
"""Validate the machine-readable contract for a vibe-editor visual hook."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


ALLOWED_RUN_MODES = {"design", "trial", "fast"}
ALLOWED_HOOK_MODES = {
    "receipt-first",
    "comparison-first",
    "demonstration-first",
    "roleplay-first",
    "interface-dive",
    "pattern-break",
    "lockup-first",
}
ALLOWED_OWNERS = {"premiere", "hyperframes", "both"}
SCORE_KEYS = (
    "specificity",
    "proof",
    "tension",
    "secondBeat",
    "muteTest",
    "feasibility",
)
GENERIC_BRIDGES = (
    "trust me",
    "simple concept",
    "wish you knew this sooner",
    "everyone is saying",
    "everything you need to know",
    "are you struggling with",
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def require_text(report: Report, value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        report.error(f"{label} must be a non-empty string")
        return ""
    return value.strip()


def number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(float(value)):
        return None
    return float(value)


def validate_evidence(report: Report, items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list) or not items:
        report.error("evidence must contain at least one verified item")
        return {}

    by_id: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(items):
        label = f"evidence[{index}]"
        if not isinstance(raw, dict):
            report.error(f"{label} must be an object")
            continue
        evidence_id = require_text(report, raw.get("id"), f"{label}.id")
        require_text(report, raw.get("kind"), f"{label}.kind")
        require_text(report, raw.get("path"), f"{label}.path")
        require_text(report, raw.get("claim"), f"{label}.claim")
        require_text(report, raw.get("source"), f"{label}.source")
        if raw.get("verified") is not True:
            report.error(f"{label}.verified must be true before the item can enter a hook")
        if evidence_id:
            if evidence_id in by_id:
                report.error(f"duplicate evidence id: {evidence_id}")
            by_id[evidence_id] = raw
    return by_id


def validate_beats(report: Report, candidate_id: str, beats: Any, duration: float) -> None:
    label = f"candidate {candidate_id}"
    if not isinstance(beats, list) or len(beats) < 3:
        report.error(f"{label} needs at least three beats spanning the opening")
        return

    parsed: list[tuple[float, float, dict[str, Any], int]] = []
    for index, raw in enumerate(beats):
        beat_label = f"{label}.beats[{index}]"
        if not isinstance(raw, dict):
            report.error(f"{beat_label} must be an object")
            continue
        start = number(raw.get("start"))
        end = number(raw.get("end"))
        if start is None or end is None or start < 0 or end <= start:
            report.error(f"{beat_label} needs numeric start/end with 0 <= start < end")
            continue
        for field in ("speech", "visual", "change"):
            text = require_text(report, raw.get(field), f"{beat_label}.{field}")
            lowered = text.lower()
            if field == "speech":
                for phrase in GENERIC_BRIDGES:
                    if phrase in lowered:
                        report.warn(f"{beat_label}.speech contains generic bridge phrase: {phrase!r}")
        owner = raw.get("owner")
        if owner not in ALLOWED_OWNERS:
            report.error(f"{beat_label}.owner must be one of {sorted(ALLOWED_OWNERS)}")
        parsed.append((start, end, raw, index))

    if not parsed:
        return
    parsed.sort(key=lambda item: item[0])
    if parsed[0][0] > 0.05:
        report.error(f"{label} starts at {parsed[0][0]:.2f}s; frame zero must be planned")

    previous_end = parsed[0][1]
    for start, end, _, index in parsed[1:]:
        if start - previous_end > 0.05:
            report.error(f"{label} has an uncovered gap before beats[{index}] ({previous_end:.2f}s–{start:.2f}s)")
        if previous_end - start > 0.05:
            report.error(f"{label} has overlapping beats around {start:.2f}s")
        previous_end = max(previous_end, end)

    if previous_end + 0.05 < duration:
        report.error(f"{label} ends at {previous_end:.2f}s but opening duration is {duration:.2f}s")

    meaningful_second_beat = any(1.5 <= start <= 5.0 for start, _, _, _ in parsed[1:])
    if not meaningful_second_beat:
        report.error(f"{label} needs a new beat between 1.5s and 5.0s")


def validate_candidate(
    report: Report,
    raw: Any,
    index: int,
    evidence: dict[str, dict[str, Any]],
    duration: float,
) -> tuple[str, int]:
    label = f"candidates[{index}]"
    if not isinstance(raw, dict):
        report.error(f"{label} must be an object")
        return "", 0

    candidate_id = require_text(report, raw.get("id"), f"{label}.id")
    mode = raw.get("mode")
    if mode not in ALLOWED_HOOK_MODES:
        report.error(f"candidate {candidate_id or index}.mode must be one of {sorted(ALLOWED_HOOK_MODES)}")

    frame_zero = raw.get("frameZero")
    if not isinstance(frame_zero, dict):
        report.error(f"candidate {candidate_id or index}.frameZero must be an object")
    else:
        require_text(report, frame_zero.get("visual"), f"candidate {candidate_id}.frameZero.visual")
        if frame_zero.get("owner") not in ALLOWED_OWNERS:
            report.error(f"candidate {candidate_id}.frameZero.owner must be one of {sorted(ALLOWED_OWNERS)}")
        evidence_ids = frame_zero.get("evidenceIds")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            report.error(f"candidate {candidate_id}.frameZero.evidenceIds must name verified proof")
        else:
            for evidence_id in evidence_ids:
                if evidence_id not in evidence:
                    report.error(f"candidate {candidate_id} references unknown evidence id {evidence_id!r}")

    validate_beats(report, candidate_id or str(index), raw.get("beats"), duration)

    score = raw.get("score")
    total = 0
    if not isinstance(score, dict):
        report.error(f"candidate {candidate_id}.score must be an object")
    else:
        for key in SCORE_KEYS:
            value = score.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 2:
                report.error(f"candidate {candidate_id}.score.{key} must be an integer from 0 to 2")
                continue
            total += value

    comparison = raw.get("comparison")
    if comparison is not None:
        if not isinstance(comparison, dict):
            report.error(f"candidate {candidate_id}.comparison must be an object")
        elif comparison.get("samenessIsClaim") is True:
            require_text(report, comparison.get("provenance"), f"candidate {candidate_id}.comparison.provenance")

    return candidate_id, total


def validate_packet(data: Any) -> Report:
    report = Report()
    if not isinstance(data, dict):
        report.error("packet root must be an object")
        return report

    if data.get("version") != 1:
        report.error("version must be 1")
    require_text(report, data.get("project"), "project")
    require_text(report, data.get("goal"), "goal")
    require_text(report, data.get("audience"), "audience")
    require_text(report, data.get("promise"), "promise")

    run_mode = data.get("runMode")
    if run_mode not in ALLOWED_RUN_MODES:
        report.error(f"runMode must be one of {sorted(ALLOWED_RUN_MODES)}")

    duration = number(data.get("durationSeconds"))
    if duration is None or duration < 6 or duration > 10:
        report.error("durationSeconds must be a number from 6 to 10")
        duration = 8.0

    evidence = validate_evidence(report, data.get("evidence"))
    candidates = data.get("candidates")
    minimum_candidates = 1 if run_mode == "fast" else 3
    if not isinstance(candidates, list) or len(candidates) < minimum_candidates:
        report.error(f"runMode {run_mode!r} requires at least {minimum_candidates} candidate(s)")
        candidates = []

    ids: set[str] = set()
    totals: dict[str, int] = {}
    candidates_by_id: dict[str, dict[str, Any]] = {}
    for index, candidate in enumerate(candidates):
        candidate_id, total = validate_candidate(report, candidate, index, evidence, duration)
        if candidate_id:
            if candidate_id in ids:
                report.error(f"duplicate candidate id: {candidate_id}")
            ids.add(candidate_id)
            totals[candidate_id] = total
            if isinstance(candidate, dict):
                candidates_by_id[candidate_id] = candidate

    selected = data.get("selectedCandidate")
    if selected not in ids:
        report.error("selectedCandidate must reference a candidate id")
    else:
        if totals.get(selected, 0) < 9:
            report.error(f"selected candidate {selected} scores {totals.get(selected, 0)}/12; minimum is 9")
        selected_score = candidates_by_id[selected].get("score", {})
        for key in ("proof", "secondBeat", "muteTest"):
            if isinstance(selected_score, dict) and selected_score.get(key, 0) < 1:
                report.error(f"selected candidate {selected} cannot score 0 for {key}")

    windows = data.get("captionMuteWindows")
    if not isinstance(windows, list):
        report.error("captionMuteWindows must be a list")
    else:
        for index, window in enumerate(windows):
            label = f"captionMuteWindows[{index}]"
            if not isinstance(window, dict):
                report.error(f"{label} must be an object")
                continue
            start = number(window.get("start"))
            end = number(window.get("end"))
            if start is None or end is None or start < 0 or end <= start:
                report.error(f"{label} needs numeric start/end with 0 <= start < end")
            require_text(report, window.get("reason"), f"{label}.reason")

    premiere = data.get("premiere")
    if not isinstance(premiere, dict):
        report.error("premiere must be an object")
    else:
        sequence = require_text(report, premiere.get("sandboxSequence"), "premiere.sandboxSequence")
        if sequence and not sequence.startswith("HOOK-LAB__"):
            report.error("premiere.sandboxSequence must start with 'HOOK-LAB__'")

    qa = data.get("qa")
    if not isinstance(qa, dict):
        report.error("qa must be an object")
    else:
        snapshots = qa.get("snapshotTimes")
        if not isinstance(snapshots, list) or len(snapshots) < 5:
            report.error("qa.snapshotTimes must contain at least five review times")
        else:
            parsed = [number(value) for value in snapshots]
            if any(value is None for value in parsed):
                report.error("qa.snapshotTimes must be finite numbers")
            elif parsed[0] is not None and parsed[0] > 0.5:
                report.error("qa.snapshotTimes must inspect frame zero (<=0.5s)")
        if qa.get("status") not in {"pending", "pass", "fail"}:
            report.error("qa.status must be pending, pass, or fail")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Path to HOOK-PACKET.json")
    args = parser.parse_args()

    try:
        data = json.loads(args.packet.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: packet not found: {args.packet}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}", file=sys.stderr)
        return 2

    report = validate_packet(data)
    for warning in report.warnings:
        print(f"WARN: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")

    selected = data.get("selectedCandidate") if isinstance(data, dict) else None
    if report.errors:
        print(f"FAIL: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")
        return 1
    print(f"PASS: selected candidate {selected}; {len(report.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

