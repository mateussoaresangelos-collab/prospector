"""SQLite persistence layer for Prospector leads and searches."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from prospector.config import DB_FILE
from prospector.models.lead import Lead


class DBClient:
    """A simple SQLite client for lead persistence."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or DB_FILE)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL,
                lead_count INTEGER NOT NULL,
                website_count INTEGER NOT NULL,
                email_count INTEGER NOT NULL,
                instagram_count INTEGER NOT NULL,
                average_score REAL NOT NULL,
                duration_seconds REAL NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id INTEGER NOT NULL,
                name TEXT,
                category TEXT,
                city TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                website TEXT,
                instagram TEXT,
                linkedin TEXT,
                facebook TEXT,
                whatsapp TEXT,
                has_website INTEGER,
                score INTEGER,
                status TEXT,
                favorite INTEGER,
                notes TEXT,
                ai_message TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY(search_id) REFERENCES searches(id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            UPDATE leads
            SET status = 'Novo'
            WHERE status IN ('Com email', 'Com website', 'Sem email')
            """
        )
        self.connection.commit()

    def save_search(
        self,
        city: str,
        category: str,
        leads: list[Lead],
        duration_seconds: float,
    ) -> int:
        now = datetime.utcnow().isoformat()
        website_count = sum(1 for lead in leads if lead.website.strip())
        email_count = sum(1 for lead in leads if lead.email.strip())
        instagram_count = sum(1 for lead in leads if lead.instagram.strip())
        average_score = float(sum(lead.score for lead in leads) / len(leads)) if leads else 0.0

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO searches (
                city, category, created_at, lead_count,
                website_count, email_count, instagram_count,
                average_score, duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                city,
                category,
                now,
                len(leads),
                website_count,
                email_count,
                instagram_count,
                average_score,
                duration_seconds,
            ),
        )
        search_id = cursor.lastrowid

        for lead in leads:
            lead.search_id = search_id
            lead.created_at = now
            lead.updated_at = now
            cursor.execute(
                """
                INSERT INTO leads (
                    search_id, name, category, city, address, phone, email,
                    website, instagram, linkedin, facebook, whatsapp,
                    has_website, score, status, favorite, notes, ai_message,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    search_id,
                    lead.name,
                    lead.category,
                    lead.city,
                    lead.address,
                    lead.phone,
                    lead.email,
                    lead.website,
                    lead.instagram,
                    lead.linkedin,
                    lead.facebook,
                    lead.whatsapp,
                    int(lead.has_website),
                    lead.score,
                    lead.status,
                    int(lead.favorite),
                    lead.notes,
                    lead.ai_message,
                    now,
                    now,
                ),
            )
            lead.id = cursor.lastrowid

        self.connection.commit()
        return search_id

    def get_searches(self) -> list[dict[str, Any]]:
        cursor = self.connection.cursor()
        rows = cursor.execute(
            "SELECT * FROM searches ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def get_last_search(self, city: str, category: str) -> tuple[dict[str, Any], list[Lead]] | None:
        cursor = self.connection.cursor()
        row = cursor.execute(
            """
            SELECT * FROM searches
            WHERE city = ? AND category = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (city, category),
        ).fetchone()
        if row is None:
            return None
        search = dict(row)
        leads = self.get_leads_for_search(search["id"])
        return search, leads

    def get_search_by_id(self, search_id: int) -> dict[str, Any] | None:
        cursor = self.connection.cursor()
        row = cursor.execute(
            "SELECT * FROM searches WHERE id = ?",
            (search_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_leads_for_search(self, search_id: int) -> list[Lead]:
        cursor = self.connection.cursor()
        rows = cursor.execute(
            "SELECT * FROM leads WHERE search_id = ? ORDER BY score DESC, name ASC",
            (search_id,),
        ).fetchall()
        return [Lead.from_row(row) for row in rows]

    def filter_leads(
        self,
        city: str | None = None,
        category: str | None = None,
        website: str | None = None,
        email: str | None = None,
        instagram: str | None = None,
        status: str | None = None,
        favorite: bool | None = None,
        search_id: int | None = None,
    ) -> list[Lead]:
        query = "SELECT * FROM leads"
        conditions: list[str] = []
        parameters: list[Any] = []

        if search_id is not None:
            conditions.append("search_id = ?")
            parameters.append(search_id)
        if city:
            conditions.append("city LIKE ?")
            parameters.append(f"%{city}%")
        if category:
            conditions.append("category LIKE ?")
            parameters.append(f"%{category}%")
        if website is not None:
            conditions.append("has_website = ?")
            parameters.append(1 if website == "Sim" else 0)
        if email is not None:
            conditions.append("email != ''" if email == "Sim" else "email = ''")
        if instagram is not None:
            conditions.append("instagram != ''" if instagram == "Sim" else "instagram = ''")
        if status and status != "Todos":
            conditions.append("status = ?")
            parameters.append(status)
        if favorite is not None:
            conditions.append("favorite = ?")
            parameters.append(int(favorite))

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY score DESC, name ASC"

        rows = self.connection.cursor().execute(query, tuple(parameters)).fetchall()
        return [Lead.from_row(row) for row in rows]

    def update_lead(self, lead: Lead) -> None:
        if lead.id is None:
            return
        lead.updated_at = datetime.utcnow().isoformat()
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE leads SET
                name = ?,
                category = ?,
                city = ?,
                address = ?,
                phone = ?,
                email = ?,
                website = ?,
                instagram = ?,
                linkedin = ?,
                facebook = ?,
                whatsapp = ?,
                has_website = ?,
                score = ?,
                status = ?,
                favorite = ?,
                notes = ?,
                ai_message = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                lead.name,
                lead.category,
                lead.city,
                lead.address,
                lead.phone,
                lead.email,
                lead.website,
                lead.instagram,
                lead.linkedin,
                lead.facebook,
                lead.whatsapp,
                int(lead.has_website),
                lead.score,
                lead.status,
                int(lead.favorite),
                lead.notes,
                lead.ai_message,
                lead.updated_at,
                lead.id,
            ),
        )
        self.connection.commit()

    def delete_lead(self, lead_id: int) -> None:
        self.connection.cursor().execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        self.connection.commit()

    def delete_search(self, search_id: int) -> None:
        self.connection.cursor().execute("DELETE FROM leads WHERE search_id = ?", (search_id,))
        self.connection.cursor().execute("DELETE FROM searches WHERE id = ?", (search_id,))
        self.connection.commit()
