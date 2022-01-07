
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

def load_songs():
    print("Loading all music...")
    all_music = os.listdir(SONG_DIR);
    processed_music = {}
    for music in all_music:
        # load metadata
        audio_metadata = eyed3.load(f'{SONG_DIR}/{music}')

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
            "dir": f'{SONG_DIR}/{music}',
            "filename": music,
            "title": audio_metadata.tag.title,
            "artist": audio_metadata.tag.artist,
            "album": audio_metadata.tag.album,
            "publisher": audio_metadata.tag.publisher,
            "genre": None if audio_metadata.tag.genre is None else audio_metadata.tag.genre.name,
            "img": encoded_img
        }

        processed_music[track_id] = track_metadata
        
    print(f"Loaded {len(processed_music)} tracks.")
    return processed_music