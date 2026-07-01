"""Guardian art triage (G5b) tests."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from monster_ai.app import create_app
from monster_ai.config import GuardianSettings, ImageQualitySettings, load_settings
from monster_ai.modules.guardian.art_triage import ArtTriageEngine
from monster_ai.modules.guardian.key_manager import TrainingKeyManager
from monster_ai.modules.guardian.training_vault import TrainingVault
from monster_ai.modules.image.quality import QualityReport
from monster_ai.modules.image.quality_store import QualityStore
from monster_ai.modules.learning.image_knowledge import ImageKnowledgeLearner
from monster_ai.modules.learning.store import LearningStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "guardian:\n"
        "  enabled: true\n"
        "  data_dir: ./data/guardian\n"
        "  network_learning:\n"
        "    enabled: true\n"
        "    art_triage_enabled: true\n"
        "    schedule_windows:\n"
        '      - "00:00-23:59"\n',
        encoding="utf-8",
    )
    settings = load_settings(cfg)
    settings.protection.monsterlock.enabled = False
    settings.protection.monsterlock.self_destruct_enabled = False
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def vault_setup(tmp_path: Path):
    settings = GuardianSettings(
        data_dir=str(tmp_path / "guardian"),
        training_encryption_enabled=True,
        bind_hardware_key=True,
        require_user_passphrase=False,
    )
    km = TrainingKeyManager(settings, tmp_path, hardware_fingerprint="test-hw-fp-art")
    km.unlock(None)
    vault = TrainingVault(tmp_path / "guardian", km)
    return vault


def test_classify_real_good_bad():
    engine = ArtTriageEngine(Path("./data/guardian"), min_quality_score=0.70)
    real = engine.classify_metadata({"quality": {"score": 0.92, "issues": []}})
    good = engine.classify_metadata({"quality": {"score": 0.75, "issues": ["low_edge"]}})
    bad = engine.classify_metadata({"quality": {"score": 0.45, "issues": ["black_image", "noise_wall"]}})
    assert real["triage"] == "real"
    assert good["triage"] == "good"
    assert bad["triage"] == "bad"


def test_apply_network_summary_extracts_hints(tmp_path):
    engine = ArtTriageEngine(tmp_path / "guardian")
    result = engine.apply_network_summary(
        "Strong anatomy and composition improve digital art quality.",
        topic="digital art anatomy",
    )
    assert result["ok"] is True
    assert result["hints_added"] >= 1
    status = engine.status()
    assert len(status["network_hints"]) >= 1


def test_run_from_vault_patches_metadata(vault_setup, tmp_path):
    vault = vault_setup
    qdir = tmp_path / "quality"
    store = QualityStore(
        str(qdir),
        ImageQualitySettings(data_dir=str(qdir)),
        training_vault=vault,
        encrypt_training=True,
    )
    src = tmp_path / "good.png"
    Image.fromarray(np.zeros((16, 16, 3), dtype=np.uint8)).save(src)
    store.save_good(
        src,
        prompt="masterpiece, detailed anatomy",
        negative="",
        report=QualityReport(passed=True, score=0.91),
        checkpoint="ckpt",
        attempt=0,
    )

    from monster_ai.config import LearningSettings

    learning_store = LearningStore(str(tmp_path / "learning"))
    image_learner = ImageKnowledgeLearner(
        learning_store,
        ImageQualitySettings(data_dir=str(qdir)),
        LearningSettings(),
    )
    engine = ArtTriageEngine(
        tmp_path / "guardian",
        training_vault=vault,
        image_learner=image_learner,
        min_quality_score=0.70,
    )
    result = engine.run_from_vault()
    assert result["ok"] is True
    assert result["counts"]["patched"] >= 1
    assert result["counts"]["real"] >= 1

    asset_id = vault.list_assets("good")[0]["id"]
    meta = vault.read_asset_metadata(asset_id)
    assert meta is not None
    assert meta.get("art_triage") == "real"
    assert meta.get("art_triage_source") == "guardian_art_triage"


def test_patch_asset_metadata(vault_setup, tmp_path):
    vault = vault_setup
    src = tmp_path / "img.png"
    Image.fromarray(np.zeros((8, 8, 3), dtype=np.uint8)).save(src)
    vault.store_image_asset(src, label="bad", metadata={"label": "bad", "quality": {"score": 0.3}})
    asset_id = vault.list_assets("bad")[0]["id"]
    assert vault.patch_asset_metadata(asset_id, {"art_triage": "bad", "art_triage_confidence": 0.8})
    meta = vault.read_asset_metadata(asset_id)
    assert meta is not None
    assert meta["art_triage"] == "bad"


def test_art_triage_api(client):
    r = client.get("/api/guardian/network-learning/art-triage/status")
    assert r.status_code == 200
    assert r.json()["enabled"] is True


def test_art_triage_run_api(client):
    r = client.post("/api/guardian/network-learning/art-triage/run")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False or "counts" in data


def test_trigger_includes_art_triage(client):
    client.post("/api/guardian/network-learning/consent", json={"consented": True})
    with patch(
        "monster_ai.modules.learning.web_knowledge.WebKnowledgeLearner.learn",
        new_callable=AsyncMock,
        return_value={
            "ok": True,
            "facts_added": 2,
            "summary": "anatomy and composition for digital art",
            "cached": False,
        },
    ):
        r = client.post(
            "/api/guardian/network-learning/trigger",
            json={"force": True, "topics": ["digital art quality"]},
        )
    assert r.status_code == 200
    assert "art_triage" in r.json()