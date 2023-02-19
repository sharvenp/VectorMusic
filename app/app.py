
from flask import Flask, render_template, send_from_directory, request
from song_loader import load_songs, query_music
import underscore as _
import os
from dotenv import load_dotenv
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
import time
import threading

load_dotenv()

SONG_DIR = os.getenv('MUSIC_DIR')
TRACK_REFRESH_RATE = 20  # seconds

tracks = {}
app = Flask(__name__)
# limiter = Limiter(app, key_func=get_remote_address)

# Set up track refreshing thread
def refresh_tracks():
    while 1:
        time.sleep(TRACK_REFRESH_RATE)
        print("Refreshing track list...")
        new_tracks = load_songs()
        tracks.clear()
        tracks.update(new_tracks)
tracks.update(load_songs())
thread = threading.Thread(
    name='vector_music_refresh_tracks', target=refresh_tracks)
thread.setDaemon(True)
thread.start()

# Flask code

@app.route("/")
def index():
    return render_template('index.html', body=render_template("home.html"))


@app.route("/music", methods=['GET'])
def musiclist():

    query = request.args.get('q')
    start_idx = request.args.get('start')
    row_count = request.args.get('rows')

    is_last_row = False
    if row_count is not None:
        row_count = max(int(row_count), 0)
    else:
        row_count = len(tracks)
        is_last_row = True

    if start_idx is not None:
        start_idx = max(int(start_idx), 0)
    else:
        start_idx = 0

    if query is None:
        query = ""

    queried_music = query_music(list(tracks.values()), query.lower())
    rows = _.chunk(queried_music, 4)

    is_last_row = (start_idx + row_count) >= len(rows)
    is_first_row = start_idx == 0
    rows = rows[start_idx:(start_idx + row_count)]

    return render_template('index.html', body=render_template("songlist.html", previous_rows=max(0, start_idx - row_count), first_row=is_first_row, next_rows=(start_idx + row_count), last_row=is_last_row, row_count=row_count, song_rows=rows, query=query))


@app.route("/music/<id>")
def music(id):
    if (id not in tracks):
        return render_template('index.html', body=render_template('notfound.html'))
    return render_template('index.html', body=render_template("song.html", song=tracks[id]))


# @limiter.limit("6/minute")
@app.route('/music/<id>/download')
def download(id):
    return send_from_directory(SONG_DIR, tracks[id]['filename'], as_attachment=True)


@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('index.html', body=render_template('toomanyrequests.html'))


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=9000)
