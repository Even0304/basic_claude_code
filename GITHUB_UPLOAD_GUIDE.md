# GitHub Upload Guide

## Pre-Upload Checklist ✓

**Sensitive Information:**
- ✓ `.env` - Git-ignored (contains real API keys)
- ✓ `.env.example` - Included as template
- ✓ No hardcoded API keys in source code
- ✓ All credentials loaded from environment variables

**Excluded Directories:**
- `claude-code-from-scratch/` - Reference/tutorial code
- `.kimi/sessions/` - User session files
- `__pycache__/` - Python cache

**Files to Upload:**
- ✓ All kimi_code source files
- ✓ All demos and examples
- ✓ All documentation (README.md, QUICK_START.md, etc.)
- ✓ PROJECT_SHOWCASE.html - Interactive feature showcase
- ✓ Tests (tests_*.py files)
- ✓ Configuration files (pyproject.toml, .env.example)

## Step-by-Step Upload

### 1. Create GitHub Repository

Go to https://github.com/new and create a new repository:
- **Repository name:** `kimi-code` (or your preferred name)
- **Description:** "Claude Code Python implementation with parallel multi-agent execution"
- **Public/Private:** Choose based on preference
- **Initialize with:** Don't initialize (we'll do it locally)

### 2. Initialize Local Git Repository

```bash
cd /Users/even/Desktop/kimi

# Initialize git
git init

# Add all files
git add .

# Verify what will be committed
git status
# Should exclude: .env, .bak files, claude-code-from-scratch/, etc.
```

### 3. Create Initial Commit

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"

git commit -m "Initial commit: Claude Code Python implementation

Features:
- Parallel multi-agent execution (3.15x-7.42x speedup)
- 9 tools (bash, read, write, edit, glob, grep, task, web_fetch, web_search)
- Kimi k2.5z and Claude Opus support
- Cost tracking system (14+ models)
- Session management with auto-save
- Permission system with danger detection
- Interactive REPL with 8 commands
- Comprehensive documentation

100% feature complete. Production ready."
```

### 4. Add Remote Repository

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME`:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Verify
git remote -v
```

### 5. Push to GitHub

```bash
# For main branch
git branch -M main
git push -u origin main

# You'll be prompted for:
# - GitHub username
# - GitHub token (or personal access token)
```

### 6. Verify Upload

Check on GitHub:
1. Repository is visible at `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. Files are uploaded correctly
3. `.env` is NOT in the repository
4. `PROJECT_SHOWCASE.html` is included

## Creating Personal Access Token (if needed)

If authentication fails, create a token:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token
5. Use token as password when pushing

## Files NOT Uploaded (for Security)

These files are excluded by `.gitignore`:
```
.env                          # Contains your API keys
.env.local                    # Local overrides
.DS_Store                     # macOS files
__pycache__/                  # Python cache
.pytest_cache/                # Test cache
.coverage                     # Coverage reports
.kimi/sessions/               # User sessions
*.egg-info/                   # Package info
venv/                         # Virtual environment
claude-code-from-scratch/     # Reference code
debug_demo.py                 # Debug scripts
test_integration.py           # Integration tests
```

## After Upload

1. Add repository description on GitHub
2. Add topics: `python`, `ai`, `multi-agent`, `claude`, `kimi`
3. Enable GitHub Pages (optional):
   - Settings → Pages
   - Source: Deploy from a branch → main
   - Then access PROJECT_SHOWCASE.html at:
     - `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/PROJECT_SHOWCASE.html`

4. Create releases (optional):
   - Go to Releases
   - Create new release with version tags (v1.0.0, etc.)

## Troubleshooting

**"fatal: not a git repository"**
- Run `git init` first

**"Please make sure you have the correct access rights"**
- Check GitHub token has `repo` scope
- Verify username and repo name in remote URL

**".env is being tracked"**
- Remove: `git rm --cached .env`
- Commit: `git commit -m "Remove .env from tracking"`

**Want to update .env afterwards?**
- Never push it to GitHub
- Document setup in README (already done)
- Users should copy .env.example and configure locally

## Security Reminders

✓ Never commit:
  - `.env` files with real credentials
  - API keys, tokens, or passwords
  - Private data or configuration

✓ Always use:
  - `.env.example` for configuration templates
  - Environment variables for secrets
  - `.gitignore` to exclude sensitive files

✓ Document:
  - How to set up `.env`
  - Required environment variables
  - Configuration options
