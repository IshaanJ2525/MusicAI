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

# Function to scan uploaded directory and categorize songs
def categorize_songs(base_path, sorted_path):
    for artist in os.listdir(base_path):
        artist_path = os.path.join(base_path, artist)
        if os.path.isdir(artist_path):
            artist_sorted_path = os.path.join(sorted_path, artist)
            os.makedirs(artist_sorted_path, exist_ok=True)
            for song in os.listdir(artist_path):
                if song.endswith((".mp3", ".wav", ".flac")):
                    shutil.move(os.path.join(artist_path, song), os.path.join(artist_sorted_path, song))

# Function to scan sorted directory
def scan_sorted_directory(sorted_path):
    music_data = []
    for artist in os.listdir(sorted_path):
        artist_path = os.path.join(sorted_path, artist)
        if os.path.isdir(artist_path):
            for song in os.listdir(artist_path):
                music_data.append({
                    "Artist": artist,
                    "Song": song,
                    "Path": os.path.join(artist_path, song)
                })
    return pd.DataFrame(music_data)

# Streamlit UI
st.title("AI Music Recommendation System")

if st.button("Categorize Songs"):
    categorize_songs(UPLOAD_FOLDER, SORTED_FOLDER)
    st.success("Songs have been categorized!")

if st.button("Scan Sorted Music Library"):
    df = scan_sorted_directory(SORTED_FOLDER)
    if not df.empty:
        st.write("### Sorted Songs Database:")
        st.dataframe(df)
    else:
        st.write("No sorted songs found. Please categorize your music.")

# Select artist and playback mode
artists = os.listdir(SORTED_FOLDER)
if artists:
    selected_artist = st.selectbox("Select Artist:", artists)
    playback_mode = st.radio("Playback Mode:", ["In Order", "Shuffle"])
    
    artist_songs = os.listdir(os.path.join(SORTED_FOLDER, selected_artist))
    if playback_mode == "Shuffle":
        random.shuffle(artist_songs)
    
    st.write("### Songs:")
    for song in artist_songs:
        st.write(f"🎵 {song}")
    
    # Reordering functionality
    reordered_songs = st.text_area("Reorder Songs (Enter song names in order, one per line):")
    if st.button("Save Order") and reordered_songs:
        new_order = reordered_songs.split("\n")
        reordered_path = os.path.join(SORTED_FOLDER, selected_artist)
        
        for idx, song in enumerate(new_order):
            if song in artist_songs:
                os.rename(os.path.join(reordered_path, song), os.path.join(reordered_path, f"{idx:02d}_{song}"))
        st.success("Song order updated!")
