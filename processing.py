'''
utility functions for getting and processing data from spotify api
'''
import spotipy

import os
from dotenv import load_dotenv
load_dotenv()
# API authentication
username = os.getenv('SPOTIFY_USERNAME')

def init(scope='playlist-read-private'):
    token = spotipy.util.prompt_for_user_token(username, scope=scope)

    global sp

    sp = spotipy.Spotify(auth=token)
    return sp


def print_tracks(tracks):
    '''prints track name and artist for list of tracks'''
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'],
            track['name']))


def print_playlist(playlist):
    '''prints playlist name, length, and tracks'''
    print(playlist['name'])
    print ('  total tracks', playlist['tracks']['total'])
    results = sp.playlist(playlist['id'],
        fields="tracks,next")
    tracks = results['tracks']
    print_tracks(tracks)
    while tracks['next']:
        tracks = sp.next(tracks)
        print_tracks(tracks)


def get_tracks_IDs(tracks):
    '''gets track IDs for each track in `tracks`'''

    track_IDs = [item['track']['id'] for item in tracks['items']]
    while tracks['next']:
       tracks = sp.next(tracks)
       track_IDs += [item['track']['id'] for item in tracks['items']]

    # filter out any invalid None IDs from list
    track_IDs = list(filter(None, track_IDs))

    return track_IDs

feature_names = ['id','danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']

def get_tracks_audio_features(tracks):
    '''returns dataframe-like dictionary of the features of the tracks in the given playlist'''

    # initialize playlist features dict
    tracks_features = {}
    for feature_name in feature_names:
        tracks_features[feature_name] = []

    # get IDs of tracks in playlist for sp.audio_features function
    track_IDs = get_tracks_IDs(tracks)

    # sp.audio_features only works with 100 tracks at a time, so...
    tracks_done = 0

    while len(track_IDs) - tracks_done > 100:
        track_features = sp.audio_features(track_IDs[tracks_done:tracks_done+100])
        tracks_done += 100

        for track in track_features:
            for feature_name in feature_names:
                tracks_features[feature_name].append(track[feature_name])

    track_features = sp.audio_features(track_IDs[tracks_done:])

    for track in track_features:
        for feature_name in feature_names:
            tracks_features[feature_name].append(track[feature_name])

    return tracks_features