"""
db.py  –  Oracle 26ai database layer
All SQL is parameterised; no hardcoded schema names (read from env/config).
"""
from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Generator

import oracledb
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
#  Config — all values from environment variables
# ─────────────────────────────────────────────────────────
class DBConfig:
    user: str        = os.environ["ORA_USER"]
    password: str    = os.environ["ORA_PASSWORD"]
    host: str        = os.environ.get("ORA_HOST", "localhost")
    port: int        = int(os.environ.get("ORA_PORT", 1521))
    service: str     = os.environ["ORA_SERVICE"]
    schema: str      = os.environ.get("ORA_SCHEMA", "DEV").upper()
    doc_table: str   = os.environ.get("ORA_DOC_TABLE",   "AITEST_DOCUMENTATION_TAB").upper()
    chunk_table: str = os.environ.get("ORA_CHUNK_TABLE", "AITEST_DOCUMENTATION_CHUNKS").upper()
    onnx_model: str  = os.environ.get("ORA_ONNX_MODEL",  "ALL_MINILM_L12_V2").upper()
    top_k: int       = int(os.environ.get("VECTOR_TOP_K",    5))
    distance: str    = os.environ.get("VECTOR_DISTANCE", "COSINE").upper()

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service}"

    @property
    def fq_doc_table(self) -> str:
        return f"{self.schema}.{self.doc_table}"

    @property
    def fq_chunk_table(self) -> str:
        return f"{self.schema}.{self.chunk_table}"

    @property
    def fq_onnx_model(self) -> str:
        return f"{self.schema}.{self.onnx_model}"

    # Constraint names derived from table names — unique, no collisions on recreate
    @property
    def pk_chunk(self) -> str:
        return f"PK_{self.chunk_table[:20]}"

    @property
    def fk_chunk_doc(self) -> str:
        return f"FK_{self.chunk_table[:15]}_DOC"


cfg = DBConfig()


# ─────────────────────────────────────────────────────────
#  Connection pool (module-level singleton)
# ─────────────────────────────────────────────────────────
_pool: oracledb.ConnectionPool | None = None


def get_pool() -> oracledb.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = oracledb.create_pool(
            user=cfg.user,
            password=cfg.password,
            dsn=cfg.dsn,
            min=1,
            max=4,
            increment=1,
        )
        logger.info("Oracle connection pool created  dsn=%s  user=%s", cfg.dsn, cfg.user)
    return _pool


@contextmanager
def get_conn() -> Generator[oracledb.Connection, None, None]:
    conn = get_pool().acquire()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        get_pool().release(conn)


# ─────────────────────────────────────────────────────────
#  DDL inspection helpers
# ─────────────────────────────────────────────────────────
def _table_exists(cur: oracledb.Cursor, table: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM all_tables "
        "WHERE owner = :s AND table_name = :t",
        {"s": cfg.schema, "t": table.upper()},
    )
    return cur.fetchone()[0] > 0


def _column_exists(cur: oracledb.Cursor, table: str, column: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM all_tab_columns "
        "WHERE owner = :s AND table_name = :t AND column_name = :c",
        {"s": cfg.schema, "t": table.upper(), "c": column.upper()},
    )
    return cur.fetchone()[0] > 0


def _index_exists(cur: oracledb.Cursor, table: str, index_type: str = "VECTOR") -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM all_indexes "
        "WHERE owner = :s AND table_name = :t AND index_type = :i",
        {"s": cfg.schema, "t": table.upper(), "i": index_type},
    )
    return cur.fetchone()[0] > 0


def _constraint_exists(cur: oracledb.Cursor, constraint_name: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM all_constraints "
        "WHERE owner = :s AND constraint_name = :c",
        {"s": cfg.schema, "c": constraint_name.upper()},
    )
    return cur.fetchone()[0] > 0


def _sequence_exists(cur: oracledb.Cursor, seq_name: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM all_sequences "
        "WHERE sequence_owner = :s AND sequence_name = :n",
        {"s": cfg.schema, "n": seq_name.upper()},
    )
    return cur.fetchone()[0] > 0


# ─────────────────────────────────────────────────────────
#  App users table (auth)
# ─────────────────────────────────────────────────────────
def ensure_app_users(conn: oracledb.Connection) -> None:
    """Bootstrap the app users table — called once at startup."""
    from auth import ensure_users_table
    ensure_users_table(conn)


# ─────────────────────────────────────────────────────────
#  ensure_tables()
#
#  Full idempotent DDL bootstrap — safe to call on every startup.
#  Handles all cases:
#    1. Fresh install      — tables don't exist yet → CREATE
#    2. First upgrade      — tables exist without NAME column → ALTER
#    3. Table was dropped  — recreates cleanly, including sequence
#    4. Partial drop       — chunk table dropped but doc table intact → recreates chunk only
#    5. Constraint collision — uses derived names checked before creation
# ─────────────────────────────────────────────────────────
def ensure_tables() -> None:
    _seq_name = f"SEQ_{cfg.doc_table[:25]}_ID"

    with get_conn() as conn:
        cur = conn.cursor()

        # ── DOC TABLE ─────────────────────────────────────────────────────────
        if not _table_exists(cur, cfg.doc_table):
            # Create sequence for doc IDs (works on tables without IDENTITY col)
            if not _sequence_exists(cur, _seq_name):
                cur.execute(
                    f"CREATE SEQUENCE {cfg.schema}.{_seq_name} "
                    f"START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE"
                )
                logger.info("Created sequence %s.%s", cfg.schema, _seq_name)

            cur.execute(f"""
                CREATE TABLE {cfg.fq_doc_table} (
                    id    NUMBER        DEFAULT {cfg.schema}.{_seq_name}.NEXTVAL
                                        NOT NULL
                                        CONSTRAINT PK_{cfg.doc_table[:25]}_ID PRIMARY KEY,
                    name  VARCHAR2(500),
                    data  BLOB
                )
            """)
            logger.info("Created table %s", cfg.fq_doc_table)
        else:
            # Table exists — patch missing NAME column (pre-existing table case)
            if not _column_exists(cur, cfg.doc_table, "NAME"):
                cur.execute(
                    f"ALTER TABLE {cfg.fq_doc_table} ADD (name VARCHAR2(500))"
                )
                logger.info("Added NAME column to %s", cfg.fq_doc_table)

            # Ensure sequence exists even if table predates this app
            if not _sequence_exists(cur, _seq_name):
                # Seed sequence above current max id to avoid PK collisions
                cur.execute(f"SELECT NVL(MAX(id), 0) + 1 FROM {cfg.fq_doc_table}")
                start_val = cur.fetchone()[0]
                cur.execute(
                    f"CREATE SEQUENCE {cfg.schema}.{_seq_name} "
                    f"START WITH {start_val} INCREMENT BY 1 NOCACHE NOCYCLE"
                )
                logger.info(
                    "Created sequence %s.%s starting at %d",
                    cfg.schema, _seq_name, start_val,
                )

        # ── CHUNK TABLE ───────────────────────────────────────────────────────
        if not _table_exists(cur, cfg.chunk_table):
            # Build constraint DDL conditionally to avoid name collisions on recreate
            pk_ddl = (
                f"CONSTRAINT {cfg.pk_chunk} PRIMARY KEY (doc_id, chunk_id)"
                if not _constraint_exists(cur, cfg.pk_chunk)
                else ""
            )
            fk_ddl = (
                f"CONSTRAINT {cfg.fk_chunk_doc} FOREIGN KEY (doc_id) "
                f"REFERENCES {cfg.fq_doc_table}(id) ON DELETE CASCADE"
                if not _constraint_exists(cur, cfg.fk_chunk_doc)
                else ""
            )
            constraints = ",\n                    ".join(
                c for c in [pk_ddl, fk_ddl] if c
            )
            comma = f",\n                    {constraints}" if constraints else ""

            cur.execute(f"""
                CREATE TABLE {cfg.fq_chunk_table} (
                    doc_id          NUMBER        NOT NULL,
                    chunk_id        NUMBER        NOT NULL,
                    chunk_data      VARCHAR2(4000),
                    chunk_embedding VECTOR{comma}
                )
            """)
            logger.info("Created table %s", cfg.fq_chunk_table)

            # Add constraints separately if they were skipped above
            if pk_ddl == "" and not _constraint_exists(cur, cfg.pk_chunk):
                cur.execute(
                    f"ALTER TABLE {cfg.fq_chunk_table} "
                    f"ADD CONSTRAINT {cfg.pk_chunk} PRIMARY KEY (doc_id, chunk_id)"
                )
            if fk_ddl == "" and not _constraint_exists(cur, cfg.fk_chunk_doc):
                cur.execute(
                    f"ALTER TABLE {cfg.fq_chunk_table} "
                    f"ADD CONSTRAINT {cfg.fk_chunk_doc} FOREIGN KEY (doc_id) "
                    f"REFERENCES {cfg.fq_doc_table}(id) ON DELETE CASCADE"
                )


def ensure_vector_index() -> None:
    """
    Create HNSW vector index on chunk_embedding if not present.
    Safe to call every startup — checks existence before attempting CREATE.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        if not _index_exists(cur, cfg.chunk_table, "VECTOR"):
            idx_name = f"IDX_{cfg.chunk_table[:20]}_EMBED"
            cur.execute(f"""
                CREATE VECTOR INDEX {idx_name}
                ON {cfg.fq_chunk_table}(chunk_embedding)
                ORGANIZATION INMEMORY NEIGHBOR GRAPH
                DISTANCE {cfg.distance}
                WITH TARGET ACCURACY 95
            """)
            logger.info("Created HNSW vector index %s on %s", idx_name, cfg.fq_chunk_table)


# ─────────────────────────────────────────────────────────
#  Document ingestion
# ─────────────────────────────────────────────────────────

def insert_document(name: str, raw_bytes: bytes) -> int:
    """
    Insert raw file bytes into doc table; return new doc_id.
    Auto-detects whether id is GENERATED ALWAYS AS IDENTITY (existing table)
    or a plain NUMBER with sequence (new table created by ensure_tables).
    """
    _seq_name = f"SEQ_{cfg.doc_table[:25]}_ID"
    with get_conn() as conn:
        cur = conn.cursor()

        # Detect GENERATED ALWAYS AS IDENTITY at runtime — no hardcoding
        cur.execute(
            "SELECT NVL(identity_column,'NO') "
            "FROM all_tab_columns "
            "WHERE owner=:s AND table_name=:t AND column_name='ID'",
            {"s": cfg.schema, "t": cfg.doc_table},
        )
        row = cur.fetchone()
        is_identity = row and row[0].upper() == "YES"

        if is_identity:
            # Oracle owns the id — omit it from INSERT, retrieve with RETURNING
            doc_id_var = cur.var(oracledb.NUMBER)
            cur.execute(
                f"INSERT INTO {cfg.fq_doc_table} (name, data) "
                f"VALUES (:n, :d) RETURNING id INTO :id",
                {"n": name, "d": raw_bytes, "id": doc_id_var},
            )
            doc_id = int(doc_id_var.getvalue()[0])
        else:
            # Use sequence if available, otherwise MAX(id)+1
            if _sequence_exists(cur, _seq_name):
                cur.execute(f"SELECT {cfg.schema}.{_seq_name}.NEXTVAL FROM dual")
            else:
                cur.execute(f"SELECT NVL(MAX(id), 0) + 1 FROM {cfg.fq_doc_table}")
            doc_id = int(cur.fetchone()[0])
            cur.execute(
                f"INSERT INTO {cfg.fq_doc_table} (id, name, data) VALUES (:id, :n, :d)",
                {"id": doc_id, "n": name, "d": raw_bytes},
            )

        logger.info("Inserted document id=%d  name=%s", doc_id, name)
        return doc_id

def insert_chunks(doc_id: int, chunks: list[str]) -> None:
    """
    Embed + insert text chunks using the DB-resident ONNX model.
    Uses executemany for efficiency.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        rows = [
            {"doc_id": doc_id, "chunk_id": idx, "chunk_data": chunk[:4000]}
            for idx, chunk in enumerate(chunks)
        ]
        cur.executemany(
            f"""
            INSERT INTO {cfg.fq_chunk_table}
                (doc_id, chunk_id, chunk_data, chunk_embedding)
            VALUES (
                :doc_id, :chunk_id, :chunk_data,
                VECTOR_EMBEDDING({cfg.fq_onnx_model} USING :chunk_data AS data)
            )
            """,
            rows,
        )
        logger.info("Inserted %d chunks for doc_id=%d", len(chunks), doc_id)


# ─────────────────────────────────────────────────────────
#  Vector search
# ─────────────────────────────────────────────────────────
def vector_search(
    query: str,
    top_k: int | None = None,
    distance: str | None = None,
) -> list[dict]:
    """
    Embed query with the same ONNX model then run ANN search.
    Returns list of {chunk_data, doc_id, chunk_id, distance}.
    """
    k    = top_k or cfg.top_k
    dist = (distance or cfg.distance).upper()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT c.chunk_data,
                   c.doc_id,
                   c.chunk_id,
                   VECTOR_DISTANCE(
                       c.chunk_embedding,
                       VECTOR_EMBEDDING({cfg.fq_onnx_model} USING :query AS data),
                       {dist}
                   ) AS distance
            FROM   {cfg.fq_chunk_table} c
            ORDER  BY distance
            FETCH  FIRST :k ROWS ONLY
            """,
            {"query": query, "k": k},
        )
        cols = [d[0].lower() for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


# ─────────────────────────────────────────────────────────
#  Utility
# ─────────────────────────────────────────────────────────
def list_documents() -> list[dict]:
    """
    List all documents with chunk counts.
    NVL on name handles rows inserted before the NAME column existed.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT d.id,
                   NVL(d.name, 'doc-' || d.id) AS name,
                   COUNT(c.chunk_id)            AS chunk_count
            FROM   {cfg.fq_doc_table}   d
            LEFT JOIN {cfg.fq_chunk_table} c ON c.doc_id = d.id
            GROUP BY d.id, d.name
            ORDER BY d.id DESC
            """
        )
        cols = [d[0].lower() for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def delete_document(doc_id: int) -> None:
    """
    Delete a document and all its chunks.
    Chunks are deleted explicitly first; the FK ON DELETE CASCADE is a safety net
    but explicit delete gives us an accurate rowcount for logging.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM {cfg.fq_chunk_table} WHERE doc_id = :id",
            {"id": doc_id},
        )
        chunks_deleted = cur.rowcount
        cur.execute(
            f"DELETE FROM {cfg.fq_doc_table} WHERE id = :id",
            {"id": doc_id},
        )
        docs_deleted = cur.rowcount
        # get_conn() commits on exit — no explicit commit needed here
        logger.info(
            "Deleted doc_id=%d  chunks_removed=%d  doc_removed=%d",
            doc_id, chunks_deleted, docs_deleted,
        )
        if docs_deleted == 0:
            logger.warning("delete_document: doc_id=%d not found", doc_id)
