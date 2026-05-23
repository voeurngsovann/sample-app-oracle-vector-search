# 📤 Upload to GitHub - Step-by-Step Guide

This guide will walk you through uploading your Oracle Vector Search project to GitHub.

---

## Step 1: Create a GitHub Account (if you don't have one)

1. Go to [github.com](https://github.com)
2. Click **Sign up**
3. Follow the registration steps
4. Verify your email

---

## Step 2: Install Git

### Windows
1. Download from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer
3. Use default settings (or customize as needed)
4. Verify installation:
   ```cmd
   git --version
   ```

### macOS
```bash
brew install git
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install git
```

---

## Step 3: Configure Git

Open Command Prompt or Terminal and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Example:
```bash
git config --global user.name "John Doe"
git config --global user.email "john@example.com"
```

Verify:
```bash
git config --global --list
```

---

## Step 4: Create a Repository on GitHub

1. Log in to [github.com](https://github.com)
2. Click the **+** icon (top-right) → **New repository**
3. Fill in details:
   - **Repository name:** `oracle-vector-search`
   - **Description:** `Semantic vector search chat with Oracle 26ai & Streamlit`
   - **Visibility:** Public (so others can find it)
   - **Initialize with:** ❌ Do NOT check "Add a README file"
4. Click **Create repository**

You'll see a setup page with commands. **Copy the HTTPS URL** (looks like: `https://github.com/YOUR_USERNAME/oracle-vector-search.git`)

---

## Step 5: Initialize Git in Your Project

Open Command Prompt/Terminal and navigate to your project:

```bash
cd D:\App\AI\app\vector_search
```

Initialize git:

```bash
git init
```

Add all files:

```bash
git add .
```

Check what will be committed:

```bash
git status
```

You should see all your files (excluding what's in `.gitignore`).

---

## Step 6: Create Your First Commit

```bash
git commit -m "Initial commit: Oracle Vector Search Chat App"
```

Example output:
```
[main (root-commit) a1b2c3d] Initial commit: Oracle Vector Search Chat App
 42 files changed, 15234 insertions(+)
 ...
```

---

## Step 7: Add Remote Repository

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/oracle-vector-search.git
```

Verify:

```bash
git remote -v
```

Should show:
```
origin  https://github.com/YOUR_USERNAME/oracle-vector-search.git (fetch)
origin  https://github.com/YOUR_USERNAME/oracle-vector-search.git (push)
```

---

## Step 8: Rename Branch to "main" (if needed)

```bash
git branch -M main
```

---

## Step 9: Push to GitHub

```bash
git push -u origin main
```

You'll be prompted for credentials:
- **Username:** Your GitHub username
- **Password:** Your GitHub personal access token (see below)

### Create a Personal Access Token

If you get a password error, you need a **Personal Access Token**:

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token** → **Generate new token (classic)**
3. Set:
   - **Token name:** `oracle-vector-search`
   - **Expiration:** 90 days (or longer)
   - **Scopes:** Check ✅ `repo` (full control of private repositories)
4. Click **Generate token**
5. **Copy the token** (you'll only see it once!)
6. Use this token as your "password" when pushing

---

## Step 10: Verify Your Code is on GitHub

1. Go to `https://github.com/YOUR_USERNAME/oracle-vector-search`
2. You should see:
   - All your files listed
   - README.md displayed
   - Commit history
   - Branches

🎉 **You're done!**

---

## Common Commands

### Update Code on GitHub

After making changes locally:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

### Check Status

```bash
git status
```

### View Commit History

```bash
git log --oneline
```

### Clone Your Repository

To clone your project on another machine:

```bash
git clone https://github.com/YOUR_USERNAME/oracle-vector-search.git
```

---

## Troubleshooting

### "fatal: not a git repository"
- Make sure you're in the correct directory
- Run `git init` again if needed

### "authentication failed"
- Use a Personal Access Token, not your GitHub password
- Verify the token hasn't expired

### ".gitignore not working"
- Files already tracked won't be ignored
- Remove them: `git rm --cached filename`
- Then commit: `git commit -m "Remove tracked files"`

### "fatal: a file would be overwritten by merge"
- Run: `git clean -fd` (removes untracked files)
- Then try again

---

## Next Steps

1. **Add a GitHub Actions workflow** (optional CI/CD)
2. **Add contributors** (invite team members)
3. **Create releases** (tag versions)
4. **Enable GitHub Pages** (for documentation)
5. **Set up project board** (for task tracking)

---

## Share Your Repository

Once uploaded, you can share the link:

```
https://github.com/YOUR_USERNAME/oracle-vector-search
```

Others can:
- ⭐ Star your project
- 🔀 Fork it
- 📝 Create issues
- 🤝 Submit pull requests

---

## Additional Resources

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://github.github.com/training-kit/downloads/github-git-cheat-sheet.pdf)
- [Pro Git Book](https://git-scm.com/book/en/v2)
