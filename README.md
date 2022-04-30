# rofi-spotify
##### A python program to interact with Spotify via rofi based on spotipy

## Installation

### Python Package

You can install the [pypi](https://pypi.org/project/rofi-spotify/) package using `pip3 install rofi-spotify`. 

Make sure wherever it is installed to is on your path. You can check with `pip3 show rofi-spotify`.

### Arch Linux

Arch users can install the [rofi-spotify-git](https://aur.archlinux.org/packages/rofi-spotify-git/) package.

### Other

Clone this repo somewhere, then run:

```bash
pip3 install -r requirements.txt
```

You may wish to use the provided script, in which case it needs to be marked as executable:

```bash
chmod +x bin/rofi-spotify
```

## Setup

On first run the script should automatically tell you what to do in order to register your app on the Spotify developer 
page and create a configuration file.

## Usage

If installed using a package manager, a script should have automatically been put on your path:

```bash
rofi-spotify # Normal usage
rofi-spotify -h # See help
```

If not, you can either do:
```bash
python3 main.py
# or
bin/rofi-spotify
```

By default, the different possible options are shown.

| Short  | Long                | Description                                                                  | Default |
|--------|---------------------|------------------------------------------------------------------------------|---------|
| -h     | --help              | Shows CLI help and exits                                                     | -       |
| -a     | --add-to-playlist   | Add current track to a playlist                                              | -       |
| -st    | --search-track      | Search for a track                                                           | -       |
| -n     | --next              | Skip current track                                                           | -       |
| -p     | --toggle-pause-play | Pause/Resume playback                                                        | -       |
| -i     | --case-sensitive    | Enable case sensitivity                                                      | False   |
| -r ... | --args ...          | Command line arguments for rofi. Separate each argument with a space.        | -       |

## Reporting Issues

If you have suggestions, bugs or other issues specific to this software, file them [here](https://github.com/AnySomebody1/rofi-spotify/issues). Or just send me a pull request.
