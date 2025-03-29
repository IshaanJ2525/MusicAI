import os
import streamlit as st
import pandas as pd
import shutil
import random

# Define directories
UPLOAD_FOLDER = "uploaded_music"
SORTED_FOLDER = "sorted_music"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SORTED_FOLDER, exist_ok=True)

# Function to categorize songs by multiple criteria
def categorize_songs(upload_path, sorted_path):
    for song in os.listdir(upload_path):
        if song.endswith((".mp3", ".wav", ".flac")):
            song_path = os.path.join(upload_path, song)
            song_name = os.path.splitext(song)[0]
            
            # Extract metadata (assuming naming format: artist_song_genre_language.mp3)
            parts = song_name.split("_")
            if len(parts) >= 4:
                artist, title, genre, language = parts[:4]
                
                # Create categorized directories
                album_path = os.path.join(sorted_path, f"{artist} - {genre} Album")
                os.makedirs(album_path, exist_ok=True)
                
                # Copy song to album
                shutil.copy(song_path, os.path.join(album_path, song))

# Function to scan sorted albums
def scan_albums(sorted_path):
    albums = []
    for album in os.listdir(sorted_path):
        album_path = os.path.join(sorted_path, album)
        if os.path.isdir(album_path):
            albums.append({
                "Album": album,
                "Songs": os.listdir(album_path)
            })
    return albums

# Streamlit UI
st.title("AI Music Recommendation System")

if st.button("Categorize Songs"):
    categorize_songs(UPLOAD_FOLDER, SORTED_FOLDER)
    st.success("Songs have been categorized into albums!")

albums = scan_albums(SORTED_FOLDER)
if albums:
    st.write("### Created Albums")
    for album in albums:
        with st.expander(album["Album"]):
            for song in album["Songs"]:
                song_path = os.path.join(SORTED_FOLDER, album["Album"], song)
                if st.button(f"Play {song}"):
                    st.session_state['current_song'] = song
                    st.session_state['current_song_path'] = song_path

# Display current playing song at the bottom
if 'current_song' in st.session_state:
    st.markdown(f"### 🎵 Now Playing: {st.session_state['current_song']}")
    st.audio(st.session_state['current_song_path'])
