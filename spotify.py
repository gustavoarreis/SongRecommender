import spotipy
import pandas as pd
import os
import configparser

def spotify_authentication():
    import spotipy
    import configparser
    cfg = configparser.RawConfigParser()
    cfg.read('config.cfg')
    SPOTIPY_CLIENT_ID = cfg.get('KEYS','client_id').strip('"')
    SPOTIPY_CLIENT_SECRET = cfg.get('KEYS','client_secret').strip('"')
    SPOTIPY_REDIRECT_URI = cfg.get('KEYS','redirect_uri').strip('"')
    scope = ['user-read-playback-position','user-read-email', 'user-library-read', 
        'user-top-read', 'playlist-modify-public',
        'ugc-image-upload', 'user-follow-modify', 
        'user-modify-playback-state', 'user-read-recently-played', 'user-read-private',
        'playlist-read-private', 'user-library-modify', 'playlist-read-collaborative', 
        'playlist-modify-private', 'user-follow-read', 
        'user-read-playback-state', 'user-read-playback-state']
    sp_oauth = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                               client_secret=SPOTIPY_CLIENT_SECRET,
                               redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope)
    return sp_oauth

def clean_tracks(df):
    df = df.drop(columns = 
                         ['external_ids','type',
                          'href', 'uri', 
                          'available_markets', 
                          'disc_number', 'explicit','is_local',
                          'preview_url','track_number', 'duration_ms', 'popularity'])
    keys_to_extract = ["name"]
    for i in df.index:
        df['album'][i] = df['album'][i]['name']
        df['artists'][i] = {key: df['artists'][i][0][key] for key in keys_to_extract}['name']
        df['external_urls'][i] = df['external_urls'][i]['spotify']
    return df


def search_tracks(query):
    sp_oauth = spotify_authentication()
    token_info = sp_oauth.get_cached_token()
    token = token_info['access_token']
    sp = spotipy.Spotify(auth = token)
    search_track = sp.search(q = query, type = "track")
    search_track = pd.DataFrame(search_track['tracks']['items'])
    search_track = clean_tracks(search_track)
    return search_track

def get_recs(reference_track):
    sp_oauth = spotify_authentication()
    token_info = sp_oauth.get_cached_token()
    token = token_info['access_token']
    sp = spotipy.Spotify(auth = token)
    recs = sp.recommendations(seed_tracks = [reference_track], limit = 100)
    track = sp.track(track_id = reference_track)
    tracks = pd.DataFrame(recs['tracks'])
    tracks = tracks.append(track, ignore_index = True)
    tracks = clean_tracks(tracks)
    return tracks

def get_nrecs(reference_track, n = 200):
    tracks = get_recs(reference_track)
    while len(tracks) < n:
        tracks2 = get_recs(reference_track)
        tracks = tracks.append(tracks2, ignore_index=True)
        tracks = tracks.drop_duplicates()
    return tracks

def fetch_features(df):
    """Get audio features for the collected tracks"""
    sp_oauth = spotify_authentication()
    token_info = sp_oauth.get_cached_token()
    token = token_info['access_token']
    sp = spotipy.Spotify(auth = token)
    df['danceability'] = float()
    df['energy'] = float()
    df['loudness'] = float()
    df['mode'] = float()
    df['speechiness'] = float()
    df['acousticness'] = float()
    df['instrumentalness'] = float()
    df['liveness'] = float()
    df['valence'] = float()
    df['tempo'] = float()
    df['key'] = float()
    df['time_signature'] = float()
    for i in df.index:
        features = sp.audio_features(tracks = df['id'][i])
        df['danceability'][i] = features[0]['danceability']
        df['energy'][i] = features[0]['energy']
        df['loudness'][i] = features[0]['loudness']
        df['mode'][i] = features[0]['mode']
        df['speechiness'][i] = features[0]['speechiness']
        df['acousticness'][i] = features[0]['acousticness']
        df['instrumentalness'][i] = features[0]['instrumentalness']
        df['liveness'][i] = features[0]['liveness']
        df['valence'][i] = features[0]['valence']
        df['tempo'][i] = features[0]['tempo']
        df['key'][i] = features[0]['key']
        df['time_signature'][i] = features[0]['time_signature']
    return df

import numpy as np

def euclidian(point_a, point_b):
    """Calculates euclidian distance between points"""
    distance = 0.000
    for i in range(len(point_a)-1):
        distance += (point_a[i] - point_b[i])**2
    return np.sqrt(distance)

def enhanced_rec(df, features, show = 25):
    """Sorts recommendations selecting nearest neighbors. Select criteria of similarity(features)."""
    df["euclidian"] = float()
    a = []
    for n in features:
        a.append(df[n][100])
    for i in df.index:
        b = []
        for n in features:
            b.append(df[n][i])
        df["euclidian"][i] = euclidian(point_a = a, point_b = b)
    df1 = df.sort_values("euclidian")[0:show]
    return df1

def make_playlist(recs, song, features):
    import configparser
    cfg = configparser.RawConfigParser()
    cfg.read('config.cfg')
    user = cfg.get('KEYS','client_id').strip('"')
    sp_oauth = spotify_authentication()
    token_info = sp_oauth.get_cached_token()
    token = token_info['access_token']
    sp = spotipy.Spotify(auth = token)
    playlist_name = str("Based on " + str(song))
    description = str("Built using track's " + str(features) + " by Playlist Wizard")
    playlist = sp.user_playlist_create(user = user, name = playlist_name, 
                     public=True, description= description)
    sp.user_playlist_add_tracks(user = user, playlist_id = playlist['id'], tracks = recs['id'])