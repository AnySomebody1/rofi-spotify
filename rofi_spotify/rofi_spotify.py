# TODO Catch errors
# TODO Get only editable playlists
# TODO Try catch errors
# TODO Get all playlists

import argparse
import configparser
import os
import subprocess
import sys
import textwrap

import appdirs
import spotipy
import spotipy.util as util
from rofi import Rofi

def load_config():
    config_dir = appdirs.user_config_dir('rofi-spotify')
    config_path = os.path.join(config_dir, 'rofi-spotify.conf')

    if os.path.exists(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
    else:
        print("No config file found, let's create one...")
        print(textwrap.wrap("Please visit https://developer.spotify.com/dashboard/applications and click on"
                            " \"Create a client id\".", width=70))
        print(textwrap.wrap("Enter arbitrary name and description and select appropriate options in the next steps.", width=70))
        print(textwrap.wrap("Click on \"Edit Settings\" and add an arbitrary Redirect URI, for instance http://localhost:8080 by entering"
              " it, clicking on \"Add\" and finally on \"Save Settings\" below.", width=70))

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
    return config, config_dir

def getPlaylists(sp, onlyEditable=True):
    return sp.current_user_playlists(limit=50)

def getCurrentTrackID(sp):
    current_playback = sp.current_playback()
    if not current_playback:
        raise Exception("Nothing playing")
    else:
        return current_playback['item']['uri'].split(":")[2]

def getCurrentTrack(sp):
    try:
        track_id = getCurrentTrackID(sp)
        track_artists, track_name = getArtistsTitleForID(sp, track_id)
        track_meta = track_artists + "-" + track_name
    except Exception:
        track_meta = "Nothing"
    return track_id, track_meta

def getArtistsTitleForID(sp, track_id):
    meta_track = sp.track(track_id)
    artists = ""
    for index, artist in enumerate(meta_track['artists']):
        if index == 0:
            artists = artist['name']
        else:
            artists = artists + ', ' + artist['name']
    return artists, meta_track['name']

def addTrackToPlaylist(rofi, rofi_args, sp, username, playlist_id, playlist_name, track_id, track_name):
    playlist_tracks_tmp = sp.playlist_tracks(playlist_id,  fields="total,items(track(id))",
                                             additional_types=('track',))
    playlist_tracks = playlist_tracks_tmp
    offset = 100
    while(playlist_tracks_tmp['total'] == 100):
        playlist_tracks_tmp = sp.playlist_tracks(playlist_id, fields="total,items(track(id))", offset=offset,
                                                 additional_types=('track',))
        offset += 100
        playlist_tracks.append(playlist_tracks_tmp)
    playlist_ids = [d['track']['id'] for d in playlist_tracks['items']]
    if track_id in playlist_ids:
        index_add, key_add = rofi.select(track_name + " is already in " + playlist_name
                                         + ". Add anyway? ", ["No", "Yes"], rofi_args=rofi_args)
        if index_add == 0:
            return
        else:
            results = sp.user_playlist_add_tracks(username, playlist_id,  {track_id})
    results = sp.user_playlist_add_tracks(username, playlist_id, {track_id})

def run():
    config, config_dir = load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add-to-playlist", action="store_true", help="Add current track to a playlist")
    parser.add_argument("-st", "--search-track", action="store_true", help="Search for a track")
    parser.add_argument('-i', '--case-sensitive', action='store_true', help='Enable case sensitivity')
    parser.add_argument('-r', '--args', nargs=argparse.REMAINDER, help='Command line arguments for rofi. '                                                                   'Separate each argument with a space.')
    args = parser.parse_args()

    rofi_args = args.args or []
    if not args.case_sensitive:
        rofi_args.append('-i')
    rofi = Rofi()

    scope = "user-library-read user-read-currently-playing user-read-playback-state user-library-modify " \
            "user-modify-playback-state playlist-modify-private playlist-read-private playlist-modify-public"
    token = util.prompt_for_user_token(config['spotify']['spotify_username'],
                                       scope=scope,
                                       client_id=config['spotipy']['client_id'],
                                       client_secret=config['spotipy']['client_secret'],
                                       redirect_uri=config['spotipy']['redirect_uri'],
                                       cache_path=(config_dir + "/token"))
    sp = spotipy.Spotify(token)

    if args.add_to_playlist:
        track_id, track_meta = getCurrentTrack(sp)
        playlists = getPlaylists(sp)
        playlists_names = [d['name'] for d in playlists['items']]
        index, key = rofi.select("To which playlist do you want to add " + track_meta + "? ",
                                playlists_names, rofi_args=rofi_args)
        target_playlist_id = playlists['items'][index]['id']
        addTrackToPlaylist(rofi, rofi_args, sp, config['spotify']['spotify_username'], target_playlist_id,
                           playlists_names[index], track_id, track_meta)
        sys.exit(0)

    if args.search_track:
        trackquery = rofi.text_entry('Search for a track: ', rofi_args=rofi_args)
        results = sp.search(trackquery, limit=50, type="track")
        if not results['tracks']['items']:
            rofi.error("No tracks found.")
        else:
            tracks = []
            for index, track in enumerate(results['tracks']['items']):
                tracks.append({'id': track['id'], 'artists': getArtistsTitleForID(sp, track['id'])[0],
                               'title': track['name']})
            rofi_tracks = [d['artists']+"-" + d['title'] for d in tracks]
            index_track, key_track = rofi.select("Select a track: ", rofi_tracks)
            index_todo, key_todo = rofi.select("What do you want to do with " + rofi_tracks[index_track] + "? ",
                                               ["Add to queue", "Add to playlist"], rofi_args=rofi_args)

            if index_todo == 0:
                sp.add_to_queue(tracks[index_track]['id'])
            if index_todo == 1:
                playlists = getPlaylists(sp)
                playlists_names = [d['name'] for d in playlists['items']]
                index_playlist, key_playlist = rofi.select("To which playlist do you want to add " + rofi_tracks[index_track] + "? ",
                                                           playlists_names, rofi_args=rofi_args)
                target_playlist_id = playlists['items'][index_playlist]['id']
                addTrackToPlaylist(rofi, rofi_args, sp, config['spotify']['spotify_username'], target_playlist_id,
                                   playlists_names[index_playlist], tracks[index_track]['id'], rofi_tracks[index_track])

        sys.exit(0)

    curr_track_id, curr_track_meta = getCurrentTrack(sp)
    index, key = rofi.select("Currently playing: " + curr_track_meta + " | What do you want to do? ",
                             ["Add current song to playlist", "Search for track"], rofi_args=rofi_args)
    if index == 0:
        rofi_args = args.args or []
        rofi_args.append('-a')
        subprocess.run(["rofi-spotify", ', '.join(rofi_args)])
    if index == 1:
        rofi_args = args.args or []
        rofi_args.append('-st')
        subprocess.run(["rofi-spotify", ', '.join(rofi_args)])
    sys.exit(0)