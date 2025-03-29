import os
import streamlit as st
import pandas as pd
import shutil
import random
import json

# Define directories
SORTED_FOLDER = "sorted_music"
USER_DATA = "user_data.json"
os.makedirs(SORTED_FOLDER, exist_ok=True)

# Load user data
def load_users():
    if os.path.exists(USER_DATA):
        with open(USER_DATA, "r") as f:
            return json.load(f)
    return {}

# Save user data
def save_users(users):
    with open(USER_DATA, "w") as f:
        json.dump(users, f, indent=4)

# User authentication
users = load_users()
current_user = None

def authenticate():
    global current_user
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "Login"

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.title("🎵 AI Music System")
        auth_mode = st.sidebar.radio("Select", ["Login", "Sign Up"], index=(0 if st.session_state.auth_mode == "Login" else 1))
        st.session_state.auth_mode = auth_mode

        if auth_mode == "Login":
            username = st.sidebar.text_input("Username", placeholder="Enter your username")
            password = st.sidebar.text_input("Password", type="password", placeholder="Enter your password")
            if st.sidebar.button("Login", use_container_width=True):
                if username in users and users[username]["password"] == password:
                    st.sidebar.success(f"Welcome back, {username}!")
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                else:
                    st.sidebar.error("Invalid credentials")
        else:
            username = st.sidebar.text_input("New Username", placeholder="Choose a username")
            password = st.sidebar.text_input("New Password", type="password", placeholder="Create a password")
            if st.sidebar.button("Sign Up", use_container_width=True):
                if username in users:
                    st.sidebar.error("Username already exists")
                else:
                    users[username] = {"password": password, "liked_songs": []}
                    save_users(users)
                    st.sidebar.success("Account created! Please log in.")
    
authenticate()

# UI for welcome screen
if not st.session_state.get("logged_in", False):
    st.markdown("""
        # 🎶 Welcome to AI Music Recommendation System
        Explore a world of music tailored to your taste. 
        Login or Sign up to start your journey!
    """)
else:
    st.title("🎶 AI Music Recommendation System")
    st.markdown(f"## Welcome, {st.session_state.current_user}")

    # Function to categorize songs
    def categorize_songs(uploaded_files, sorted_path):
        for uploaded_file in uploaded_files:
            song_name = uploaded_file.name
            if song_name.endswith((".mp3", ".wav", ".flac", ".mp4")):
                song_path = os.path.join(sorted_path, song_name)
                with open(song_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                parts = os.path.splitext(song_name)[0].split("_")
                if len(parts) >= 4:
                    artist, title, genre, language = parts[:4]
                    
                    album_path = os.path.join(sorted_path, f"{artist} - {genre} Album")
                    os.makedirs(album_path, exist_ok=True)
                    shutil.move(song_path, os.path.join(album_path, song_name))

    # Function to scan albums
    def scan_albums(sorted_path):
        albums = []
        for album in os.listdir(sorted_path):
            album_path = os.path.join(sorted_path, album)
            if os.path.isdir(album_path):
                albums.append({
                    "Album": album,
                    "Songs": os.listdir(album_path),
                    "Count": len(os.listdir(album_path))
                })
        return albums

    st.markdown("### Upload and Categorize Songs")
    uploaded_files = st.file_uploader("Upload Songs (MP3, WAV, FLAC, MP4)", accept_multiple_files=True, type=["mp3", "wav", "flac", "mp4"], help="Upload multiple songs to categorize them into albums automatically.")
    if st.button("Categorize Songs", use_container_width=True) and uploaded_files:
        categorize_songs(uploaded_files, SORTED_FOLDER)
        st.success("Songs have been categorized into albums!")
    
    albums = scan_albums(SORTED_FOLDER)
    if albums:
        st.write("## 🎼 Created Albums")
        for album in albums:
            with st.expander(f"🎵 {album['Album']} ({album['Count']} Songs)"):
                for song in album["Songs"]:
                    song_path = os.path.join(SORTED_FOLDER, album["Album"], song)
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if song.endswith(".mp4"):
                            st.video(song_path)
                        else:
                            if st.button(f"▶ Play {song}", use_container_width=True):
                                st.session_state['current_song'] = song
                                st.session_state['current_song_path'] = song_path
                    with col2:
                        if st.button(f"❤️ Like", key=song, use_container_width=True):
                            users[st.session_state.current_user]["liked_songs"].append(song)
                            save_users(users)
    
    # Display liked songs
    if users[st.session_state.current_user]["liked_songs"]:
        st.write("## ❤️ Liked Songs")
        for liked_song in users[st.session_state.current_user]["liked_songs"]:
            st.write(f"🎶 {liked_song}")

    # Display current playing song at the bottom
    if 'current_song' in st.session_state:
        st.markdown("---")
        st.markdown(f"### 🎵 Now Playing: {st.session_state['current_song']}")
        if st.session_state['current_song'].endswith(".mp4"):
            st.video(st.session_state['current_song_path'])
        else:
            st.audio(st.session_state['current_song_path'])
