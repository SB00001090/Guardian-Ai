"""Guardian Ai toddler learning tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from monster_ai.app import create_app
from monster_ai.config import load_settings


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "guardian:\n  enabled: true\n  data_dir: ./data/guardian\n",
        encoding="utf-8",
    )
    settings = load_settings(cfg)
    settings.protection.monsterlock.enabled = False
    settings.protection.monsterlock.self_destruct_enabled = False
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


def test_toddler_status_default_infant(client):
    r = client.get("/api/guardian/learning/toddler/status")
    assert r.status_code == 200
    data = r.json()
    assert data["stage"] == "infant"


def test_toddler_feedback_and_quality(client):
    fb = client.post("/api/guardian/learning/toddler/feedback", json={"reason": "test"})
    assert fb.status_code == 200
    gate = client.post("/api/guardian/quality/gate", json={"score": 0.85})
    assert gate.status_code == 200
    assert gate.json()["passed"] is True
    assert "toddler" in gate.json()


def test_guardian_status_no_callguard(client):
    r = client.get("/api/guardian/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("connection_policy") == "tunnel_or_usb_only"
    assert "toddler_learning" in data