# TODO Catch errors
# TODO Try catch errors

import argparse
import configparser
import os
import subprocess
import sys
import textwrap
import time

import appdirs
import spotipy
# import spotipy.util as util
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
        print(textwrap.wrap("Enter arbitrary name and description and select appropriate options in the next steps.",
                            width=70))
        print(textwrap.wrap("Click on \"Edit Settings\" and add an arbitrary Redirect URI, for instance "
                            "http://localhost:8080 by entering"
                            " it, clicking on \"Add\" and finally on \"Save Settings\" below.", width=70))

        config = configparser.ConfigParser()
        config['spotipy'] = {}
        config['spotipy']['client_id'] = str(input("Please enter the Client ID you received after the previous step: "))
        config['spotipy']['client_secret'] = str(input("Please enter the Client Secret you received after the previous "
                                                       "step: "))
        config['spotipy']['redirect_uri'] = str(input("Please enter the Redirect URI you added: "))

        config['spotify'] = {}
        config['spotify']['spotify_username'] = str(input("Please enter your Spotify username. "))

        config['settings'] = {}
        config['settings']['show_playback_popups'] = 'false'
        config['settings']['show_add_to_playlist_popups'] = 'true'
        config['settings']['track_search_max_entries'] = '5'

        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    return config, config_dir


def getPlaylists(sp, onlyEditable, username):
    playlists_tmp = sp.current_user_playlists(limit=50)
    playlists = playlists_tmp
    offset = 50
    while offset < playlists['total']:
        playlists_tmp = sp.current_user_playlists(limit=50, offset=offset)
        offset += 50
        playlists['items'].extend(playlists_tmp['items'])
    if onlyEditable:
        playlists['items'] = [playlist for playlist in playlists['items']
                              if (playlist['owner']['display_name'] == username or playlist['collaborative'])]
    return playlists


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
    except Exception("Nothing playing"):
        track_id = None
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
    while offset < playlist_tracks_tmp['total']:
        playlist_tracks_tmp = sp.playlist_tracks(playlist_id, fields="total,items(track(id))", offset=offset,
                                                 additional_types=('track',))
        offset += 100
        playlist_tracks['items'].extend(playlist_tracks_tmp['items'])
    playlist_ids = [d['track']['id'] for d in playlist_tracks['items']]
    if track_id in playlist_ids:
        index, key = rofi.select(track_name + " is already in " + playlist_name +
                                 ". Add anyway? ", ["No", "Yes"], rofi_args=rofi_args)
        if index == -1:
            sys.exit(0)
        if index == 0:
            sys.exit()
    return sp.user_playlist_add_tracks(username, playlist_id, {track_id}) 


def run():
    config, config_dir = load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add-to-playlist", action="store_true", help="Add current track to a playlist")
    parser.add_argument("-l", "--like-track", action="store_true", help="Like current track")
    parser.add_argument("-st", "--search-track", action="store_true", help="Search for a track")
    parser.add_argument('-i', '--case-sensitive', action='store_true', help='Enable case sensitivity')
    parser.add_argument('-r', '--args', nargs=argparse.REMAINDER, help='Command line arguments for rofi. '
                                                                       'Separate each argument with a space.')
    args = parser.parse_args()

    rofi_args = args.args or []
    if not args.case_sensitive:
        rofi_args.append('-i')
    rofi = Rofi()

    scope = "user-library-read user-read-currently-playing user-read-playback-state user-library-modify " \
            "user-modify-playback-state playlist-modify-private playlist-read-private playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(client_id=config['spotipy']['client_id'],
                                                                  client_secret=config['spotipy']['client_secret'],
                                                                  redirect_uri=config['spotipy']['redirect_uri'],
                                                                  scope=scope, cache_path=(config_dir + "/token")))

    if args.add_to_playlist:
        track_id, track_meta = getCurrentTrack(sp)
        playlists = getPlaylists(sp, onlyEditable=True, username=config['spotify']['spotify_username'])
        playlists_names = [d['name'] for d in playlists['items']]
        index, key = rofi.select("To which playlist do you want to add " + track_meta + "? ",
                                 playlists_names, rofi_args=rofi_args)
        if key == -1:
            sys.exit(0)
        target_playlist_id = playlists['items'][index]['id']
        result = addTrackToPlaylist(rofi, rofi_args, sp, config['spotify']['spotify_username'], target_playlist_id,
                           playlists_names[index], track_id, track_meta)
        if not result == 0:
            if config['settings'].getboolean('show_add_to_playlist_popups'):
                rofi.status(track_meta + " added to " + playlists_names[index] + ".", rofi_args=rofi_args)
                time.sleep(2)
        rofi.close()
        sys.exit(0)

    if args.like_current:
        track_id, track_meta = getCurrentTrack(sp)
        sp.current_user_saved_tracks_add({track_id})
        rofi.status(track_meta + " liked.", rofi_args=rofi_args)
        time.sleep(2)
        rofi.close()


    if args.search_track:
        trackquery = rofi.text_entry('Search for a track: ', rofi_args=rofi_args)
        results = sp.search(trackquery, limit=config['settings']['track_search_max_entries'], type="track")
        if not results['tracks']['items']:
            rofi.status("No tracks found.", rofi_args=rofi_args)
            time.sleep(2)
            rofi.close()
        else:
            tracks = []
            for index, track in enumerate(results['tracks']['items']):
                tracks.append({'id': track['id'], 'artists': getArtistsTitleForID(sp, track['id'])[0],
                               'title': track['name'], 'uri': track['uri']})
            rofi_tracks = [d['artists'] + " - " + d['title'] for d in tracks]
            index_track, key_track = rofi.select("Select a track: ", rofi_tracks, rofi_args=rofi_args)
            if key_track == -1:
                sys.exit(0)
            index_todo, key_todo = rofi.select(rofi_tracks[index_track] + ": ",
                                               ["Add to queue", "Add to playlist", "Play"], rofi_args=rofi_args)
            if key_todo == -1:
                sys.exit(0)

            if index_todo == 0:
                sp.add_to_queue(tracks[index_track]['id'])
                if config['settings'].getboolean('show_playback_popups'):
                    rofi.status(rofi_tracks[index_track] + " added to queue.", rofi_args=rofi_args)
                    time.sleep(2)
                rofi.close()

            if index_todo == 1:
                playlists = getPlaylists(sp, onlyEditable=True, username=config['spotify']['spotify_username'])
                playlists_names = [d['name'] for d in playlists['items']]
                index_playlist, key_playlist = rofi.select("To which playlist do you want to add "
                                                           + rofi_tracks[index_track] + "? ", playlists_names,
                                                           rofi_args=rofi_args)
                if key_playlist == -1:
                    sys.exit(0)
                target_playlist_id = playlists['items'][index_playlist]['id']
                result = addTrackToPlaylist(rofi, rofi_args, sp, config['spotify']['spotify_username'],
                                            target_playlist_id, playlists_names[index_playlist],
                                            tracks[index_track]['id'], rofi_tracks[index_track])
                if not result == 0:
                    if config['settings'].getboolean('show_add_to_playlist_popups'):
                        rofi.status(rofi_tracks[index_track] + " added to " + playlists_names[index_playlist] + ".",
                                rofi_args=rofi_args)
                        time.sleep(2)
                    rofi.close()

            if index_todo == 2:
                sp.start_playback(uris=[tracks[index_track]['uri']])
                if config['settings'].getboolean('show_playback_popups'):
                    rofi.status("Playing " + rofi_tracks[index_track] + ".", rofi_args=rofi_args)
                    time.sleep(2)
                rofi.close()

        sys.exit(0)

    curr_track_id, curr_track_meta = getCurrentTrack(sp)
    index, key = rofi.select("Currently playing: " + curr_track_meta + " ",
                             ["Add current song to playlist", "Like current song", "Search track"], rofi_args=rofi_args)
    if index == 0:
        rofi_args = args.args or []
        rofi_args.append('-a')
        subprocess.run(["rofi-spotify", ', '.join(rofi_args)])
    if index == 1:
        rofi_args = args.arg or []
        rofi_args.append('-l')
        subprocess.run(["rofi-spotify", ', '.join(rofi_args)])
    if index == 2:
        rofi_args = args.args or []
        rofi_args.append('-st')
        subprocess.run(["rofi-spotify", ', '.join(rofi_args)])
    sys.exit(0)


run()
