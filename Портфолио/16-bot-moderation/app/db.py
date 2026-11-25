"""Database abstraction supporting SQLite (local) and PostgreSQL (prod).

The driver is chosen via configuration (``DB_DRIVER``).  Both backends expose
the same tiny async API so the repository layer stays driver-agnostic.

All queries are written with ``?`` placeholders; the PostgreSQL backend
rewrites them to ``$1, $2, ...`` on the fly.  Timestamps are stored as UNIX
epoch seconds (BIGINT / INTEGER) to avoid cross-database datetime typing
differences.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from .config import Config


def _pg_translate(sql: str) -> str:
    """Rewrite ``?`` placeholders to PostgreSQL ``$1, $2, ...`` form."""
    out: List[str] = []
    idx = 0
    for ch in sql:
        if ch == "?":
            idx += 1
            out.append("$%d" % idx)
        else:
            out.append(ch)
    return "".join(out)


class Database:
    """Common interface implemented by both backends."""

    driver: str = ""

    async def connect(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    async def close(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    async def executescript(self, script: str) -> None:  # pragma: no cover
        raise NotImplementedError

    async def execute(self, sql: str, *params: Any) -> None:  # pragma: no cover
        raise NotImplementedError

    async def fetchone(self, sql: str, *params: Any) -> Optional[Dict[str, Any]]:  # pragma: no cover
        raise NotImplementedError

    async def fetchall(self, sql: str, *params: Any) -> List[Dict[str, Any]]:  # pragma: no cover
        raise NotImplementedError

    async def insert(self, sql: str, *params: Any) -> int:  # pragma: no cover
        raise NotImplementedError


class SqliteDatabase(Database):
    driver = "sqlite"

    def __init__(self, path: str) -> None:
        self._path = path
        self._conn = None  # type: ignore[assignment]

    async def connect(self) -> None:
        import aiosqlite

        # Ensure parent directory exists for file-based DBs.
        parent = os.path.dirname(os.path.abspath(self._path))
        if parent and self._path != ":memory:":
            os.makedirs(parent, exist_ok=True)
        self._conn = await aiosqlite.connect(self._path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA foreign_keys = ON")
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def executescript(self, script: str) -> None:
        assert self._conn is not None
        await self._conn.executescript(script)
        await self._conn.commit()

    async def execute(self, sql: str, *params: Any) -> None:
        assert self._conn is not None
        await self._conn.execute(sql, params)
        await self._conn.commit()

    async def fetchone(self, sql: str, *params: Any) -> Optional[Dict[str, Any]]:
        assert self._conn is not None
        async with self._conn.execute(sql, params) as cur:
            row = await cur.fetchone()
            return dict(row) if row is not None else None

    async def fetchall(self, sql: str, *params: Any) -> List[Dict[str, Any]]:
        assert self._conn is not None
        async with self._conn.execute(sql, params) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def insert(self, sql: str, *params: Any) -> int:
        assert self._conn is not None
        # Caller SQL ends with "RETURNING id". The returned row must be consumed
        # before commit, otherwise SQLite reports "SQL statements in progress".
        cur = await self._conn.execute(sql, params)
        row = await cur.fetchone()
        new_id = int(row[0]) if row is not None else int(cur.lastrowid)
        await cur.close()
        await self._conn.commit()
        return new_id


class PostgresDatabase(Database):
    driver = "postgres"

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._pool = None  # type: ignore[assignment]

    async def connect(self) -> None:
        import asyncpg

        self._pool = await asyncpg.create_pool(self._dsn, min_size=1, max_size=5)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def executescript(self, script: str) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(script)

    async def execute(self, sql: str, *params: Any) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(_pg_translate(sql), *params)

    async def fetchone(self, sql: str, *params: Any) -> Optional[Dict[str, Any]]:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(_pg_translate(sql), *params)
            return dict(row) if row is not None else None

    async def fetchall(self, sql: str, *params: Any) -> List[Dict[str, Any]]:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(_pg_translate(sql), *params)
            return [dict(r) for r in rows]

    async def insert(self, sql: str, *params: Any) -> int:
        assert self._pool is not None
        # Caller SQL must end with "RETURNING id".
        async with self._pool.acquire() as conn:
            val = await conn.fetchval(_pg_translate(sql), *params)
            return int(val)


def build_dsn(cfg: Config) -> str:
    return (
        "postgresql://%s:%s@%s:%d/%s"
        % (cfg.pg_user, cfg.pg_password, cfg.pg_host, cfg.pg_port, cfg.pg_database)
    )


def get_database(cfg: Config) -> Database:
    """Factory: pick a backend based on configuration."""
    if cfg.db_driver == "postgres":
        return PostgresDatabase(build_dsn(cfg))
    return SqliteDatabase(cfg.sqlite_path)
