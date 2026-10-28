import re

import streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi

# ---------- Page setup ----------
st.set_page_config(page_title="YouTube Video Summarizer", page_icon="🎬", layout="wide")
st.title("🎬 YouTube Video Summarizer")
st.caption("Paste a YouTube link and get a summary, key points, timestamps and study notes.")

MAX_CHARS = 300_000  # safety limit for very long videos


# ---------- Helpers ----------
def get_api_key() -> str:
    """Read the key from Streamlit secrets, or fall back to the sidebar input."""
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return ""


def extract_video_id(url: str):
    """Return the 11-character video ID from common YouTube URL formats."""
    patterns = [
        r"(?:v=|/videos/|embed/|youtu\.be/|/shorts/|/live/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fmt_time(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


@st.cache_data(show_spinner=False)
def fetch_transcript(video_id: str, languages: tuple):
    """Fetch the transcript and return it as lines like '[01:23] text'."""
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id, languages=list(languages))
    lines = [f"[{fmt_time(item.start)}] {item.text}" for item in fetched]
    return "\n".join(lines)


def build_prompt(transcript: str, mode: str, language: str) -> str:
    instructions = {
        "Short summary": (
            "Write a clear summary of the video in 5-8 sentences, then give a "
            "one-line takeaway."
        ),
        "Key points": (
            "List the 8-12 most important points as bullet points. "
            "Each bullet should be one or two sentences."
        ),
        "Timestamps / chapters": (
            "Create a chapter list. For each chapter give the start timestamp "
            "(use the [mm:ss] times from the transcript) and a short title plus "
            "one sentence describing it."
        ),
        "Study notes + quiz": (
            "Write structured study notes with headings and bullet points, then "
            "create 5 multiple-choice questions with the correct answers at the end."
        ),
    }
    return f"""You are an expert note-taker. Below is the transcript of a YouTube video.
Each line starts with its timestamp.

Task: {instructions[mode]}
Write the answer in {language}. Use Markdown formatting.
Only use information from the transcript. Do not invent facts.

TRANSCRIPT:
{transcript[:MAX_CHARS]}
"""


def ask_gemini(api_key: str, model: str, prompt: str) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text


# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = get_api_key() or st.text_input(
        "Google AI Studio API key", type="password", help="Get one at aistudio.google.com"
    )
    model = st.text_input("Gemini model", value="gemini-3.5-flash")
    mode = st.selectbox(
        "Output type",
        ["Short summary", "Key points", "Timestamps / chapters", "Study notes + quiz"],
    )
    language = st.selectbox(
        "Output language", ["English", "Urdu", "Hindi", "Arabic", "French", "Spanish", "German"]
    )
    transcript_langs = st.text_input(
        "Transcript language codes (comma separated)", value="en,ur,hi"
    )

# ---------- Main area ----------
url = st.text_input("YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")

with st.expander("Transcript not loading? Paste it manually instead"):
    manual_transcript = st.text_area("Paste transcript text here (optional)", height=150)

if st.button("Summarize", type="primary"):
    if not api_key:
        st.error("Please add your Google AI Studio API key in the sidebar.")
        st.stop()

    transcript = manual_transcript.strip()

    if not transcript:
        video_id = extract_video_id(url)
        if not video_id:
            st.error("That doesn't look like a valid YouTube link.")
            st.stop()

        st.video(f"https://www.youtube.com/watch?v={video_id}")
        langs = tuple(code.strip() for code in transcript_langs.split(",") if code.strip())

        with st.spinner("Fetching transcript..."):
            try:
                transcript = fetch_transcript(video_id, langs)
            except Exception as e:
                st.error(
                    "Could not get the transcript. The video may have no captions, "
                    "or YouTube blocked the request. Try the manual paste option above."
                )
                st.exception(e)
                st.stop()

    with st.spinner("Gemini is thinking..."):
        try:
            result = ask_gemini(api_key, model, build_prompt(transcript, mode, language))
        except Exception as e:
            st.error("Gemini API error. Check your API key and model name.")
            st.exception(e)
            st.stop()

    st.session_state["result"] = result
    st.session_state["transcript"] = transcript

# ---------- Show results ----------
if "result" in st.session_state:
    tab1, tab2 = st.tabs(["📝 Result", "📜 Transcript"])
    with tab1:
        st.markdown(st.session_state["result"])
        st.download_button(
            "Download as Markdown",
            st.session_state["result"],
            file_name="summary.md",
            mime="text/markdown",
        )
    with tab2:
        st.text_area("Full transcript", st.session_state["transcript"], height=400)
