# PaperLens 🔬

Scientific paper summarizer powered by LivAI. Drop a PDF or paste a URL — get a structured summary in seconds.

## Deploy to Streamlit Community Cloud (free)

> **First time only — takes ~5 minutes.**

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "PaperLens"
git remote add origin https://github.com/YOUR_USERNAME/paperlens.git
git push -u origin main
```

### 2. Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app**
3. Select your `paperlens` repo → branch `main` → file `app.py`
4. Click **Deploy**

You get a URL like `https://yourname-paperlens-app.streamlit.app`

### 3. Use on any device
Open the URL on your phone, tablet, or desktop. Add it to your phone home screen for an app icon.

## Requirements

- LLNL network or VPN access (LivAI is only reachable from LLNL)
- Your LivAI API key (entered in the sidebar each session)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- PDF text is extracted on the server before anything touches LivAI
- Your API key is never stored — entered per session only
- Large PDFs are truncated at 80,000 characters to stay within context limits
