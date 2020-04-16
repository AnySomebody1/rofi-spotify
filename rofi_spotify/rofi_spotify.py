#!/usr/bin/env python3

import argparse
import configparser
import os
import subprocess
import sys

import appdirs
import spotipy
import spotipy.util as util
from rofi import Rofi

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--add-to-playlist", action="store_true", help="Add current track to a playlist")

parser.add_argument('-i', '--case-sensitive', action='store_true', help='Enable case sensitivity')

parser.add_argument('-r', '--args', nargs=argparse.REMAINDER, help='Command line arguments for rofi. '
                                                                   'Separate each argument with a space.')

args = parser.parse_args()

def load_config():
    config_dir = appdirs.user_config_dir('rofi-spotify')
    config_path = os.path.join(config_dir, 'rofi-spotify.conf')

    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        os.environ["SPOTIPY_CLIENT_ID"] = config['spotipy']['client_id']
        os.environ["SPOTIPY_CLIENT_SECRET"] = config['spotipy']['client_secret']
        os.environ["SPOTIPY_REDIRECT_URI"] = config['spotipy']['redirect_uri']
        os.environ["SPOTIFY_USERNAME"] = config['spotify']['spotify_username']

    else:
        print("No config file found, let's create one...")
        print("Please visit https://developer.spotify.com/dashboard/applications and click on \"Create a client id\".")
        print("Enter arbitrary name and description and select appropriate options in the next steps.")
        print("Click on \"Edit Settings\" and add an arbitrary Redirect URI, for instance http://127.0.0.1/ by entering"
              " it, clicking on \"Add\" and finally on \"Save Settings\" below.")

        config = configparser.ConfigParser()
        config['spotipy'] = {}
        config['spotipy']['client_id'] = str(input("Please enter the Client ID you received after the previous step: "))
        config['spotipy']['client_secret'] = str(input("Please enter the Client Secret you received after the previous step: "))
        config['spotipy']['redirect_uri'] = str(input("Please enter the Redirect URI you added: "))

        config['spotify'] = {}
        config['spotify']['spotify_username'] = str(input("Please enter your Spotify username. "))

        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        load_config()
    return config_dir

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
    config_dir = load_config()
    rofi = Rofi()

    rofi_args = args.args or []
    if not args.case_sensitive:
        rofi_args = rofi_args.append('-i')

    username = os.getenv("SPOTIFY_USERNAME")
    scope = "user-library-read user-read-currently-playing user-read-playback-state user-library-modify " \
            "playlist-modify-private playlist-read-private playlist-modify-public playlist-read-collaborative"
    token = util.prompt_for_user_token(username, scope=scope, cache_path=config_dir + "/token")
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
        sys.exit(0)

    track_id = getCurrentTrackID(sp)
    track_artists, track_name = getArtistTitleForID(sp, track_id)
    index, key = rofi.select("Currently playing: " + track_artists + "-" + track_name + " - what do you want to do?",
                             ['Add current song to playlist'], rofi_args=rofi_args)
    if index == 0:
        subprocess.run(["rofi-spotify", "-a" + rofi_args])
    sys.exit(0)

