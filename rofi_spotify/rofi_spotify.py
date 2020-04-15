#!/usr/bin/env python3

import argparse
import os
import sys

import spotipy
import spotipy.util as util

from rofi import Rofi

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--add-to-playlist", action="store_true", help="Add current track to a playlist")

parser.add_argument('-i', '--case-sensitive', action='store_true', help='Enable case sensitivity')

parser.add_argument('-r', '--args', nargs=argparse.REMAINDER, help='Command line arguments for rofi. '
                                                                   'Separate each argument with a space.')

args = parser.parse_args()


def select(data, prompt, rofi, select=None):
    index, key = rofi.select(prompt, data, select=select)

    if key == -1:
        sys.exit()

    return index

# TODO Only select editable playlists
def getPlaylists(sp, onlyEditable=True):
    return sp.current_user_playlists(limit=50)

def getCurrentTrackID(sp):
    current_playback = sp.current_playback()
    return current_playback['item']['uri'].split(":")[2]

def getArtistTitleForID(sp, track_id):
    meta_track = sp.track(track_id)
    return meta_track['artists'][0]['name'], meta_track['name']

def run():
    rofi = Rofi()
    rofi_args = args.args or []
    if not args.case_sensitive:
        rofi_args = rofi_args.append('-i')
    
    username = os.environ.get("ROFI_SPOTIFY_USERNAME")
    scope = "user-library-read user-read-currently-playing user-read-playback-state user-library-modify playlist-modify-private playlist-read-private playlist-modify-public playlist-read-collaborative"
    token = util.prompt_for_user_token(username, scope)
    sp = spotipy.Spotify(token)

    if args.add_to_playlist:
        track_id = getCurrentTrackID(sp)
        track_artists, track_name = getArtistTitleForID(sp, track_id)
        playlists = getPlaylists(sp)
        playlists_names = [d['name'] for d in playlists['items']]
        index, key = rofi.select("To which playlist do you want to add " + track_artists + "-" +  track_name + "?",
                                playlists_names, rofi_args=rofi_args)
        target_playlist_id = playlists['items'][index]['id']
        results = sp.user_playlist_add_tracks(username, target_playlist_id, {track_id})