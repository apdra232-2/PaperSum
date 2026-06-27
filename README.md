# PaperLens 🔬

Scientific paper summarizer for LLNL scientists — powered by LivAI.  
Works on phone, tablet, and desktop. No install needed.

## Deploy to GitHub Pages (free, ~3 minutes)

### 1. Create a GitHub repo
Go to [github.com/new](https://github.com/new), name it `paperlens`, set it to **Public**, create it.

### 2. Upload the file
On the new repo page, click **Add file → Upload files**, drag `index.html` in, commit.

### 3. Enable GitHub Pages
Go to **Settings → Pages → Source**, set branch to `main`, folder to `/ (root)`, save.

### 4. Get your URL
After ~1 minute: `https://YOUR_USERNAME.github.io/paperlens`

### 5. Add to phone home screen
- **iPhone:** Open URL in Safari → Share → Add to Home Screen
- **Android:** Open in Chrome → menu → Add to Home Screen

## Usage

1. Open the app → tap ⚙ → enter your LivAI API key and model name
2. Tap the upload zone to select a PDF from your Files app — or paste a URL
3. Tap **Summarize**

Your API key stays in your browser tab only. GitHub never sees it.

## Requirements

- LLNL network or VPN (LivAI is only reachable from LLNL)
- LivAI API key

## Notes

- PDF text is extracted locally in your browser — only the text goes to LivAI
- If you get a network error, make sure you are on LLNL WiFi or VPN
- Large PDFs are trimmed to 80,000 characters to fit the context window
