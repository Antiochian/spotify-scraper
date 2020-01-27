# -*- coding: utf-8 -*- python3
"""
Created on Sun Jan 26 23:32:16 2020

@author: Antiochian
"""
from global_variables import *
import dateutil.parser as dp
import time
from datetime import datetime

#this info is contained inside a seperate config file called scraperconfig.py
#(this is not included here for security reasons)

def get_number_of_tracks():
    probe = spotify.current_user_saved_tracks(limit=1, offset=0)
    number_of_tracks = probe['total']
    return number_of_tracks

def convert_time(ISOtime):
    #converts spotifys ISO86001 time format to epoch milliseconds
    if type(ISOtime) == dict:
        ISOtime = ISOtime['added_at']
    parsed_t = dp.parse(ISOtime)
    #to get only day: parsed_t = dp.parse(ISOtime[0:10])
    seconds = parsed_t.timestamp()
    milliseconds = int(seconds*1000)
    return milliseconds

def get_top_from_freq_dict(freq_dict,limit=10):
    #get top "limit" most occuring values from freq_dictionary
    sorted_data = [(k,v) for k, v in sorted(freq_dict.items(), key=lambda item: item[1])]
    data = []
    labels = []
    for i in range(limit):
        data.append(sorted_data[-i][1])
        labels.append(sorted_data[-i][0])
    return data,labels

def count_frequency(input_list):
    #given a list with repeating values, create a freq dictionary
    freq_dict = {}
    for el in input_list:
        if el not in freq_dict:
            freq_dict[el] = 1
        else:
            freq_dict[el] += 1
    return freq_dict

def add_blank_days(data):
    #generate a list of all days between the start of dataset and now
    #(this is required to add in the days that DONT appear in dataset)
    date_list = []
    start_time = convert_time(data[-1])//1000
    end_time = int(time.time())
    deltaT = 86400 #seconds per day
    T_stamp = start_time-deltaT
    for i in range(((end_time-start_time)//deltaT) + 1):
    #T_stamp to ISO
        T_stamp += deltaT
        day = datetime.fromtimestamp(T_stamp).strftime("%d")
        month = datetime.fromtimestamp(T_stamp).strftime("%m")
        year = datetime.fromtimestamp(T_stamp).strftime("%Y")
        ISOtime = year+"-"+month+"-"+day
        date_list.append(ISOtime)
    return date_list

def search_for_artist(items,artist_ID):
    #search through item list and return matching playback events for given artist ID
    matches = []
    for el in items:
        date = convert_time(el['played_at'])
        track = el['track']
        name = track['name']
        artists = track['artists']
        #ID search in listed artists (in case there are more than 1)
        for ar in artists:
            if ar['id'] == artist_ID:
                matches.append([name,date])
        return matches
    
def get_track_IDs(items):
    #extract list of track IDs
    IDs = []
    if "id" in items[0].keys():
       for el in items:
           IDs.append(el['id'])     
    elif "track" in items[0].keys():
        for el in items:
            IDs.append(el['track']['id'])
    else:
        print("Error // Invalid item format for ID extraction")
    return IDs

def get_play_dates(items):
    #badly named - actually extracts the date ADDED, not the date played
    dates = []
    for el in items:
        dates.append(el['added_at'][0:10])
    return dates

def get_track_names(items):
    #extracts track names
    names = []
    for el in items:
        names.append(el['track']['name'])
    return names

def get_artist_names(items): #only accepts primary artist
    #extracts artist names
    artists = []
    for el in items:
        artists.append(el['track']['artists'][0]['name'])
    return artists

def get_library(total=10): #gets the last "total" saved tracks
    Searching = True
    index_offset = 0
    all_items = []
    total_batches = total // 50
    remainder = total % 50
    current_batch = 0
    #we have to do this in batches of 50, since spotify wont accept calls for more than that
    while Searching: #FULL 50-item batches
        if current_batch >= total_batches:
            Searching = False
        else:
            batch = spotify.current_user_saved_tracks(limit=50, offset=index_offset)
            all_items += batch['items']
            #print("batch number: ",current_batch)
            index_offset += 50
            current_batch += 1
    #final remainder:
    if remainder != 0:
        batch = spotify.current_user_saved_tracks(limit=remainder, offset=index_offset)
        all_items += batch['items']
    return all_items

def get_top(total=50): #same as get_library but just gets users top tracks instead
    Searching = True
    index_offset = 0
    all_items = []
    total_batches = total // 50
    remainder = total % 50
    current_batch = 0
    while Searching: #FULL 50-item batches
        if current_batch >= total_batches:
            Searching = False
        else:
            batch = spotify.current_user_top_tracks(limit=50, offset=index_offset)
            all_items += batch['items']
#            print("batch number: ",current_batch)
            index_offset += 50
            current_batch += 1
    #final remainder:
    if remainder != 0:
        batch = spotify.current_user_top_tracks(limit=remainder, offset=index_offset)
        all_items += batch['items']
    return all_items

def print_track_history(all_items):
    output = get_track_names(all_items)
    print(*output, sep = "\n")
    print("--\n",len(output)," items returned.")
    return

def print_artist_history(all_items):
    output = get_artist_names(all_items)
    print(*output, sep = "\n")
    print("--\n",len(output)," items returned.")
    return

def print_date_history(all_items,num=2790):
    output = get_play_dates(all_items)
    print(*output, sep = "\n")
    print("--\n",len(output)," items returned.")
    return

def get_track_metrics(IDs):
    #extracts audio analysis data
    total_batches = len(IDs) // 100
    remainder = len(IDs) % 100
    current_batch = 0
    Searching = True
    all_info = []
    while Searching:
        if current_batch >= total_batches:
            Searching = False
        else:
            current_ids = IDs[100*current_batch:100*current_batch+100]
            current_ids = ",".join(current_ids)
            current_ids = current_ids.translate({ord(c): None for c in '!@#$'})
            batch = spotify._get('https://api.spotify.com/v1/audio-features', Authorization=token, ids=current_ids)
            all_info += batch['audio_features']
#            print("batch number: ",current_batch)
            current_batch += 1
    #final remainder:
    if remainder != 0:
        current_ids = IDs[100*current_batch:]
        current_ids = ",".join(current_ids)
        current_ids = current_ids.translate({ord(c): None for c in '!@#$'})
        batch = spotify._get('https://api.spotify.com/v1/audio-features', Authorization=token, ids=current_ids)
        all_info += batch['audio_features']
    return all_info

def get_energy_X_valence(all_info,X="energy",Y="valence"):
    #badly named - can actually accept any given metric with X and Y parameters, not just energy/valence
    x = []
    y = []
    for el in all_info:
        if el != None:
            x.append(el[X])
            y.append(el[Y])
    return x, y
