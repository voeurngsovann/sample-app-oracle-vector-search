# 🔮 Oracle 26ai · Vector Search Chat App

A **Streamlit chat application** that lets you upload documents, vectorize them in-database using Oracle's built-in ONNX model, and chat over them via semantic vector search—with optional RAG answers powered by Ollama, Google Gemini, or Claude.

**Key Features:**
- 📄 Upload PDFs, DOCX, TXT, Markdown files
- 🧠 Automatic text chunking with overlap
- 🔍 Semantic search using Oracle 26ai vector embeddings (ONNX `ALL_MINILM_L12_V2`)
- 🤖 Optional RAG mode with local LLMs (Ollama) or cloud providers (Gemini, Claude)
- 🎨 Beautiful dark-theme UI with split login layout
- 🔐 Secure authentication with PBKDF2-SHA256 hashing

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ User  ──  Streamlit UI (app.py)                             │
├─────────────────────────────────────────────────────────────┤
│ • Split login (sonar animation)                              │
│ • Sidebar with controls & document management                │
│ • Chat interface with vector search results                  │
└───────────────┬─────────────────────────────────────────────┘
                │
        ┌───────v────────┐
        │ db.py          │  ──────────────┐
        │ Connection     │                │
        │ Pool & DDL     │                │
        └────────────────┘                │
                                          │
                        ┌─────────────────v────────────────────┐
                        │ Oracle 26ai Database (DEV schema)     │
                        ├────────────────────────────────────────┤
                        │ Tables:                                │
                        │  • AITEST_DOCUMENTATION_TAB (blobs)    │
                        │  • AITEST_DOCUMENTATION_CHUNKS (emb.)  │
                        │  • VS_APP_USERS (auth)                    │
                        │ ONNX Model:                            │
                        │  • ALL_MINILM_L12_V2 (embeddings)      │
                        │ Index:                                 │
                        │  • IDX_ADC_CHUNK_EMBED (HNSW)          │
                        └────────────────────────────────────────┘
                        
        Optional RAG:
        ┌──────────────────────────────────────┐
        │ rag.py (LLM integration)             │
        ├──────────────────────────────────────┤
        │ • Ollama (local, http://localhost...)│
        │ • Google Gemini (cloud)              │
        │ • Anthropic Claude (cloud)           │
        └──────────────────────────────────────┘
```

---

## Prerequisites

| Requirement                | Version                     |
|----------------------------|------------------------------|
| **Python**                 | 3.10+                        |
| **Oracle Database**        | 26ai (23ai+)                 |
| **Oracle Instant Client**  | ❌ Not needed (thin mode)    |
| **ONNX Model in DB**       | `DEV.ALL_MINILM_L12_V2`      |
| **LLM (optional)**         | Ollama, Gemini, or Claude    |

---

## Complete Setup Guide

### Step 1: Create Oracle Database User (DEV)

Connect to your Oracle 26ai database as a DBA or SYSTEM user:

```sql
-- Connect as SYSDBA or SYSTEM
sqlplus system@DEVPDB

-- Create the DEV user
CREATE USER dev IDENTIFIED BY your_secure_password;

-- Grant required privileges for vector search
GRANT CONNECT, RESOURCE TO dev;
GRANT CREATE TABLE TO dev;
GRANT CREATE PROCEDURE TO dev;
GRANT CREATE FUNCTION TO dev;
GRANT db_developer_role, create mining model,dba to dev;

-- Grant vector embedding privileges (Oracle 26ai)
GRANT EXECUTE ON SYS.VECTOR_EMBEDDING TO dev;

create or replace directory model_dir as '/u01/models';
grant read, write on directory model_dir to dev;

connect dev/Welcome1@AIDBPDB1

-- download model 
cd /u01/models
#https://adwc4pm.objectstorage.us-ashburn-1.oci.customer-oci.com/p/fU1V-voY2VBhhqMPjhCC57Up77ROK9u6GN_j3-uGi_EzIdHm9XDn-RfnZS5bV0cN/n/adwc4pm/b/OML-ai-models/o/Oracle%20Machine%20Learning%20AI%20models.htm

begin
  dbms_vector.drop_onnx_model (
    model_name => 'ALL_MINILM_L12_V2',
    force => true);

  dbms_vector.load_onnx_model (
    directory  => 'model_dir',
    file_name  => 'all_MiniLM_L12_v2.onnx',
    model_name => 'ALL_MINILM_L12_V2');
end;
/
CREATE SEQUENCE dev.SEQ_QUESTION_CACHE_ID 
START WITH 1 
INCREMENT BY 1 
NOCACHE 
NOCYCLE;

CREATE TABLE dev.QUESTION_CACHE (
    id              NUMBER          DEFAULT dev.SEQ_QUESTION_CACHE_ID.NEXTVAL
                                    NOT NULL
                                    CONSTRAINT PK_QUESTION_CACHE_ID PRIMARY KEY,
    user_id         NUMBER          NOT NULL,
    question        VARCHAR2(4000)  NOT NULL,
    answer          CLOB            NOT NULL,
    response_time   NUMBER,
    created_at      TIMESTAMP       DEFAULT SYSTIMESTAMP,
    CONSTRAINT FK_QUESTION_CACHE_USER FOREIGN KEY (user_id)
        REFERENCES dev.VS_APP_USERS(id) ON DELETE CASCADE
);



CREATE INDEX dev.IDX_QUESTION_CACHE_USER_Q ON dev.QUESTION_CACHE(user_id, question);

-- Create application user (for login)
-- This is done automatically by the app on first run
-- But you can pre-create if needed:
-- CREATE USER appuser IDENTIFIED BY apppassword;
-- GRANT CONNECT TO appuser;

COMMIT;
EXIT;
```

#### Verify ONNX Model is Available
```sql
sqlplus dev/your_secure_password@DEVPDB

-- Check if ALL_MINILM_L12_V2 model exists
SELECT * FROM all_mining_models WHERE model_name LIKE '%MINILM%';

-- If not found, the app will attempt to create it on first run
-- (requires model binary in Oracle)
```

---

### Step 2: Clone or Download the Project

```bash
# Clone from GitHub (once uploaded)
git clone https://github.com/YOUR_USERNAME/oracle-vector-search.git
cd oracle-vector-search

# Or download as ZIP and extract
```

---

### Step 3: Set Up Python Environment

**Windows:**
```batch
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your database credentials
```

**Minimum required (.env):**
```ini
# Oracle Database Connection
ORA_USER=dev
ORA_PASSWORD=your_secure_password
ORA_HOST=localhost        # or your database server IP
ORA_PORT=1521
ORA_SERVICE=DEVPDB

# Schema & Objects (auto-created)
ORA_SCHEMA=DEV
ORA_DOC_TABLE=AITEST_DOCUMENTATION_TAB
ORA_CHUNK_TABLE=AITEST_DOCUMENTATION_CHUNKS
ORA_ONNX_MODEL=ALL_MINILM_L12_V2

# Vector Search
VECTOR_TOP_K=5
VECTOR_DISTANCE=COSINE

# LLM Provider (choose one)
LLM_PROVIDER=ollama       # or: gemini
```

**Optional: Enable RAG with LLMs**

For **Ollama** (local, free):
```ini
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/api
OLLAMA_MODEL=gemma4:e4b
# Or use another model: llama2, mistral, neural-chat, etc.
# Install Ollama from: https://ollama.ai
# Pull a model: ollama pull gemma4:e4b
```

For **Google Gemini** (cloud):
```ini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
# Get API key: https://aistudio.google.com/app/apikey
```

For **Anthropic Claude** (cloud):
```ini
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
# Get API key: https://console.anthropic.com/
```

---

### Step 5: Run the Application

```bash
# Make sure .venv is activated
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

streamlit run app.py
```

The app will:
1. ✅ Create application users table (`VS_APP_USERS`) if missing
2. ✅ Create document tables (`AITEST_DOCUMENTATION_TAB`, `AITEST_DOCUMENTATION_CHUNKS`)
3. ✅ Create HNSW vector index
4. ✅ Insert a default admin user (`admin` / `Admin@1234`) for first login

**Browser opens to:** `http://localhost:8501`

---

## First Login

Default credentials (created automatically):
- **Username:** `admin`
- **Password:** `Admin@1234`

⚠️ **Change these immediately!** Modify in the database:

```sql
sqlplus appuser/apppassword@DEVPDB

-- Update admin password (app uses PBKDF2-SHA256)
-- You can do this via the app's UI or database directly
-- For now, use the app's sign-out and re-login with default creds
```

---

## File Structure

```
oracle-vector-search/
├── app.py                    ← Streamlit UI (entry point) ⭐
├── db.py                     ← Oracle connection, DDL, CRUD, search
├── auth.py                   ← User authentication
├── chunker.py                ← File parsing (PDF/DOCX/TXT/MD)
├── rag.py                    ← RAG synthesis (Ollama/Gemini/Claude)
├── requirements.txt          ← Python dependencies
├── .env.example              ← Environment variables template
├── .gitignore                ← Git ignore rules
├── README.md                 ← This file
└── run.bat                   ← Windows batch runner
```

---

## How It Works

### 1. **Document Upload**
- Drop PDF, DOCX, TXT, or Markdown files in the sidebar
- App extracts text content automatically
- Text is split into overlapping chunks (configurable: 100–1000 words)

### 2. **Vector Embedding**
- Each chunk is embedded using Oracle's **ONNX model** (`ALL_MINILM_L12_V2`)
- Embeddings computed **inside the database** for efficiency
- Chunks stored in `AITEST_DOCUMENTATION_CHUNKS` with metadata (doc_id, chunk_id)

### 3. **Vector Search**
- User query is embedded with the same ONNX model (1 DB round-trip)
- Oracle's **HNSW index** returns top-K nearest neighbors
- Distance metrics: **COSINE** (default), DOT, or EUCLIDEAN

### 4. **Optional RAG Answer**
- Retrieved chunks passed as context to LLM
- LLM synthesizes grounded natural-language answer
- Sources cited with chunk references

---

## Configuration Details

### Environment Variables

| Variable               | Default         | Description |
|------------------------|-----------------|-------------|
| `ORA_USER`             | `dev`           | Oracle database user |
| `ORA_PASSWORD`         | *(required)*    | Oracle password |
| `ORA_HOST`             | `localhost`     | Database host/IP |
| `ORA_PORT`             | `1521`          | Database port |
| `ORA_SERVICE`          | `DEVPDB`        | Service name |
| `ORA_SCHEMA`           | `DEV`           | Schema name |
| `ORA_DOC_TABLE`        | `AITEST_DOCUMENTATION_TAB` | Documents table |
| `ORA_CHUNK_TABLE`      | `AITEST_DOCUMENTATION_CHUNKS` | Chunks/embeddings table |
| `ORA_ONNX_MODEL`       | `ALL_MINILM_L12_V2` | Embedding model |
| `VECTOR_TOP_K`         | `5`             | Number of search results |
| `VECTOR_DISTANCE`      | `COSINE`        | Distance metric |
| `LLM_PROVIDER`         | `ollama`        | LLM service: `ollama` \| `gemini` \| `anthropic` |
| `OLLAMA_BASE_URL`      | `http://localhost:11434/api` | Ollama server |
| `OLLAMA_MODEL`         | `gemma4:e4b`    | Ollama model name |
| `GEMINI_API_KEY`       | *(optional)*    | Google Gemini API key |
| `GEMINI_MODEL`         | `gemini-2.0-flash` | Gemini model |
| `ANTHROPIC_API_KEY`    | *(optional)*    | Anthropic API key |

---

## Troubleshooting

### `ORA-01017: invalid username/password`
- Check credentials in `.env`
- Verify Oracle user exists and is unlocked

### `ORA-00942: table or view does not exist`
- App auto-creates tables on first run
- Check database logs for creation errors
- Verify DEV user has CREATE TABLE privilege

### `Vector search returns no results`
- Check documents were uploaded and indexed
- Verify `AITEST_DOCUMENTATION_CHUNKS` is not empty
- Check vector index exists: `SELECT * FROM user_indexes WHERE index_name LIKE '%CHUNK%'`

### Streamlit not starting
- Ensure `.venv` is activated
- Reinstall: `pip install -r requirements.txt`
- Check `app.log` for detailed errors

### LLM (Ollama/Gemini) not responding
- **Ollama:** Ensure server is running (`ollama serve`) and model pulled
- **Gemini:** Verify API key is valid and has quota
- Check `application.log` for detailed errors

---

## Performance Tips

1. **Use COSINE distance** for text embeddings (most relevant)
2. **Increase TOP_K** for more search results (slower but more context)
3. **Optimize chunk size:** 200–400 words is a good balance
4. **Use Ollama locally** for faster, cost-free RAG
5. **Index DDL:** HNSW index is created automatically on first run

---

## License

MIT License – feel free to use, modify, and distribute.

---

## Support

For issues or questions:
1. Check app.log for error messages
2. Review this README and .env.example
3. Open an issue on GitHub with:
   - Error message
   - Database version
   - Python version
   - Steps to reproduce

---

## Changelog

### v1.0.0 (2026-05-19)
- ✨ Initial release
- 🔐 Split login with animated UI
- 📄 Multi-format document upload
- 🔍 Semantic vector search with HNSW index
- 🤖 RAG mode with Ollama/Gemini/Claude
- 🎨 Dark theme with responsive sidebar

## Environment Variables Reference

| Variable           | Default                        | Description              |
|--------------------|--------------------------------|--------------------------|
| `ORA_USER`         | —                              | DB username              |
| `ORA_PASSWORD`     | —                              | DB password              |
| `ORA_HOST`         | `localhost`                    | DB hostname              |
| `ORA_PORT`         | `1521`                         | Listener port            |
| `ORA_SERVICE`      | —                              | Service name             |
| `ORA_SCHEMA`       | `DEV`                          | Owner schema             |
| `ORA_DOC_TABLE`    | `AITEST_DOCUMENTATION_TAB`     | Source doc table         |
| `ORA_CHUNK_TABLE`  | `AITEST_DOCUMENTATION_CHUNKS`  | Chunk + vector table     |
| `ORA_ONNX_MODEL`   | `ALL_MINILM_L12_V2`            | ONNX model name in DB    |
| `VECTOR_TOP_K`     | `5`                            | Default search results   |
| `VECTOR_DISTANCE`  | `COSINE`                       | Distance metric          |
| `Gemini_API_KEY`| —                              | Enables RAG mode         |
| `RAG_MODEL`        | `gemini-3-flash-preview`     | Gemini model for answers |
