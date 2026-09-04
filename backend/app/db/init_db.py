import sqlite3
import json
from pathlib import Path
from typing import Optional
from app.config import settings
from app.models.db_models import SessionRecord, SessionState


def get_db_path() -> Path:
    base_dir = Path(__file__).resolve().parent.parent.parent  # backend/
    db_path = base_dir / settings.SQLITE_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create session store tables if they don't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            state TEXT NOT NULL,
            target_node_id TEXT NOT NULL,
            diagnosed_gap_node_id TEXT,
            current_candidate_node_id TEXT,
            probing_question TEXT,
            traversal_path TEXT NOT NULL,
            mastered_nodes TEXT NOT NULL,
            history TEXT NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        );
        """)
        conn.commit()


def save_session(session: SessionRecord) -> SessionRecord:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO sessions (
            session_id, state, target_node_id, diagnosed_gap_node_id,
            current_candidate_node_id, probing_question, traversal_path,
            mastered_nodes, history, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            state = excluded.state,
            target_node_id = excluded.target_node_id,
            diagnosed_gap_node_id = excluded.diagnosed_gap_node_id,
            current_candidate_node_id = excluded.current_candidate_node_id,
            probing_question = excluded.probing_question,
            traversal_path = excluded.traversal_path,
            mastered_nodes = excluded.mastered_nodes,
            history = excluded.history,
            updated_at = excluded.updated_at
        """, (
            session.session_id,
            session.state.value,
            session.target_node_id,
            session.diagnosed_gap_node_id,
            session.current_candidate_node_id,
            session.probing_question,
            json.dumps(session.traversal_path),
            json.dumps(session.mastered_nodes),
            json.dumps(session.history),
            session.created_at,
            session.updated_at,
        ))
        conn.commit()
    return session


def get_session(session_id: str) -> Optional[SessionRecord]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None

        return SessionRecord(
            session_id=row["session_id"],
            state=SessionState(row["state"]),
            target_node_id=row["target_node_id"],
            diagnosed_gap_node_id=row["diagnosed_gap_node_id"],
            current_candidate_node_id=row["current_candidate_node_id"],
            probing_question=row["probing_question"],
            traversal_path=json.loads(row["traversal_path"]),
            mastered_nodes=json.loads(row["mastered_nodes"]),
            history=json.loads(row["history"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
