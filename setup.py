from setuptools import setup

setup(
    name='rofi_spotify',
    version='0.0.2',
    install_requires=['python-rofi', 'spotipy', 'appdirs'],
    packages=['rofi_spotify'],
    url='https://github.com/AnySomebody1/rofi-spotify',
    license='GPLv3+',
    author='Any Somebody',
    author_email='anysomebody@gmx.de',
    description='A Rofi menu for interacting with Spotify.',
    scripts=['bin/rofi-spotify']
)
