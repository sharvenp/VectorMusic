
import os
import eyed3
import base64
import string
import random
from dotenv import load_dotenv

load_dotenv()

SONG_DIR = os.getenv('MUSIC_DIR') 

def _generate_id():
    # generate random alphanumeric string
    return ''.join(random.choice(string.ascii_lowercase  + string.digits) for _ in range(12))

def _get_files_sorted_by_creation_date(directory):
    file_names = os.listdir(directory);
    all_music = []
    for fn in file_names:
        all_music.append(f'{directory}/{fn}')
    all_music.sort(key=os.path.getmtime)
    return all_music

def load_songs():
    print("Loading all music...")
    all_music = _get_files_sorted_by_creation_date(SONG_DIR);
    processed_music = {}
    for music in all_music:
        # load metadata
        audio_metadata = eyed3.load(music)

        # encode album art into base64
        encoded_img = ''
        for d in audio_metadata.tag.images:
            encoding = base64.b64encode(d.image_data).decode('ascii')
            encoded_img += f'data:image/png;base64,{encoding}'
            

        track_id = _generate_id()
        while track_id in processed_music:
            # no duplicate ids
            track_id = _generate_id()

        track_metadata = {
            "id": track_id,
            "dir": music,
            "filename": music,
            "title": audio_metadata.tag.title or '',
            "artist": audio_metadata.tag.artist or '',
            "album": audio_metadata.tag.album or '',
            "publisher": audio_metadata.tag.publisher or '',
            "genre": '' if audio_metadata.tag.genre is None else audio_metadata.tag.genre.name,
            "img": encoded_img
        }

        processed_music[track_id] = track_metadata
        
    print(f"Loaded {len(processed_music)} tracks.")
    return processed_music

def query_music(songs, query):
    filtered = []
    for song in songs:
        val = (query in song['title'].lower() or
            query in song['artist'].lower()  or
            query in song['album'].lower()  or
            query in song['publisher'].lower()  or 
            query in song['genre'].lower() )

        if val:
            filtered.append(song)
    
    return filtered