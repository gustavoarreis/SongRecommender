from flask import Flask, render_template, url_for, request, redirect
import pandas as pd
import numpy as np
import ast
import spotipy

app = Flask(__name__)
app.jinja_env.globals.update(str=str)

from spotify import search_tracks, get_nrecs, fetch_features, enhanced_rec, make_playlist

@app.route('/', methods = ['POST', 'GET'])
def index():
    message = request.args.get('message')
    if message == None:
        message = ""
    if request.method == 'POST':
        try:
            name = request.form['content']
            search_results = search_tracks(query = name)
            return render_template('index.html', search_results = search_results)
        except:
            message = "Could not complete your search. Try again!"
            return render_template('home.html', message = message)
    else:  
        return render_template('home.html', message = message)

@app.route('/search/<id>', methods=['POST', 'GET'])
def search(id):
    id = id
    tracks = get_nrecs(reference_track = id)
    song = str(tracks['name'][100] + " by " + tracks['artists'][100])
    features = []
    if request.method == 'POST':
        try:
            features.append(request.form.get('danceability'))
            features.append(request.form.get('energy'))
            features.append(request.form.get('loudness'))
            features.append(request.form.get('mode'))
            features.append(request.form.get('speechiness'))
            features.append(request.form.get('acousticness'))
            features.append(request.form.get('instrumentalness'))
            features.append(request.form.get('liveness'))
            features.append(request.form.get('valence'))
            features.append(request.form.get('tempo'))
            features.append(request.form.get('key'))
            features.append(request.form.get('time_signature'))
            features = [i for i in features if i != None]
            return redirect(url_for('results', id = id, features = features))
        except:
            return render_template('search.html', id = id, features = features, song = song)
    else:
        return render_template('search.html', id = id, features = features, song = song)

@app.route('/results/<id>/<features>', methods=['POST', 'GET'])
def results(id, features):
    id = id
    try:
        features = ast.literal_eval(features)
    except:
        features = [features]
    tracks = get_nrecs(reference_track = id)
    song = str(tracks['name'][100] + " by " + tracks['artists'][100])
    tracks_with_features = fetch_features(tracks)
    recs = enhanced_rec(tracks_with_features, features = features)
    if request.method == 'POST':
        make_playlist(recs, song = song, features = features)
        return redirect(url_for('index', message = "Done! Try again!"))
    return render_template('results.html', song = song, features = features, recs = recs)

if __name__ == "__main__":
    app.run(debug = True)