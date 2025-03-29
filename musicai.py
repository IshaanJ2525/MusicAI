import os
import streamlit as st
import pandas as pd
import shutil
import random

# Define directories
BASE_FOLDER = "base_music"
SORTED_FOLDER = "sorted_music"
os.makedirs(BASE_FOLDER, exist_ok=True)
os.makedirs(SORTED_FOLDER, exist_ok=True)

# Function to categorize songs by multiple criteria
def categorize_songs(base_path, sorted_path):
    for song in os.listdir(base_path):
        if song.endswith((".mp3", ".wav", ".flac")):
            song_path = os.path.join(base_path, song)
            song_name = os.path.splitext(song)[0]
            
            # Extract metadata (assuming naming format: artist_song_genre_language.mp3)
            parts = song_name.split("_")
            if len(parts) >= 4:
                artist, title, genre, language = parts[:4]
                
                # Create categorized directories
                artist_path = os.path.join(sorted_path, "Artists", artist)
                genre_path = os.path.join(sorted_path, "Genres", genre)
                language_path = os.path.join(sorted_path, "Languages", language)
                
                os.makedirs(artist_path, exist_ok=True)
                os.makedirs(genre_path, exist_ok=True)
                os.makedirs(language_path, exist_ok=True)
                
                # Copy song to each category
                shutil.copy(song_path, os.path.join(artist_path, song))
                shutil.copy(song_path, os.path.join(genre_path, song))
                shutil.copy(song_path, os.path.join(language_path, song))

# Function to scan sorted directory
def scan_sorted_directory(sorted_path):
    music_data = []
    for category in os.listdir(sorted_path):
        category_path = os.path.join(sorted_path, category)
        if os.path.isdir(category_path):
            for subcategory in os.listdir(category_path):
                subcategory_path = os.path.join(category_path, subcategory)
                if os.path.isdir(subcategory_path):
                    for song in os.listdir(subcategory_path):
                        music_data.append({
                            "Category": category,
                            "Subcategory": subcategory,
                            "Song": song,
                            "Path": os.path.join(subcategory_path, song)
                        })
    return pd.DataFrame(music_data)

# Streamlit UI
st.title("AI Music Recommendation System")

if st.button("Categorize Songs"):
    categorize_songs(BASE_FOLDER, SORTED_FOLDER)
    st.success("Songs have been categorized!")

if st.button("Scan Sorted Music Library"):
    df = scan_sorted_directory(SORTED_FOLDER)
    if not df.empty:
        st.write("### Sorted Songs Database:")
        st.dataframe(df)
    else:
        st.write("No sorted songs found. Please categorize your music.")

# Select category and playback mode
categories = os.listdir(SORTED_FOLDER)
if categories:
    selected_category = st.selectbox("Select Category:", categories)
    subcategories = os.listdir(os.path.join(SORTED_FOLDER, selected_category))
    if subcategories:
        selected_subcategory = st.selectbox("Select Subcategory:", subcategories)
        playback_mode = st.radio("Playback Mode:", ["In Order", "Shuffle"])
        
        subcategory_songs = os.listdir(os.path.join(SORTED_FOLDER, selected_category, selected_subcategory))
        if playback_mode == "Shuffle":
            random.shuffle(subcategory_songs)
        
        st.write("### Songs:")
        for song in subcategory_songs:
            st.write(f"🎵 {song}")
