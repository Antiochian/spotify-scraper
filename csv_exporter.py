# -*- coding: utf-8 -*- python3
"""
Created on Sun Jan 26 23:31:37 2020

@author: Antiochian
"""
import csv
from get_data import *

def make_backup(all_items):
    info_array = [["Track Name","Album","Artist","Release Date","Popularity","Date Added"]]
    for item in all_items:
        track_name = item['track']['name']
        album_name = item['track']['album']['name']
        artist_name = item['track']['artists'][0]['name']
        album_date = item['track']['album']['release_date']
        popularity = item['track']['popularity']
        added_on = item['added_at']
        row = [track_name,album_name,artist_name,album_date,popularity,added_on]
        info_array.append(row)
    return info_array


def export_backup(USER_NAME="default"):
    num = get_number_of_tracks()
    all_items = get_library(num)
    info_array = make_backup(all_items)
    with open("output_"+USER_NAME+".csv", "w", newline = "",encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(info_array)
    return
