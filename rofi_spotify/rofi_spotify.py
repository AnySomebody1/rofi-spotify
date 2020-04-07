#!/usr/bin/env python3

import argparse
import os
import sys

import spotipy
import spotipy.util as util

from rofi import Rofi

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--add-to-playlist', action='store_true', help='Add current track to a playlist')

args = parser.parse_args()


def select(data, prompt, rofi, select=None):
    index, key = rofi.select(prompt, data, select=select)

    if key == -1:
        sys.exit()

    return index

def run():
    rofi = Rofi()

    username = os.environ.get("ROFI_SPOTIFY_USERNAME")
    scope = 'user-library-read user-read-currently-playing user-read-playback-state user-library-modify playlist-modify-private playlist-read-private playlist-modify-public playlist-read-collaborative'
    token = util.prompt_for_user_token(username, scope)
        
    sp = spotipy.Spotify(token)
    print(args)
    if args.add_to_playlist:
        playlists = sp.current_user_playlists(limit=50)
        options = ['Red', 'Green', 'Blue', 'White', 'Silver', 'Black', 'Other']
        playlists_names = [d['name'] for d in playlists['items']]
        index, key = rofi.select('To which playlist do you want to add the current track?', playlists_names)
        target_playlist_id = playlists['items'][index]['id']
        current_playback = sp.current_playback()
        track_id = current_playback["item"]["uri"].split(":")[2]
        results = sp.user_playlist_add_tracks(username, target_playlist_id, {track_id})
#run()