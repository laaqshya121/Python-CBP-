"""SQLite persistence — alerts, congestion, queues, routes, chat."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from smartvenue_ai.config import ROOT

DB_PATH = ROOT / "data" / "smartvenue.db"


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            gate_wait REAL, food_wait REAL, washroom_wait REAL
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, zone TEXT, message TEXT, severity TEXT
        );
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, origin TEXT, destination TEXT, minutes INTEGER
        );
        CREATE TABLE IF NOT EXISTS congestion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, zone TEXT, density REAL, score REAL
        );
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, role TEXT, content TEXT
        );
        CREATE TABLE IF NOT EXISTS queue_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL, category TEXT, location TEXT, wait_min INTEGER
        );
    """)
    conn.commit()


def save_metrics(gate: float, food: float, wash: float) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO metrics (ts, gate_wait, food_wait, washroom_wait) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), gate, food, wash),
        )
        c.commit()


def log_alert(zone: str, message: str, severity: str) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO alerts (ts, zone, message, severity) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), zone, message, severity),
        )
        c.commit()


def log_route(origin: str, dest: str, minutes: int) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO routes (ts, origin, destination, minutes) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), origin, dest, minutes),
        )
        c.commit()


def log_congestion(zone: str, density: float, score: float) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO congestion_history (ts, zone, density, score) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), zone, density, score),
        )
        c.commit()


def log_chat(role: str, content: str) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO chat_history (ts, role, content) VALUES (?,?,?)",
            (datetime.now().isoformat(), role, content),
        )
        c.commit()


def log_queue_snapshot(category: str, location: str, wait_min: int) -> None:
    with connect() as c:
        c.execute(
            "INSERT INTO queue_snapshots (ts, category, location, wait_min) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), category, location, wait_min),
        )
        c.commit()


def recent_chats(limit: int = 20) -> List[Tuple[str, str]]:
    with connect() as c:
        rows = c.execute(
            "SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [(r["role"], r["content"]) for r in reversed(rows)]
