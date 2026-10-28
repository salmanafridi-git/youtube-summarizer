# 🎬 YouTube Video Summarizer

A Streamlit app that takes a YouTube link, fetches its transcript, and uses Google Gemini to produce:

- a short summary
- key points
- timestamps / chapters
- study notes with a quiz

Built with Python, Streamlit, the Google Gemini API (Google AI Studio key), and code generated with Claude.

## Features

- Supports `watch`, `youtu.be`, `shorts`, `embed` and `live` links
- Output in several languages (English, Urdu, Hindi, Arabic, ...)
- Manual transcript paste as a fallback
- Download the result as Markdown

## Project structure

```
youtube-summarizer/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml      # local only, never commit
```

## Setup

1. Clone the repo and enter the folder:
   ```bash
   git clone https://github.com/<your-username>/youtube-summarizer.git
   cd youtube-summarizer
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).
4. Create `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "your-key-here"
   ```
   (Or skip this and paste the key in the app sidebar.)
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## .gitignore

```
venv/
__pycache__/
.streamlit/secrets.toml
.env
```

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub (without `secrets.toml`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app**, choose your repo, branch `main`, and main file `app.py`.
4. Open **Advanced settings → Secrets** and add:
   ```toml
   GOOGLE_API_KEY = "your-key-here"
   ```
5. Click **Deploy**.

## Known limitations

- Videos without captions cannot be summarized (use the manual paste option).
- YouTube sometimes blocks transcript requests from cloud servers. If that happens on the deployed app, paste the transcript manually or run the app locally.
- Free Gemini API keys have rate limits.
- If the model name stops working, update it in the sidebar (see the model list in Google AI Studio).

## Ideas for improvement

- Chat with the video (ask follow-up questions)
- Summarize whole playlists
- Export to PDF
- Save history of summaries

## License

MIT
