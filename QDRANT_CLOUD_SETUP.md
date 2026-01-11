# 🎯 Setup Qdrant Cloud (Free & Better!)

## Why Qdrant Cloud? ✨

✅ **Completely FREE** - No credit card needed  
✅ **Persistent database** - Data stays even if app restarts  
✅ **Much faster** - No rebuild delays  
✅ **Professional** - Managed by Qdrant team  
✅ **Perfect for Streamlit** - Built for this use case  

---

## Step 1: Create Qdrant Cloud Account

1. Go to: **https://cloud.qdrant.io**
2. Click **"Sign Up"**
3. Create account (free tier available)

---

## Step 2: Create a Cluster

1. Login to Qdrant Cloud dashboard
2. Click **"Create Cluster"**
3. Choose settings:
   - **Cluster name**: `chandamama` (or any name)
   - **Size**: Free tier is fine (~500MB)
   - **Region**: Pick one close to you
4. Click **"Create"**
5. Wait ~2 minutes for cluster to be ready

---

## Step 3: Get Your Credentials

After cluster is created:

1. Click on your cluster name
2. Copy these values:

**You'll see:**
```
Cluster URL: https://abc123-xyz.qdr.cloud
API Key: (long random string)
```

Save them! You'll need them for the next step.

---

## Step 4: Update Your `.env` File

Replace your `.env` with:

```
# API Keys
OPENAI_API_KEY=sk-proj-VHYWyLW7XwHXM17MgSa7...
GEMINI_API_KEY=your_gemini_api_key_here
HF_TOKEN=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
GROQ_API_KEY=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

# Qdrant Cloud (NEW!)
QDRANT_URL=https://your-cluster-url.qdr.cloud
QDRANT_API_KEY=your-api-key-here
```

---

## Step 5: Update Configuration Files

### Update `src/config.py`

Change this line:
```python
QDRANT_PATH = os.path.join(os.getcwd(), "qdrant_db")
```

To this:
```python
# Use Qdrant Cloud if URL is set, otherwise use local
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if QDRANT_URL:
    QDRANT_PATH = QDRANT_URL  # Use cloud URL
else:
    QDRANT_PATH = os.path.join(os.getcwd(), "qdrant_db")  # Fallback to local
```

---

## Step 6: Build Database in Cloud

### Option A: Build Locally First (Recommended)

```bash
# Make sure your .env has the Qdrant Cloud credentials
source venv/bin/activate
python rebuild_db.py
```

This will:
1. Read your Qdrant Cloud credentials from `.env`
2. Build the database in your Qdrant Cloud cluster
3. Upload all story embeddings
4. Take ~5-10 minutes

### Option B: Let Streamlit Cloud Build It

You can skip local build and let Streamlit Cloud do it on first run (takes a bit longer).

---

## Step 7: Update Your Code

I'll provide code updates to handle Qdrant Cloud automatically.

### For `app.py` - Remove old database check

Replace the database check code with:

```python
# Database is now in Qdrant Cloud - no local rebuild needed
# App will connect to cloud automatically via QDRANT_URL env var
```

### For `src/scripts/populate_qdrant.py` - Support Cloud

Update to use environment variables:

```python
import os
from qdrant_client import QdrantClient

# Use Qdrant Cloud if credentials provided
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if qdrant_url:
    # Connect to Qdrant Cloud
    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key
    )
    print(f"Connected to Qdrant Cloud: {qdrant_url}")
else:
    # Use local Qdrant
    QDRANT_PATH = os.path.join(PROJECT_ROOT, "qdrant_db")
    client = QdrantClient(path=QDRANT_PATH)
    print(f"Connected to local Qdrant: {QDRANT_PATH}")
```

---

## Step 8: Deploy to Streamlit Cloud

1. Update `.env` in `.gitignore` (already done)
2. Add Qdrant credentials to Streamlit Cloud:
   - App settings → Secrets
   - Add:
     ```
     QDRANT_URL = https://your-cluster-url.qdr.cloud
     QDRANT_API_KEY = your-api-key-here
     ```
   - Add your other API keys too

3. Push code:
   ```bash
   git add .
   git commit -m "Use Qdrant Cloud for vector database"
   git push origin main
   ```

4. Streamlit Cloud auto-redeploys ✅

---

## Result ✨

**Before (Local DB):**
- ⏳ First load: 1-2 min (database rebuilds)
- ⚡ Subsequent: instant

**After (Qdrant Cloud):**
- ⚡ All loads: instant
- 💾 Data always persists
- 🔒 Professional managed database

---

## Free Tier Limits

Qdrant Cloud free tier includes:
- **Storage**: 500MB
- **Search**: Unlimited
- **Collections**: Multiple
- **Perfect for**: Your use case ✅

---

## Commands

```bash
# Test locally
python rebuild_db.py

# Push to GitHub
git add . && git commit -m "msg" && git push

# View Qdrant Cloud
# Go to: https://cloud.qdrant.io
```

---

## Troubleshooting

### "Cannot connect to Qdrant Cloud"
- Verify QDRANT_URL is correct
- Check QDRANT_API_KEY is correct
- Ensure cluster is "Ready" in dashboard

### "API Key not recognized"
- Copy API key again from dashboard
- Make sure no extra spaces

### "Database size exceeded"
- Free tier is 500MB (plenty for your use case)
- Each story index ~100KB
- Your data: ~50-100MB max

---

## ✅ Ready?

1. Create Qdrant Cloud account
2. Get credentials
3. Update `.env`
4. Build database: `python rebuild_db.py`
5. Push code to GitHub
6. Add secrets to Streamlit Cloud
7. Deploy!

**Your app is now powered by professional managed database!** 🚀
