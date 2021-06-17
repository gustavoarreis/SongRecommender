import spotipy
import pandas as pd
import os
import configparser
import numpy as np

cfg = configparser.RawConfigParser()
cfg.read('config.cfg') # Read your .cfg file to retrieve API keys
SPOTIPY_CLIENT_ID = cfg.get('KEYS','client_id').strip('"') # Get Client ID
SPOTIPY_CLIENT_SECRET = cfg.get('KEYS','client_secret').strip('"') # Get Client Secret
SPOTIPY_REDIRECT_URI = cfg.get('KEYS','redirect_uri').strip('"') # Get Redirect URI
USERNAME = cfg.get('KEYS', 'username').strip('"') # Get Username
scope = ['user-read-playback-position','user-read-email', 'user-library-read', 
        'user-top-read', 'playlist-modify-public',
        'ugc-image-upload', 'user-follow-modify', 
        'user-modify-playback-state', 'user-read-recently-played', 'user-read-private',
        'playlist-read-private', 'user-library-modify', 'playlist-read-collaborative', 
        'playlist-modify-private', 'user-follow-read', 
        'user-read-playback-state', 'user-read-playback-state'] # Set scope of API interaction

def spotify_authentication():
    """Authenticate your access to the Spotify API"""
    sp_oauth = spotipy.SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                               client_secret=SPOTIPY_CLIENT_SECRET,
                               redirect_uri=SPOTIPY_REDIRECT_URI,scope=scope)
    return sp_oauth

def get_token():
    """Gets token from Spotify API if you don't already have one"""
    token = spotipy.util.prompt_for_user_token(username = USERNAME,
    scope = scope,client_id= SPOTIPY_CLIENT_ID,
                           client_secret=SPOTIPY_CLIENT_SECRET,
                           redirect_uri=SPOTIPY_REDIRECT_URI)
    return token

def clean_tracks(df):
    """Clean any data frame of tracks maintaining only the essencial info"""
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
    """Search reference track"""
    sp_oauth = spotify_authentication() # Authenticate your access
    token_info = sp_oauth.get_cached_token() # Get Token
    if token_info == None:
        token = get_token()
    else:
        token = token_info['access_token'] 
    sp = spotipy.Spotify(auth = token) # Initialize session
    search_track = sp.search(q = query, type = "track") # Query track
    search_track = pd.DataFrame(search_track['tracks']['items']) # Make data frame of search results
    search_track = clean_tracks(search_track) # Clean the data frame
    return search_track

def get_recs(reference_track):
    """Get Spotify recommendations for reference track"""
    sp_oauth = spotify_authentication() # Authenticate your access
    token_info = sp_oauth.get_cached_token() # Get Token
    if token_info == None:
        token = get_token()
    else:
        token = token_info['access_token']
    sp = spotipy.Spotify(auth = token) # Initialize session
    recs = sp.recommendations(seed_tracks = [reference_track], limit = 100) # Fetch 100 recommendations
    track = sp.track(track_id = reference_track) # Fetch reference track info
    tracks = pd.DataFrame(recs['tracks']) # Make data frame of recommendations
    tracks = tracks.append(track, ignore_index = True) # Join the reference track with the recommendations
    tracks = clean_tracks(tracks) # Clean the data frame
    return tracks

def get_nrecs(reference_track, n = 200):
    """Get n recommendations"""
    tracks = get_recs(reference_track)
    while len(tracks) < n:
        tracks2 = get_recs(reference_track)
        tracks = tracks.append(tracks2, ignore_index=True)
        tracks = tracks.drop_duplicates() # Get more recommendations until condition is satisfied
    return tracks

def fetch_features(df):
    """Fetch audio features for the collected tracks"""
    sp_oauth = spotify_authentication() # Authenticate your access
    token_info = sp_oauth.get_cached_token() # Get Token
    if token_info == None:
        token = get_token()
    else:
        token = token_info['access_token']
    sp = spotipy.Spotify(auth = token) # Initialize session
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
        features = sp.audio_features(tracks = df['id'][i]) # Get audio features for each track in data frame
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
        df["euclidian"][i] = euclidian(point_a = a, point_b = b) # Calculates euclidian distance using features
    df1 = df.sort_values("euclidian")[0:show] # Sorts values based on ascending euclidian distance
    return df1

def make_playlist(recs, song, features):
    """Makes playlist with recommended songs"""
    user = USERNAME # Get username
    sp_oauth = spotify_authentication() # Authenticate your access
    token_info = sp_oauth.get_cached_token() # Get Token
    if token_info == None:
        token = get_token()
    else:
        token = token_info['access_token']
    sp = spotipy.Spotify(auth = token) # Initialize session
    playlist_name = str("Based on " + str(song)) # Set playlist name
    description = str("Built using track's " + str(features) + " by Song Recommender") # Set playlist description
    playlist = sp.user_playlist_create(user = user, name = playlist_name, 
                     public=True, description= description) # Creates playlist
    sp.user_playlist_add_tracks(user = user, playlist_id = playlist['id'], tracks = recs['id']) # Adds tracks to playlist