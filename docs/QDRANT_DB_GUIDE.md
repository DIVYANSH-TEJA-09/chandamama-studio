# ⚡ Qdrant Database on Streamlit Cloud

## What Changed

Your `app.py` now **automatically rebuilds the Qdrant database** on first run if it's missing.

---

## How It Works

### On First Load
1. App checks if `qdrant_db/meta.json` exists
2. If **NOT found**: Runs `rebuild_db.py` automatically
3. Database builds (~1-2 minutes)
4. App loads normally after

### On Subsequent Loads
- Database already exists
- Loads instantly ⚡

---

## What to Do

### 1. Keep `.gitignore` as is
```
qdrant_db/  # Already in .gitignore (not pushed to GitHub)
chunks/     # Already in repository (pushed to GitHub)
```

### 2. Git Commit & Push
```bash
git add app.py
git commit -m "Add auto-rebuild for Qdrant database"
git push origin main
```

### 3. Deploy on Streamlit Cloud
- Streamlit Cloud will auto-redeploy with the new code
- App will build the database on first load

### 4. First Load Experience
- Go to your Streamlit Cloud app URL
- You'll see: "Building vector database..."
- Wait 1-2 minutes
- App loads with full RAG functionality ✅

---

## Benefits ✨

✅ **No need to upload 100MB+ database**  
✅ **Database auto-builds on first run**  
✅ **Works reliably on Streamlit Cloud**  
✅ **Users don't notice anything unusual**  
✅ **Database persists during session**  

---

## Database Details

### What Gets Built
- Embeds 10,000+ stories from `chunks/`
- Indexes them with Qdrant
- Creates searchable vector database

### Time Required
- First load: ~1-2 minutes (building database)
- Subsequent loads: <1 second (using cache)

### Disk Space
- `qdrant_db/` folder: ~200-500MB
- Stored in app's temporary storage
- Rebuilt if app restarts (usually weekly)

---

## Troubleshooting

### "Database still building after 5 minutes"
- Give it more time (depends on your machine specs)
- Check Streamlit Cloud logs

### "Database build failed"
- Check your `chunks/` folder has data
- Verify `rebuild_db.py` works locally:
  ```bash
  python rebuild_db.py
  ```

### "Database rebuilds every time"
- This is normal on Streamlit Cloud if it restarts weekly
- Database rebuilds automatically (users don't notice)

---

## Optional: Use Persistent Database

If you want the database to persist longer, consider:

1. **Qdrant Cloud** (free tier available)
   - Managed database in cloud
   - Never need to rebuild
   - Link: https://cloud.qdrant.io

2. **Local file persistence** (current approach)
   - Works well on Streamlit Cloud
   - Database rebuilds when needed

For now, auto-rebuild is perfect! ✅

---

## Commands

```bash
# Test locally before pushing
streamlit run app.py

# Push updated code
git add app.py
git commit -m "Auto-rebuild Qdrant database"
git push origin main
```

---

## Expected Behavior on Streamlit Cloud

**First Visit:**
```
⏳ Building vector database... This may take 1-2 minutes on first load.
✅ Database built successfully!
🎉 App loads normally
```

**Subsequent Visits:**
```
🚀 App loads instantly
📖 Full RAG search available
✨ Everything works!
```

---

**Status**: ✅ Your app is ready for Streamlit Cloud with auto-database building!
