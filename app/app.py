
from flask import Flask, render_template, send_from_directory, request
from song_loader import load_songs
import underscore as _
import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

SONG_DIR = os.getenv('MUSIC_DIR') 

music = {}
app = Flask(__name__) 
limiter = Limiter(app, key_func=get_remote_address)

@app.route("/") 
def index(): 
    return render_template('index.html', body=render_template("home.html"))

@app.route("/music") 
def musiclist(): 
    start_idx = request.args.get('start')
    row_count = request.args.get('rows')
    rows = _.chunk(list(music.values()), 4)
    if row_count is not None:
        row_count = int(row_count)
    else:
        row_count = len(music)

    if start_idx is not None:
        start_idx = int(start_idx) 
    else:
        start_idx = 0

    print(len(rows), len(music), start_idx, row_count)
    rows = rows[start_idx:(start_idx + row_count)]
    return render_template('index.html', body=render_template("songlist.html", song_rows=rows))

@app.route("/music/<id>") 
def music(id): 
    if (id not in music):
        return render_template('index.html', body=render_template('notfound.html'))
    return render_template('index.html', body=render_template("song.html", song=music[id]))


@app.route('/music/<id>/download')
@limiter.limit("5/minute")
def download(id):
    return send_from_directory(SONG_DIR, music[id]['filename'], as_attachment=True)

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('index.html', body=render_template('toomanyrequests.html'))

if __name__ == '__main__':
    # load all songs
    music = load_songs()
    app.run(debug=True, host="0.0.0.0")