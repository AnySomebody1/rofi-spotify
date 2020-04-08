# rofi-spotify
##### A python program to interact with Spotify via rofi based on spotipy

<!--
## Documentation

Spotipy's full documentation is online at [Spotipy Documentation](http://spotipy.readthedocs.org/).

## Installation

```bash
pip install spotipy
```
-->

## Setup

To get started, create an app on https://developers.spotify.com/.
Then click on "Edit settings" and add a Redirect URI for your app. It does not need to be publicly accessible, so you can for instance specify "http://localhost/".
Hint: Click on "Add" after you entered it. If you just click on "Save" no changes are made.

Add your new ID, SECRET, Redirect URI and Spotify username to your environment like this:

```bash
export SPOTIPY_CLIENT_ID=client_id_here
export SPOTIPY_CLIENT_SECRET=client_secret_here
export SPOTIPY_REDIRECT_URI=redirect_uri_here
export ROFI_SPOTIFY_USERNAME=spotify_username
```

rofi_spotify will use this variables to connect to the Spotify web API.

## Reporting Issues

If you have suggestions, bugs or other issues specific to this software, file them [here](https://github.com/AnySomebody1/rofi-spotify/issues). Or just send me a pull request.