# -*- coding: utf-8 -*- python3
"""
Created on Sun Jan 26 23:39:15 2020

@author: Antiochian
"""
import scraperconfig
import spotipy
import spotipy.util as util

CLIENT_ID, CLIENT_SECRET,REDIRECT, USER_NAME = scraperconfig.get_secret_info()
scope = 'user-library-read user-top-read'

global token
token = util.prompt_for_user_token(USER_NAME, scope,CLIENT_ID,CLIENT_SECRET,REDIRECT)
global spotify
spotify = spotipy.Spotify(auth=token)
global spotify_green
spotify_green = "#1DB954"