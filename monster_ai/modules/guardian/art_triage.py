"""Art triage — classify good / bad / real reference art from vault metadata."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING

from monster_ai.modules.guardian.privacy_firewall import sanitize_outbound, topic_anonymous_id

if TYPE_CHECKING:
    from monster_ai.modules.guardian.training_vault import TrainingVault
    from monster_ai.modules.learning.image_knowledge import ImageKnowledgeLearner

TRIAGE_LABELS = frozenset({"good", "bad", "real"})

ART_QUALITY_MARKERS = (
    "anatomy",
    "composition",
    "lighting",
    "detail",
    "texture",
    "perspective",
    "解剖",
    "構圖",
    "光影",
    "細節",
    "寫實",
)

REAL_ART_THRESHOLD = 0.85


class ArtTriageEngine:
    """Strengthen good/bad/real classification using vault metadata + network facts."""

    def __init__(
        self,
        data_dir: Path,
        *,
        training_vault: TrainingVault | None = None,
        image_learner: ImageKnowledgeLearner | None = None,
        min_quality_score: float = 0.70,
    ) -> None:
        self.root = data_dir / "network_learning"
        self.root.mkdir(parents=True, exist_ok=True)
        self.patterns_path = self.root / "art_triage.json"
        self.log_path = self.root / "art_triage.jsonl"
        self._vault = training_vault
        self._image = image_learner
        self.min_quality_score = min_quality_score

    def status(self) -> dict[str, Any]:
        patterns = self._load_patterns()
        return {
            "enabled": True,
            "min_quality_score": self.min_quality_score,
            "real_threshold": REAL_ART_THRESHOLD,
            "counts": patterns.get("counts", {}),
            "network_hints": patterns.get("network_hints", [])[:8],
            "last_run_at": patterns.get("last_run_at"),
            "vault_available": self._vault is not None,
        }

    def classify_metadata(self, meta: dict[str, Any]) -> dict[str, Any]:
        quality = meta.get("quality") or {}
        score = float(quality.get("score", 0))
        issues = [str(i) for i in (quality.get("issues") or [])]
        patterns = self._load_patterns()
        hints = patterns.get("network_hints") or []

        reasons: list[str] = []
        if score >= REAL_ART_THRESHOLD and not issues:
            triage = "real"
            reasons.append("high_score_no_issues")
        elif score >= self.min_quality_score and len(issues) <= 1:
            triage = "good"
            reasons.append("meets_quality_gate")
        else:
            triage = "bad"
            if issues:
                reasons.append(f"issues:{','.join(issues[:3])}")
            if score < self.min_quality_score:
                reasons.append("below_min_quality")

        confidence = min(1.0, max(0.35, score))
        if triage == "real":
            confidence = min(1.0, score + 0.05)
        prompt = str(meta.get("prompt", "")).lower()
        if hints and any(h in prompt for h in hints):
            confidence = min(1.0, confidence + 0.05)
            reasons.append("network_hint_match")

        return {
            "triage": triage,
            "confidence": round(confidence, 3),
            "reasons": reasons,
            "quality_score": round(score, 3),
            "issue_count": len(issues),
        }

    def apply_network_summary(self, summary: str, *, topic: str = "") -> dict[str, Any]:
        text = summary.strip().lower()
        if not text:
            return {"ok": False, "reason": "empty_summary"}

        hints: list[str] = []
        for marker in ART_QUALITY_MARKERS:
            if marker.lower() in text and marker not in hints:
                hints.append(marker)
        for match in re.findall(r"[\w\u4e00-\u9fff]{3,}", text):
            if any(k in match for k in ("anatomy", "light", "detail", "解剖", "構圖")):
                if match not in hints:
                    hints.append(match[:40])

        patterns = self._load_patterns()
        existing = patterns.get("network_hints") or []
        merged = list(dict.fromkeys(existing + hints))[:24]
        patterns["network_hints"] = merged
        patterns["last_network_topic_id"] = topic_anonymous_id(topic) if topic else None
        patterns["updated_at"] = time.time()
        self._save_patterns(patterns)

        if self._image is not None:
            self._image.merge_art_triage_patterns(
                {
                    "network_hints": merged,
                    "topic_id": patterns.get("last_network_topic_id"),
                }
            )

        safe = sanitize_outbound({"hints_added": len(hints), "topic": topic})
        self._append_log({"event": "network_summary", **safe})
        return {"ok": True, "hints": merged[:12], "hints_added": len(hints)}

    def run_from_vault(self) -> dict[str, Any]:
        if self._vault is None:
            return {"ok": False, "reason": "training_vault_disabled"}

        counts = {"good": 0, "bad": 0, "real": 0, "patched": 0, "skipped": 0}
        samples: list[dict[str, Any]] = []

        for label in ("good", "bad"):
            for entry in self._vault.list_assets(label=label):
                asset_id = str(entry.get("id", ""))
                if not asset_id:
                    counts["skipped"] += 1
                    continue
                meta = self._vault.read_asset_metadata(asset_id)
                if not meta:
                    counts["skipped"] += 1
                    continue

                triage = self.classify_metadata(meta)
                triage_label = str(triage.get("triage", "bad"))
                if triage_label in counts:
                    counts[triage_label] += 1

                patch = {
                    "art_triage": triage_label,
                    "art_triage_confidence": triage.get("confidence"),
                    "art_triage_reasons": triage.get("reasons"),
                    "art_triage_source": "guardian_art_triage",
                    "art_triage_at": time.time(),
                }
                if self._vault.patch_asset_metadata(asset_id, patch):
                    counts["patched"] += 1
                samples.append(
                    sanitize_outbound(
                        {
                            "asset_id": asset_id,
                            "triage": triage_label,
                            "confidence": triage.get("confidence"),
                        }
                    )
                )

        patterns = self._load_patterns()
        patterns["counts"] = {
            "good": counts["good"],
            "bad": counts["bad"],
            "real": counts["real"],
            "patched": counts["patched"],
        }
        patterns["last_run_at"] = time.time()
        self._save_patterns(patterns)

        if self._image is not None:
            self._image.merge_art_triage_patterns(patterns)
            self._image.ingest_triage_summary(counts)

        summary_text = json.dumps(
            sanitize_outbound({"counts": counts, "samples": samples[:6]}),
            ensure_ascii=False,
        )
        self._store_vault_summary(summary_text, counts)

        self._append_log({"event": "vault_run", "counts": counts})
        return {
            "ok": True,
            "counts": counts,
            "samples": samples[:10],
            "network_hints": patterns.get("network_hints", [])[:8],
        }

    def _store_vault_summary(self, content: str, counts: dict[str, int]) -> None:
        if self._vault is None:
            return
        try:
            self._vault.store_text_asset(
                label="prompt",
                name=f"art_triage_{int(time.time())}",
                content=content[:4000],
                metadata={
                    "source": "art_triage",
                    "counts": counts,
                },
            )
        except PermissionError:
            pass

    def _load_patterns(self) -> dict[str, Any]:
        default: dict[str, Any] = {
            "network_hints": [],
            "counts": {"good": 0, "bad": 0, "real": 0, "patched": 0},
            "last_run_at": None,
        }
        if not self.patterns_path.is_file():
            return default
        try:
            data = json.loads(self.patterns_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else default
        except json.JSONDecodeError:
            return default

    def _save_patterns(self, data: dict[str, Any]) -> None:
        self.patterns_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _append_log(self, record: dict[str, Any]) -> None:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")