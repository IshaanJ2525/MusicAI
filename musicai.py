import streamlit as st
import requests
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import io

# GitHub Details
GITHUB_USERNAME = "YOUR_USERNAME"  # Replace with your GitHub username
REPO_NAME = "YOUR_REPO_NAME"  # Replace with your repo name
MUSIC_FOLDER = "music"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{MUSIC_FOLDER}"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{MUSIC_FOLDER}/"

# Fetch metadata from MP3 files
@st.cache_data
def fetch_albums():
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        albums = {}
        files = response.json()
        for song in files:
            if song["name"].endswith(".mp3"):
                song_url = f"{RAW_BASE_URL}/{song['name']}"
                metadata = fetch_metadata(song_url)
                artist = metadata.get("artist", "Unknown Artist")
                genre = metadata.get("genre", "Unknown Genre")
                album_name = f"{artist} - {genre} Album"
                if album_name not in albums:
                    albums[album_name] = []
                albums[album_name].append((song["name"], song_url))
        return albums
    else:
        st.error("Failed to fetch songs from GitHub. Check your repository settings.")
        return {}

# Extract metadata from MP3 file
@st.cache_data
def fetch_metadata(song_url):
    try:
        response = requests.get(song_url)
        if response.status_code == 200:
            audio = MP3(io.BytesIO(response.content), ID3=EasyID3)
            return {
                "artist": audio.get("artist", ["Unknown"])[0],
                "genre": audio.get("genre", ["Unknown"])[0],
                "title": audio.get("title", ["Unknown"])[0],
            }
    except Exception as e:
        st.error(f"Error fetching metadata: {e}")
    return {}

# Streamlit UI
st.title("🎵 AI Music Recommendation System")
st.write("Browse and play music directly from GitHub.")

# Fetch albums
albums = fetch_albums()
if albums:
    for album, songs in albums.items():
        with st.expander(album):
            for song_name, song_url in songs:
                st.write(f"🎶 {song_name}")
                st.audio(song_url)
else:
    st.warning("No songs found in the GitHub repository.")
