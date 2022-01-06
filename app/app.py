
from flask import Flask, render_template
from song_loader import load_songs
import underscore as _

music = {}
app = Flask(__name__) 

@app.route("/") 
def index(): 
    return render_template('index.html', body=render_template("home.html"))

@app.route("/music") 
def musiclist(): 
    return render_template('index.html', body=render_template("songlist.html", song_chunks=_.chunk(list(music.values()), 4)))

@app.route("/music/<id>") 
def music(id): 
    if (id not in music):
        return render_template('index.html', body=render_template('notfound.html'))
    return render_template('index.html', body=render_template("song.html", song=music[id]))


if __name__ == '__main__':
    # load all songs
    music = load_songs()
    app.run(debug=True, host="0.0.0.0")