"""Toddler-style progressive learning — encouragement, gentle correction, Grok supervision."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from monster_ai.modules.guardian.grok_supervisor import GrokSupervisor

STAGES = ("infant", "toddler", "preschool", "school")
STAGE_THRESHOLDS = {
    "infant": {"positive_feedback": 0},
    "toddler": {"positive_feedback": 10},
    "preschool": {"art_triage_days": 7, "quality_passes": 30},
    "school": {"quality_success_rate": 0.98},
}


class ToddlerLearningEngine:
    """Treat Guardian Ai like a human toddler — gradual growth, praise, gentle fixes."""

    def __init__(self, data_dir: Path, supervisor: GrokSupervisor | None = None) -> None:
        self.root = data_dir / "toddler"
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path = self.root / "state.json"
        self.log_path = self.root / "events.jsonl"
        self._supervisor = supervisor

    def _load(self) -> dict[str, Any]:
        if not self.state_path.is_file():
            return self._default_state()
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else self._default_state()
        except (json.JSONDecodeError, OSError):
            return self._default_state()

    def _default_state(self) -> dict[str, Any]:
        return {
            "stage": "infant",
            "milestones": {
                "positive_feedback": 0,
                "quality_passes": 0,
                "quality_attempts": 0,
                "art_triage_stable_days": 0,
            },
            "encouragement_log": [],
            "gentle_corrections": [],
            "grok_directives": [],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _save(self, state: dict[str, Any]) -> None:
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def _append_event(self, event: dict[str, Any]) -> None:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def status(self) -> dict[str, Any]:
        state = self._load()
        m = state.get("milestones") or {}
        attempts = max(int(m.get("quality_attempts", 0)), 1)
        rate = int(m.get("quality_passes", 0)) / attempts
        return {
            "stage": state.get("stage", "infant"),
            "milestones": m,
            "quality_success_rate": round(rate, 4),
            "encouragement_count": len(state.get("encouragement_log") or []),
            "correction_count": len(state.get("gentle_corrections") or []),
            "next_stage": self._next_stage_hint(state),
            "network_learning_unlocked": state.get("stage") in {"preschool", "school"},
        }

    def _next_stage_hint(self, state: dict[str, Any]) -> str | None:
        stage = state.get("stage", "infant")
        m = state.get("milestones") or {}
        if stage == "infant":
            need = STAGE_THRESHOLDS["toddler"]["positive_feedback"] - int(m.get("positive_feedback", 0))
            return "toddler" if need <= 0 else f"toddler in {need} more positive feedback"
        if stage == "toddler":
            need = STAGE_THRESHOLDS["preschool"]["quality_passes"] - int(m.get("quality_passes", 0))
            return "preschool" if need <= 0 else f"preschool after {max(need, 0)} more quality passes"
        if stage == "preschool":
            return "school when quality success rate >= 98%"
        return None

    def record_positive_feedback(self, *, reason: str = "user_praise") -> dict[str, Any]:
        state = self._load()
        m = state.setdefault("milestones", {})
        m["positive_feedback"] = int(m.get("positive_feedback", 0)) + 1
        praise = {
            "at": datetime.now(timezone.utc).isoformat(),
            "type": "praise",
            "reason": reason,
            "message": "做得好！繼續保持。 / Great job — keep learning!",
        }
        logs = state.setdefault("encouragement_log", [])
        logs.append(praise)
        state["encouragement_log"] = logs[-50:]
        self._maybe_promote(state)
        self._save(state)
        self._append_event({"event": "praise", **praise})
        return {"ok": True, "praise": praise, "status": self.status()}

    def record_quality_result(self, *, passed: bool, score: float) -> dict[str, Any]:
        state = self._load()
        m = state.setdefault("milestones", {})
        m["quality_attempts"] = int(m.get("quality_attempts", 0)) + 1
        correction: dict[str, Any] | None = None
        if passed:
            m["quality_passes"] = int(m.get("quality_passes", 0)) + 1
            praise = {
                "at": datetime.now(timezone.utc).isoformat(),
                "type": "quality_pass",
                "reason": f"score={score:.2f}",
                "message": "品質達標，做得好！",
            }
            logs = state.setdefault("encouragement_log", [])
            logs.append(praise)
            state["encouragement_log"] = logs[-50:]
        else:
            correction = {
                "at": datetime.now(timezone.utc).isoformat(),
                "issue": "quality_low",
                "score": score,
                "suggestion": "讓我們再試一次，調整提示詞或參數。 / Let's try again with a refined prompt.",
            }
            fixes = state.setdefault("gentle_corrections", [])
            fixes.append(correction)
            state["gentle_corrections"] = fixes[-50:]
        self._maybe_promote(state)
        self._save(state)
        self._append_event({"event": "quality", "passed": passed, "score": score})
        return {"ok": True, "passed": passed, "correction": correction, "status": self.status()}

    def record_art_triage_day(self, *, stable: bool) -> dict[str, Any]:
        state = self._load()
        m = state.setdefault("milestones", {})
        if stable:
            m["art_triage_stable_days"] = int(m.get("art_triage_stable_days", 0)) + 1
        else:
            m["art_triage_stable_days"] = 0
        self._maybe_promote(state)
        self._save(state)
        return {"ok": True, "stable_days": m.get("art_triage_stable_days", 0), "status": self.status()}

    def _maybe_promote(self, state: dict[str, Any]) -> None:
        stage = state.get("stage", "infant")
        m = state.get("milestones") or {}
        attempts = max(int(m.get("quality_attempts", 0)), 1)
        rate = int(m.get("quality_passes", 0)) / attempts

        if stage == "infant" and int(m.get("positive_feedback", 0)) >= STAGE_THRESHOLDS["toddler"]["positive_feedback"]:
            state["stage"] = "toddler"
        elif stage == "toddler" and int(m.get("quality_passes", 0)) >= STAGE_THRESHOLDS["preschool"]["quality_passes"]:
            state["stage"] = "preschool"
        elif (
            stage == "preschool"
            and int(m.get("art_triage_stable_days", 0)) >= STAGE_THRESHOLDS["preschool"]["art_triage_days"]
            and rate >= 0.85
        ):
            state["stage"] = "school" if rate >= STAGE_THRESHOLDS["school"]["quality_success_rate"] else "preschool"
        elif stage == "preschool" and rate >= STAGE_THRESHOLDS["school"]["quality_success_rate"]:
            state["stage"] = "school"

    async def progress_with_grok(self, learning_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        state = self._load()
        snapshot = learning_snapshot or {}
        grok_note: dict[str, Any] = {}
        if self._supervisor is not None:
            grok_note = await self._supervisor.review_toddler_progress(
                stage=state.get("stage", "infant"),
                milestones=state.get("milestones") or {},
                learning_snapshot=snapshot,
            )
            directives = state.setdefault("grok_directives", [])
            directives.append(grok_note)
            state["grok_directives"] = directives[-20:]
            if grok_note.get("stage_recommendation") in STAGES:
                state["stage"] = grok_note["stage_recommendation"]
        self._save(state)
        return {
            "ok": True,
            "status": self.status(),
            "grok": grok_note,
            "latest_praise": (state.get("encouragement_log") or [])[-1:] or [],
            "latest_correction": (state.get("gentle_corrections") or [])[-1:] or [],
        }