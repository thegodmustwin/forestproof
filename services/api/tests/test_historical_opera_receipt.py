from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from app.historical_opera_receipt import (
    MODE,
    ROLES,
    ReceiptError,
    copy_database,
    dossier,
    ingest,
    initialize,
)


@pytest.fixture
def bundle(tmp_path: Path) -> tuple[Path, Path, dict]:
    root = tmp_path / "synthetic-input"
    root.mkdir()
    data = {
        "schema_version": 1,
        "mode": MODE,
        "granule": "OPERA_L3_DIST-ALERT-HLS_T00AAA_20200105T000000Z_20200107T000000Z_L8_30_v1",
        "row": 0,
        "column": 1,
        "observed_on": "2020-01-03",
        "assessed_on": "2020-01-05",
        "layers": {},
    }
    for role in ROLES:
        filename = f"{role}.tif"
        payload = f"SYNTHETIC PLACEHOLDER {role}".encode()
        (root / filename).write_bytes(payload)
        data["layers"][role] = {
            "filename": filename,
            "byte_count": len(payload),
            "sha256": sha256(payload).hexdigest(),
        }
    manifest = root / "manifest.json"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    original = tmp_path / "rehearsal.sqlite3"
    initialize(original)
    return original, manifest, data


def test_replay_and_copy_reproduce_dossier_without_input_files(tmp_path: Path, bundle):
    original, manifest, data = bundle
    record_id, result = ingest(original, manifest)
    first = dossier(original, record_id)
    assert result == "imported"
    assert first["owner_review"] == "pending"
    assert first["receipt"]["manifest"] == data
    assert first["receipt"]["manifest_sha256"] == sha256(manifest.read_bytes()).hexdigest()
    assert ingest(original, manifest) == (record_id, "replayed")
    assert dossier(original, record_id) == first
    with closing(sqlite3.connect(original)) as db, db:
        assert db.execute("SELECT count(*) FROM receipt").fetchone() == (1,)

    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    copy_database(original, backup)
    original.rename(tmp_path / "offline.sqlite3")
    manifest.parent.rename(tmp_path / "offline-input")
    copy_database(backup, restored)
    assert dossier(restored, record_id) == first
    with closing(sqlite3.connect(restored)) as db:
        row = db.execute(
            "SELECT manifest, status, first_date, last_date, mask, fmask FROM receipt"
        ).fetchone()
    assert row == (
        (tmp_path / "offline-input" / manifest.name).read_bytes(),
        *(f"SYNTHETIC PLACEHOLDER {role}".encode() for role in ROLES),
    )


def test_conflicting_manifest_is_rejected_atomically(bundle):
    original, manifest, data = bundle
    record_id, _ = ingest(original, manifest)
    first = dossier(original, record_id)
    payload = b"SYNTHETIC PLACEHOLDER status revision2"
    layer = data["layers"]["status"]
    (manifest.parent / layer["filename"]).write_bytes(payload)
    layer.update(byte_count=len(payload), sha256=sha256(payload).hexdigest())
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ReceiptError, match="immutable"):
        ingest(original, manifest)
    assert dossier(original, record_id) == first


def test_invalid_attachment_never_enters_the_database(bundle):
    original, manifest, data = bundle
    layer = data["layers"]["first_date"]
    (manifest.parent / layer["filename"]).write_bytes(b"!" * layer["byte_count"])
    with pytest.raises(ReceiptError, match="digest"):
        ingest(original, manifest)
    layer["filename"] = "../first_date.tif"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ReceiptError, match="schema"):
        ingest(original, manifest)
    with closing(sqlite3.connect(original)) as db, db:
        assert db.execute("SELECT count(*) FROM receipt").fetchone() == (0,)


def test_reject_real_granule_and_non_placeholder_even_with_matching_digest(bundle):
    original, manifest, data = bundle
    data["granule"] = data["granule"].replace("T00AAA", "T36MZE")
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ReceiptError, match="schema"):
        ingest(original, manifest)

    data["granule"] = data["granule"].replace("T36MZE", "T00AAA")
    payload = b"ordinary imagery bytes"
    layer = data["layers"]["mask"]
    (manifest.parent / layer["filename"]).write_bytes(payload)
    layer.update(byte_count=len(payload), sha256=sha256(payload).hexdigest())
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ReceiptError, match="synthetic placeholder"):
        ingest(original, manifest)
    with closing(sqlite3.connect(original)) as db:
        assert db.execute("SELECT count(*) FROM receipt").fetchone() == (0,)


def test_copy_and_dossier_refuse_corrupt_receipt(tmp_path: Path, bundle):
    original, manifest, _ = bundle
    record_id, _ = ingest(original, manifest)
    with closing(sqlite3.connect(original)) as db, db:
        db.execute("UPDATE receipt SET status = ?", (b"damaged",))
    copy = tmp_path / "invalid.sqlite3"
    with pytest.raises(ReceiptError, match="digest"):
        copy_database(original, copy)
    assert not copy.exists()
    with pytest.raises(ReceiptError, match="digest"):
        dossier(original, record_id)


def test_cli_uses_separate_new_database_and_safe_errors(tmp_path: Path):
    database = tmp_path / "demo.sqlite3"
    with closing(sqlite3.connect(database)) as db, db:
        db.execute("CREATE TABLE existing (test TEXT)")
    original = database.read_bytes()
    cli = [sys.executable, "-m", "app.historical_opera_receipt", str(database)]
    for command in (["init"], ["dossier", "private-record-id"]):
        result = subprocess.run([*cli, *command], capture_output=True, text=True, check=False)
        assert result.returncode == 1
        assert "OPERA rehearsal failed" in result.stderr
        assert "private-record-id" not in result.stderr
    assert database.read_bytes() == original