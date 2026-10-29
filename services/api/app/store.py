from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from fastapi import HTTPException

from .config import Settings
from .demo_data import DEMO_OBSERVATIONS, utc_now


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS observations (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_product TEXT NOT NULL,
  source_record_id TEXT NOT NULL,
  observation_type TEXT NOT NULL,
  classification TEXT NOT NULL,
  confidence_value REAL,
  confidence_meaning TEXT,
  spatial_resolution_meters REAL,
  observed_at TEXT NOT NULL,
  published_at TEXT,
  ingested_at TEXT NOT NULL,
  processing_version TEXT NOT NULL,
  forest_classification TEXT,
  quality_flags_json TEXT NOT NULL,
  geometry_json TEXT NOT NULL,
  raw_evidence_ref TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(source_id, source_record_id, processing_version)
);
CREATE INDEX IF NOT EXISTS idx_observations_org_observed ON observations(organization_id, observed_at DESC);
CREATE TABLE IF NOT EXISTS investigation_cases (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  observation_id TEXT NOT NULL REFERENCES observations(id),
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  owner_organization TEXT NOT NULL,
  reviewer TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(organization_id, observation_id)
);
CREATE INDEX IF NOT EXISTS idx_cases_org_status ON investigation_cases(organization_id, status, updated_at DESC);
CREATE TABLE IF NOT EXISTS case_events (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES investigation_cases(id),
  event_type TEXT NOT NULL,
  actor TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_case_events_case_time ON case_events(case_id, occurred_at ASC);
CREATE TABLE IF NOT EXISTS evidence_assets (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES investigation_cases(id),
  file_name TEXT NOT NULL,
  media_type TEXT NOT NULL,
  storage_key TEXT NOT NULL UNIQUE,
  sha256 TEXT NOT NULL,
  byte_size INTEGER NOT NULL,
  source_description TEXT NOT NULL,
  observed_at TEXT,
  uploaded_at TEXT NOT NULL,
  uploaded_by TEXT NOT NULL,
  integrity_status TEXT NOT NULL DEFAULT 'PENDING'
);
CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence_assets(case_id, uploaded_at ASC);
CREATE TABLE IF NOT EXISTS case_assignments (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES investigation_cases(id),
  assignee TEXT NOT NULL,
  role TEXT NOT NULL,
  assigned_by TEXT NOT NULL,
  assigned_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS case_actions (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES investigation_cases(id),
  action_type TEXT NOT NULL,
  summary TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  recorded_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS follow_up_assessments (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES investigation_cases(id),
  assessment TEXT NOT NULL,
  summary TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  recorded_by TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  aggregate_type TEXT NOT NULL,
  aggregate_id TEXT NOT NULL,
  action TEXT NOT NULL,
  actor TEXT NOT NULL,
  occurred_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_aggregate ON audit_events(aggregate_type, aggregate_id, occurred_at ASC);
"""


VALID_TRANSITIONS = {
    "NEW": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"FIELD_VERIFICATION", "REOPENED"},
    "FIELD_VERIFICATION": {"ACTION_RECORDED", "FOLLOW_UP", "REOPENED"},
    "ACTION_RECORDED": {"FOLLOW_UP", "REOPENED"},
    "FOLLOW_UP": {"CLOSED", "REOPENED"},
    "CLOSED": {"REOPENED"},
    "REOPENED": {"UNDER_REVIEW", "FIELD_VERIFICATION"},
}


class Store:
    """Small, testable persistence adapter.

    SQLite keeps the local demo self-contained. Production uses the matching
    PostGIS migration under `migrations/`; geometries remain GeoJSON at the API
    boundary so no source loses its original footprint.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._lock = threading.RLock()

    def _connection(self) -> sqlite3.Connection:
        self.settings.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.settings.database_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def prepare(self) -> None:
        with self._lock, self._connection() as connection:
            connection.executescript(SCHEMA)
            evidence_columns = {row[1] for row in connection.execute("PRAGMA table_info(evidence_assets)").fetchall()}
            if "integrity_status" not in evidence_columns:
                # Lightweight forward migration for existing local demo databases.
                connection.execute("ALTER TABLE evidence_assets ADD COLUMN integrity_status TEXT NOT NULL DEFAULT 'PENDING'")
            if self.settings.mode in {"demo", "owner_demo"}:
                self.seed_demo_observations(connection)

    def seed_demo_observations(self, connection: sqlite3.Connection | None = None) -> int:
        owns_connection = connection is None
        if owns_connection:
            connection = self._connection()
        assert connection is not None
        count = 0
        try:
            for observation in DEMO_OBSERVATIONS:
                cursor = connection.execute(
                    """INSERT OR IGNORE INTO observations (
                    id, organization_id, source_id, source_product, source_record_id,
                    observation_type, classification, confidence_value, confidence_meaning,
                    spatial_resolution_meters, observed_at, published_at, ingested_at,
                    processing_version, forest_classification, quality_flags_json,
                    geometry_json, raw_evidence_ref, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        observation["id"], observation["organization_id"], observation["source_id"],
                        observation["source_product"], observation["source_record_id"],
                        observation["observation_type"], observation["classification"],
                        observation["confidence_value"], observation["confidence_meaning"],
                        observation["spatial_resolution_meters"], observation["observed_at"],
                        observation["published_at"], observation["ingested_at"], observation["processing_version"],
                        observation["forest_classification"], json.dumps(observation["quality_flags"]),
                        json.dumps(observation["geometry"]), observation["raw_evidence_ref"], utc_now(),
                    ),
                )
                count += cursor.rowcount
            connection.commit()
            return count
        finally:
            if owns_connection:
                connection.close()

    @staticmethod
    def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        data = dict(row)
        for key in ("quality_flags_json", "geometry_json", "payload_json", "metadata_json"):
            if key in data:
                destination = key.removesuffix("_json")
                data[destination] = json.loads(data.pop(key))
        return data

    @staticmethod
    def _rows(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
        return [Store._row(row) for row in rows if row is not None]  # type: ignore[list-item]

    def _require_case(self, connection: sqlite3.Connection, case_id: str) -> dict[str, Any]:
        case = self._row(connection.execute("SELECT * FROM investigation_cases WHERE id = ?", (case_id,)).fetchone())
        if case is None:
            raise HTTPException(status_code=404, detail="Investigation case not found")
        return case

    def _audit(self, connection: sqlite3.Connection, organization_id: str, aggregate_type: str, aggregate_id: str,
               action: str, actor: str, metadata: dict[str, Any]) -> None:
        connection.execute(
            "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (str(uuid4()), organization_id, aggregate_type, aggregate_id, action, actor, utc_now(), json.dumps(metadata)),
        )

    def list_observations(self, organization_id: str, source_id: str | None = None) -> list[dict[str, Any]]:
        with self._connection() as connection:
            if source_id:
                records = connection.execute(
                    "SELECT * FROM observations WHERE organization_id = ? AND source_id = ? ORDER BY observed_at DESC",
                    (organization_id, source_id),
                ).fetchall()
            else:
                records = connection.execute(
                    "SELECT * FROM observations WHERE organization_id = ? ORDER BY observed_at DESC", (organization_id,)
                ).fetchall()
            return self._rows(records)

    def get_observation(self, organization_id: str, observation_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            observation = self._row(connection.execute(
                "SELECT * FROM observations WHERE id = ? AND organization_id = ?", (observation_id, organization_id)
            ).fetchone())
            if observation is None:
                raise HTTPException(status_code=404, detail="Observation not found")
            return observation

    def create_case(self, organization_id: str, observation_id: str, title: str, owner_organization: str,
                    reviewer: str | None, actor: str | None = None) -> dict[str, Any]:
        with self._lock, self._connection() as connection:
            self.get_observation(organization_id, observation_id)
            existing = self._row(connection.execute(
                "SELECT * FROM investigation_cases WHERE organization_id = ? AND observation_id = ?",
                (organization_id, observation_id),
            ).fetchone())
            if existing:
                return existing
            now, case_id = utc_now(), str(uuid4())
            connection.execute(
                "INSERT INTO investigation_cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (case_id, organization_id, observation_id, title, "NEW", owner_organization, reviewer, now, now),
            )
            recorded_actor = actor or reviewer or "system"
            connection.execute(
                "INSERT INTO case_events VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid4()), case_id, "CASE_CREATED", recorded_actor, now,
                 json.dumps({"status": "NEW", "observation_id": observation_id})),
            )
            self._audit(connection, organization_id, "CASE", case_id, "CASE_CREATED", recorded_actor, {"observation_id": observation_id})
            connection.commit()
            return self._require_case(connection, case_id)

    def list_cases(self, organization_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                """SELECT c.*, o.classification AS observation_classification, o.observed_at,
                o.quality_flags_json FROM investigation_cases c JOIN observations o ON c.observation_id = o.id
                WHERE c.organization_id = ? ORDER BY c.updated_at DESC""", (organization_id,)
            ).fetchall()
            return self._rows(rows)

    def get_case(self, case_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            case = self._require_case(connection, case_id)
            observation = self._row(connection.execute("SELECT * FROM observations WHERE id = ?", (case["observation_id"],)).fetchone())
            events = self._rows(connection.execute("SELECT * FROM case_events WHERE case_id = ? ORDER BY occurred_at", (case_id,)).fetchall())
            evidence = self._rows(connection.execute("SELECT * FROM evidence_assets WHERE case_id = ? ORDER BY uploaded_at", (case_id,)).fetchall())
            assignments = self._rows(connection.execute("SELECT * FROM case_assignments WHERE case_id = ? ORDER BY assigned_at", (case_id,)).fetchall())
            actions = self._rows(connection.execute("SELECT * FROM case_actions WHERE case_id = ? ORDER BY occurred_at", (case_id,)).fetchall())
            follow_ups = self._rows(connection.execute("SELECT * FROM follow_up_assessments WHERE case_id = ? ORDER BY observed_at", (case_id,)).fetchall())
            return {**case, "observation": observation, "events": events, "evidence": evidence, "assignments": assignments,
                    "actions": actions, "follow_ups": follow_ups}

    def assert_case_access(self, case_id: str, organization_id: str) -> None:
        """Keep every API operation tenant-scoped, including direct-ID routes."""
        with self._connection() as connection:
            case = self._require_case(connection, case_id)
            if case["organization_id"] != organization_id:
                # Return the same response as an absent object to avoid ID enumeration.
                raise HTTPException(status_code=404, detail="Investigation case not found")

    def transition_case(self, case_id: str, to_status: str, actor: str, note: str) -> dict[str, Any]:
        with self._lock, self._connection() as connection:
            case = self._require_case(connection, case_id)
            allowed = VALID_TRANSITIONS.get(case["status"], set())
            if to_status not in allowed:
                raise HTTPException(status_code=409, detail={"message": "Invalid case-state transition", "from": case["status"], "to": to_status, "allowed": sorted(allowed)})
            now = utc_now()
            connection.execute("UPDATE investigation_cases SET status = ?, updated_at = ? WHERE id = ?", (to_status, now, case_id))
            connection.execute("INSERT INTO case_events VALUES (?, ?, ?, ?, ?, ?)",
                               (str(uuid4()), case_id, "STATUS_CHANGED", actor, now, json.dumps({"from": case["status"], "to": to_status, "note": note})))
            self._audit(connection, case["organization_id"], "CASE", case_id, "STATUS_CHANGED", actor, {"from": case["status"], "to": to_status})
            connection.commit()
            return self._require_case(connection, case_id)

    def assign_case(self, case_id: str, assignee: str, role: str, actor: str) -> dict[str, Any]:
        with self._lock, self._connection() as connection:
            case, now, assignment_id = self._require_case(connection, case_id), utc_now(), str(uuid4())
            connection.execute("INSERT INTO case_assignments VALUES (?, ?, ?, ?, ?, ?)", (assignment_id, case_id, assignee, role, actor, now))
            connection.execute("INSERT INTO case_events VALUES (?, ?, ?, ?, ?, ?)", (str(uuid4()), case_id, "ASSIGNED", actor, now, json.dumps({"assignee": assignee, "role": role})))
            self._audit(connection, case["organization_id"], "CASE", case_id, "ASSIGNED", actor, {"assignee": assignee, "role": role})
            connection.commit()
            return self._row(connection.execute("SELECT * FROM case_assignments WHERE id = ?", (assignment_id,)).fetchone()) or {}

    def record_action(self, case_id: str, action_type: str, summary: str, actor: str, occurred_at: str | None) -> dict[str, Any]:
        with self._lock, self._connection() as connection:
            case, now, action_id = self._require_case(connection, case_id), utc_now(), str(uuid4())
            if case["status"] not in {"FIELD_VERIFICATION", "ACTION_RECORDED"}:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": "An action can be recorded only after field verification has begun.",
                        "case_status": case["status"],
                        "allowed": ["FIELD_VERIFICATION", "ACTION_RECORDED"],
                    },
                )
            connection.execute("INSERT INTO case_actions VALUES (?, ?, ?, ?, ?, ?, ?)", (action_id, case_id, action_type, summary, occurred_at or now, now, actor))
            connection.execute("INSERT INTO case_events VALUES (?, ?, ?, ?, ?, ?)", (str(uuid4()), case_id, "ACTION_RECORDED", actor, now, json.dumps({"action_type": action_type})))
            self._audit(connection, case["organization_id"], "CASE", case_id, "ACTION_RECORDED", actor, {"action_type": action_type})
            connection.commit()
            return self._row(connection.execute("SELECT * FROM case_actions WHERE id = ?", (action_id,)).fetchone()) or {}

    def record_follow_up(self, case_id: str, assessment: str, summary: str, actor: str, observed_at: str | None) -> dict[str, Any]:
        with self._lock, self._connection() as connection:
            case, now, follow_up_id = self._require_case(connection, case_id), utc_now(), str(uuid4())
            if case["status"] not in {"ACTION_RECORDED", "FOLLOW_UP"}:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": "A follow-up outcome can be recorded only after an action record exists.",
                        "case_status": case["status"],
                        "allowed": ["ACTION_RECORDED", "FOLLOW_UP"],
                    },
                )
            connection.execute("INSERT INTO follow_up_assessments VALUES (?, ?, ?, ?, ?, ?, ?)", (follow_up_id, case_id, assessment, summary, observed_at or now, now, actor))
            connection.execute("INSERT INTO case_events VALUES (?, ?, ?, ?, ?, ?)", (str(uuid4()), case_id, "FOLLOW_UP_RECORDED", actor, now, json.dumps({"assessment": assessment})))
            self._audit(connection, case["organization_id"], "CASE", case_id, "FOLLOW_UP_RECORDED", actor, {"assessment": assessment})
            connection.commit()
            return self._row(connection.execute("SELECT * FROM follow_up_assessments WHERE id = ?", (follow_up_id,)).fetchone()) or {}

    def attach_evidence(self, case_id: str, file_name: str, media_type: str, content_base64: str, source_description: str,
                        actor: str, observed_at: str | None) -> dict[str, Any]:
        try:
            raw = base64.b64decode(content_base64, validate=True)
        except Exception as error:  # noqa: BLE001 - turn malformed input into a client error
            raise HTTPException(status_code=422, detail="Evidence must be valid base64") from error
        if len(raw) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Evidence upload exceeds the 10 MiB demo limit")
        safe_name = Path(file_name).name
        if safe_name in {"", "."}:
            raise HTTPException(status_code=422, detail="Evidence file name is not safe")
        with self._lock, self._connection() as connection:
            case, now, evidence_id = self._require_case(connection, case_id), utc_now(), str(uuid4())
            sha256 = hashlib.sha256(raw).hexdigest()
            storage_key = f"{case['organization_id']}/{case_id}/{evidence_id}-{safe_name}"
            destination = self.settings.evidence_directory / storage_key
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = destination.with_name(f"{destination.name}.partial")
            temporary_path.write_bytes(raw)
            try:
                # A committed PENDING row is safer than an untracked final object:
                # the dossier will not count it until it is atomically finalized
                # and its hash is re-verified.
                connection.execute("INSERT INTO evidence_assets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (evidence_id, case_id, safe_name, media_type, storage_key, sha256, len(raw), source_description, observed_at, now, actor, "PENDING"))
                connection.commit()
            except Exception:
                temporary_path.unlink(missing_ok=True)
                raise
            try:
                temporary_path.replace(destination)
            except OSError as error:
                raise HTTPException(status_code=500, detail="Evidence object could not be finalized; it remains excluded from dossiers") from error
            connection.execute("UPDATE evidence_assets SET integrity_status = 'VERIFIED' WHERE id = ?", (evidence_id,))
            connection.execute("INSERT INTO case_events VALUES (?, ?, ?, ?, ?, ?)", (str(uuid4()), case_id, "EVIDENCE_ATTACHED", actor, now, json.dumps({"evidence_id": evidence_id, "sha256": sha256})))
            self._audit(connection, case["organization_id"], "EVIDENCE", evidence_id, "EVIDENCE_ATTACHED", actor, {"case_id": case_id, "sha256": sha256})
            connection.commit()
            return self._row(connection.execute("SELECT * FROM evidence_assets WHERE id = ?", (evidence_id,)).fetchone()) or {}

    def dossier(self, case_id: str) -> dict[str, Any]:
        case = self.get_case(case_id)
        verified_evidence_count = 0
        for asset in case["evidence"]:
            stored_status = asset.get("integrity_status", "PENDING")
            stored_file = self.settings.evidence_directory / asset["storage_key"]
            if stored_status != "VERIFIED":
                asset["dossier_integrity_status"] = "PENDING_FINALIZATION"
            elif not stored_file.is_file():
                asset["dossier_integrity_status"] = "MISSING_OBJECT"
            else:
                actual_hash = hashlib.sha256(stored_file.read_bytes()).hexdigest()
                asset["dossier_integrity_status"] = "HASH_VERIFIED" if actual_hash == asset["sha256"] else "HASH_MISMATCH"
            if asset["dossier_integrity_status"] == "HASH_VERIFIED":
                verified_evidence_count += 1
        completeness = {
            "provenance_present": bool(case["observation"] and case["observation"].get("raw_evidence_ref")),
            "evidence_asset_count": len(case["evidence"]),
            "verified_evidence_asset_count": verified_evidence_count,
            "assignment_recorded": bool(case["assignments"]),
            "action_recorded": bool(case["actions"]),
            "follow_up_recorded": bool(case["follow_ups"]),
            "human_review_required": True,
        }
        return {
            "document_type": "FORESTPROOF_EVIDENCE_DOSSIER",
            "generated_at": utc_now(),
            "verification_notice": "This dossier records submitted observations and workflow history. It does not make a legal finding or establish that any activity was unauthorized.",
            "case": case,
            "completeness": completeness,
        }

    def outcome_graph(self, organization_id: str) -> dict[str, Any]:
        cases = self.list_cases(organization_id)
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        for case in cases:
            observation_node = f"observation:{case['observation_id']}"
            case_node = f"case:{case['id']}"
            nodes.extend([
                {"id": observation_node, "type": "OBSERVATION", "label": case["observation_id"]},
                {"id": case_node, "type": "CASE", "label": case["title"], "status": case["status"]},
            ])
            edges.append({"source": observation_node, "target": case_node, "type": "GENERATED_CASE"})
            full_case = self.get_case(case["id"])
            for action in full_case["actions"]:
                action_node = f"action:{action['id']}"
                nodes.append({"id": action_node, "type": "ACTION", "label": action["action_type"]})
                edges.append({"source": case_node, "target": action_node, "type": "RECORDED_ACTION"})
            for follow_up in full_case["follow_ups"]:
                outcome_node = f"outcome:{follow_up['id']}"
                nodes.append({"id": outcome_node, "type": "OUTCOME", "label": follow_up["assessment"]})
                edges.append({"source": case_node, "target": outcome_node, "type": "FOLLOW_UP"})
        return {"nodes": nodes, "edges": edges, "notice": "Graph edges reflect recorded workflow activity, not demonstrated environmental causality."}
