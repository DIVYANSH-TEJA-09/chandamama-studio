# 🚀 Deploy to Streamlit Cloud (FREE!)

Your Chandamama Studio app is ready to deploy for FREE on Streamlit Cloud in just 2 minutes!

---

## ✅ What You Have Ready

- ✅ `app.py` - Your Streamlit application
- ✅ `requirements.txt` - All dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.gitignore` - Excludes `.env` from GitHub (secrets safe!)

---

## 🎯 Deployment Steps

### Step 1: Push Your Code to GitHub

```bash
# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Ready for Streamlit Cloud deployment"

# Push to GitHub
git push origin main
```

**If you don't have a GitHub repo yet:**
1. Go to: https://github.com/new
2. Create a new repository
3. Copy the commands shown
4. Run them in your project folder

### Step 2: Deploy on Streamlit Cloud

1. Go to: **https://streamlit.io/cloud**
2. Click **"Deploy an app"** button
3. **Select your GitHub repository**
   - Choose your GitHub account
   - Select `chandamama-studio` repo
   - Select `main` branch
4. **Configure the app**
   - Main file path: `app.py`
   - Python version: 3.9+ (automatic)
5. Click **"Deploy"**

**Wait 1-2 minutes...** Your app will be live! 🎉

---

## 📌 Important: Handle Secrets Safely

Since your `.env` is in `.gitignore`, you need to add secrets to Streamlit Cloud:

1. After deployment, go to **App menu** → **Settings**
2. Click **"Secrets"** tab
3. Add your environment variables:
   ```
   OPENAI_API_KEY = sk-proj-VHYWyLW7XwHXM17MgSa7...
   GEMINI_API_KEY = your_gemini_api_key_here
   HF_TOKEN = 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
   GROQ_API_KEY = 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
   ```
4. Save → App reloads with your secrets

---

## ✨ Your Live App

After deployment, you'll get a URL like:
```
https://chandamama-studio-abc123.streamlit.app
```

Just open it in your browser → Your app is live! 🌟

---

## 🔄 Update Your App

After deployment, updates are automatic:
1. Make changes to your code
2. Commit: `git commit -am "Update"`
3. Push: `git push origin main`
4. Streamlit Cloud auto-redeploys in ~1 minute

---

## 💰 Cost

**Streamlit Cloud**: Completely FREE ✅

- No credit card required
- No limitations
- No hidden fees
- Professional domain included

---

## 🆘 Troubleshooting

### App shows error loading
- Wait 2-3 minutes for initial deployment
- Check "Logs" tab in Streamlit Cloud

### Missing API keys
- Add secrets via Settings → Secrets
- Secrets are loaded from `st.secrets` in Streamlit

### Large file size
- The Qdrant database (`qdrant_db/`) should be ignored
- Verify it's in `.gitignore`

---

## 📖 Quick Commands

```bash
# Test locally before pushing
streamlit run app.py

# Push to GitHub
git add . && git commit -m "msg" && git push origin main

# View deployment status
# Go to: https://streamlit.io/cloud
```

---

## 🎊 You're All Set!

No Azure configuration needed. Just:
1. Push to GitHub
2. Deploy on Streamlit Cloud
3. Share your URL

**Ready to deploy?** Follow the steps above! 🚀
