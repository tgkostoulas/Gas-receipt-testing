# Upload to GitHub - Quick Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon (top right) → **"New repository"**
3. Repository name: `gas-station-tracker` (or any name you prefer)
4. Description: "Gas station receipt tracker for Greece"
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

## Step 2: Initialize Git and Push

Run these commands in your project directory:

### Windows (PowerShell)

```powershell
# Navigate to project
cd C:\Users\thano\Desktop\personal\receipt

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Gas station tracker"

# Add GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gas-station-tracker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### macOS/Linux

```bash
# Navigate to project
cd ~/Desktop/personal/receipt

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Gas station tracker"

# Add GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/gas-station-tracker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Authentication

When you run `git push`, GitHub will ask for authentication:

**Option 1: Personal Access Token (Recommended)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Select scopes: `repo` (full control)
4. Copy the token
5. When prompted for password, paste the token (not your GitHub password)

**Option 2: GitHub CLI**
```bash
# Install GitHub CLI, then:
gh auth login
```

## What Gets Uploaded

✅ **Will be uploaded:**
- All source code (backend/, web/, tests/)
- README.md
- .gitignore
- Test images (test_*.JPEG in uploads/)
- Configuration files

❌ **Will NOT be uploaded (ignored by .gitignore):**
- Virtual environments (venv/, venv312/)
- node_modules/
- User-uploaded receipts (non-test images)
- .env files (your API keys)
- Cache files

## Future Updates

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

## Troubleshooting

**"Repository not found"**
- Check repository name and username are correct
- Ensure repository exists on GitHub

**"Authentication failed"**
- Use Personal Access Token instead of password
- Check token has `repo` scope

**"Large file" warning**
- Test images might be large - that's okay for now
- Consider using Git LFS for very large files later
