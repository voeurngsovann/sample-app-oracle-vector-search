# ⚡ Quick Start Checklist

Complete this checklist to get the Oracle Vector Search app running in 15 minutes.

---

## 1️⃣ Oracle Database Setup (5 min)

**Prerequisites:** Oracle 26ai installed, SYSTEM user access

- [ ] **Connect as SYSTEM user:**
  ```sql
  sqlplus system@DEVPDB
  ```

- [ ] **Copy-paste this SQL block:**
  ```sql
  CREATE USER dev IDENTIFIED BY YourSecurePassword123!;
  GRANT CONNECT, RESOURCE TO dev;
  GRANT CREATE TABLE TO dev;
  GRANT CREATE PROCEDURE TO dev;
  GRANT EXECUTE ON SYS.VECTOR_EMBEDDING TO dev;
  ALTER USER dev QUOTA UNLIMITED ON USERS;
  COMMIT;
  EXIT;
  ```

- [ ] **Verify DEV user created:**
  ```sql
  sqlplus dev@DEVPDB
  SELECT user FROM dual;  -- Should show: DEV
  EXIT;
  ```

---

## 2️⃣ Python Environment Setup (3 min)

**Prerequisites:** Python 3.10+, Git installed

- [ ] **Clone or download project:**
  ```bash
  # Clone from GitHub (recommended)
  git clone https://github.com/YOUR_USERNAME/oracle-vector-search.git
  cd oracle-vector-search
  
  # OR extract ZIP and navigate:
  cd D:\App\AI\app\vector_search
  ```

- [ ] **Create virtual environment:**
  ```bash
  # Windows
  python -m venv .venv
  .venv\Scripts\activate
  
  # macOS/Linux
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- [ ] **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

---

## 3️⃣ Configure Environment (2 min)

- [ ] **Copy example file:**
  ```bash
  # Windows
  copy .env.example .env
  
  # macOS/Linux
  cp .env.example .env
  ```

- [ ] **Edit `.env` file with your database credentials:**
  ```ini
  ORA_USER=dev
  ORA_PASSWORD=YourSecurePassword123!
  ORA_HOST=localhost
  ORA_PORT=1521
  ORA_SERVICE=DEVPDB
  LLM_PROVIDER=ollama
  ```

- [ ] **Verify `.env` is created:**
  ```bash
  # Windows
  dir .env
  
  # macOS/Linux
  ls -la .env
  ```

---

## 4️⃣ Run the Application (2 min)

- [ ] **Ensure virtual environment is activated:**
  ```bash
  # Windows
  .venv\Scripts\activate
  
  # macOS/Linux
  source .venv/bin/activate
  ```

- [ ] **Start Streamlit:**
  ```bash
  streamlit run app.py
  ```

- [ ] **Browser should open to:**
  ```
  http://localhost:8501
  ```

- [ ] **Check console for success message:**
  ```
  Database initialized successfully
  ✓ App is running on http://localhost:8501
  ```

---

## 5️⃣ First Login (1 min)

- [ ] **Use default credentials:**
  - Username: `admin`
  - Password: `admin`

- [ ] **After login you should see:**
  - Left sidebar with controls
  - Chat area with empty state
  - "Upload Documents" section

- [ ] **⚠️ Change default password:**
  - Click "🚪 Sign Out" in sidebar
  - Log back in as admin
  - OR change in database:
    ```sql
    sqlplus dev@DEVPDB
    UPDATE app_users SET password_hash='...' WHERE username='admin';
    ```

---

## 6️⃣ Test the App (2 min)

- [ ] **Upload a test document:**
  - Go to sidebar → "Upload Documents"
  - Drag & drop a PDF, DOCX, TXT, or Markdown file
  - Click "⬆ Ingest Selected Files"
  - Wait for success message

- [ ] **Perform a vector search:**
  - Type a question in the chat box at the bottom
  - Press Enter or click Send
  - App should return relevant chunks from your document

- [ ] **Try RAG mode (optional):**
  - Sidebar → "Answer Mode" → "🤖 RAG — Ollama"
  - (Requires Ollama running: `ollama serve`)
  - Ask a question → Ollama generates a grounded answer

---

## 7️⃣ Upload to GitHub (3 min)

- [ ] **Create GitHub account:**
  - Go to [github.com](https://github.com)
  - Sign up (free)

- [ ] **Create new repository:**
  - Click **+** → **New repository**
  - Name: `oracle-vector-search`
  - Visibility: **Public**
  - **Don't** initialize with README
  - Click **Create**

- [ ] **Initialize Git locally:**
  ```bash
  cd D:\App\AI\app\vector_search
  git init
  git add .
  git commit -m "Initial commit: Oracle Vector Search App"
  ```

- [ ] **Push to GitHub:**
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/oracle-vector-search.git
  git branch -M main
  git push -u origin main
  ```

- [ ] **Verify on GitHub:**
  - Visit: `https://github.com/YOUR_USERNAME/oracle-vector-search`
  - Should see all files including README.md

---

## 🎉 Success Indicators

After completing this checklist, you should have:

✅ **Database:**
- DEV user created and accessible
- Tables auto-created by app (visible in `sqlplus`)

✅ **App Running:**
- Streamlit UI on `http://localhost:8501`
- Sidebar visible and responsive
- Chat interface operational

✅ **Core Features Working:**
- ✅ Login (admin/admin)
- ✅ File upload
- ✅ Vector search
- ✅ Chat messages saved

✅ **Code on GitHub:**
- ✅ Repository created
- ✅ All files pushed
- ✅ Public and shareable

---

## 🆘 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| `ORA-01017: invalid username/password` | Check `.env` credentials match DEV user |
| `Streamlit not starting` | Activate venv: `.venv\Scripts\activate` |
| `Connection refused` | Check Oracle is running: `sqlplus system@DEVPDB` |
| Sidebar not appearing after login | Refresh browser or restart `streamlit run app.py` |
| Can't push to GitHub | Use Personal Access Token instead of password |

---

## 📖 Next Steps

1. **Read full documentation:**
   - [README.md](README.md) – Complete overview
   - [ORACLE_SETUP.md](ORACLE_SETUP.md) – Detailed DB setup
   - [GITHUB_SETUP.md](GITHUB_SETUP.md) – GitHub instructions

2. **Enable RAG Mode (optional):**
   - Install Ollama: `ollama.ai`
   - Pull a model: `ollama pull gemma4:e4b`
   - Update `.env`: `LLM_PROVIDER=ollama`

3. **Invite Team Members:**
   - Create new app_users in database
   - Share GitHub repo link
   - Share Streamlit app URL

4. **Production Deployment (optional):**
   - Use Streamlit Cloud or Docker
   - Configure remote Oracle connection
   - Set up SSL/TLS

---

## 📋 Quick Reference

### Important Directories
```
D:\App\AI\app\vector_search\
├── .env                 ← Your config (don't commit to Git!)
├── .env.example         ← Template
├── app.py              ← Main app
├── db.py               ← Database code
└── requirements.txt    ← Dependencies
```

### Key Commands
```bash
# Activate Python env
.venv\Scripts\activate

# Start app
streamlit run app.py

# View database
sqlplus dev@DEVPDB

# Commit code
git add . && git commit -m "message" && git push
```

### Database Connections
```sql
-- Connect as DBA
sqlplus system@DEVPDB

-- Connect as app user
sqlplus dev@DEVPDB

-- Check tables (as dev user)
SELECT * FROM app_users;
SELECT COUNT(*) FROM aitest_documentation_chunks;
```

---

## 🆘 Get Help

1. **Check app.log for errors:**
   ```bash
   tail -f app.log
   ```

2. **Review documentation:**
   - README.md
   - ORACLE_SETUP.md
   - GITHUB_SETUP.md

3. **Open GitHub issue:**
   - Include error message
   - Include app.log snippet
   - Include Python version

---

**🚀 You're all set! Start by uploading a document and asking a question. Happy searching!**
