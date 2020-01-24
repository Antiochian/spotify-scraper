
# -*- coding: utf-8 -*- python3
"""
Created on Mon Jan 13 01:30:12 2020

@author: Antiochian
<TODO>:
  1) currently max tracklimit is set to 2790 (the amount of tracks I have)
     i need to make an automatically set tracklimit based on user's library data
     
  2) add more stats
    
  3) add non-manual authentication (requires website host)
    
  4) reorder functions so they are less confusing
    
  5) add more comments
"""


import spotipy
import spotipy.util as util
import dateutil.parser as dp
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

import scraperconfig
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
    T_stamp = start_time
    for i in range((end_time-start_time)//deltaT):
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

#===============================================#
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

def get_average_metrics(all_info):
    #print average results
    n = len(all_info)
    IDs = get_track_IDs(all_info)
    all_info = get_track_metrics(IDs)
    E,V = get_energy_X_valence(all_info,"energy","valence")
    D,T = get_energy_X_valence(all_info,"danceability","tempo")
    A,I = get_energy_X_valence(all_info,"acousticness","instrumentalness")
    print("- - - - - - - - - - - - - - - - - - - ")
    print("Averages for user's top ",n," tracks:")
    print("- - - - - - - - - - - - - - - - - - - ")
    print("Energy = ", round(sum(E)/n,3))
    print("Valence (mood) = ", round(sum(V)/n,3))
    print("Danceability = ", round(sum(D)/n,3))
    print("Tempo = ", int(sum(T)/n), "bpm")
    print("Acousticness = ", round(sum(A)/n,3))
    print("Instrumentalness = ", round(sum(I)/n,3))
    return

def plot_mood_trends(all_items):
    IDs = get_track_IDs(all_items)
    all_info = get_track_metrics(IDs)
    E,V = get_energy_X_valence(all_info,"energy","valence")
    D,T = get_energy_X_valence(all_info,"danceability","tempo")
    A,I = get_energy_X_valence(all_info,"acousticness","instrumentalness")

    featured_dates = get_play_dates(all_items) #dates    
    featured_dates.reverse()
    all_days = add_blank_days(all_items)
    
    i = 0
    date_dict = {}
    for date in set(all_days):
        date_dict[date] = i
        i += 1
        
    x = []
    for date in set(featured_dates):
        if date in date_dict.keys():
            x.append(date_dict[date])
        else:
            print("date ",date," skipped")
            
    Ey = concatenate_metrics(E,featured_dates)
#    Vy = concatenate_metrics(V,featured_dates)
#    Dy = concatenate_metrics(D,featured_dates)
##    Ty = concatenate_metrics(T,featured_dates)
#    Ay = concatenate_metrics(A,featured_dates)
#    Iy = concatenate_metrics(I,featured_dates)

    plt.plot(x,Ey,marker='o')
#    plt.plot(x,Vy)
#    plt.plot(x,Dy)
#    plt.plot(x,Ay)
#    plt.plot(x,Iy)
#    legend((Ey,Vy,Dy,Ay,Iy),("Energy","Mood","Danceability","Acoustincess","Instrumentalness"))
    plt.show()
    return

def concatenate_metrics(metric,featured_dates):
    y = []
    running_average = []
    prev_date = featured_dates[0]
    for i in range(len(featured_dates)):
        date = featured_dates[i]
        if date == prev_date:
            running_average.append(metric[i])                        
        else:
            average = sum(running_average)/len(running_average)
            y.append(average)
            prev_date = date
            running_average = []
            running_average.append(metric[i])
    return y

def plot_scatter(all_items,X="energy",Y="valence"):
    #plot valence vs energy
    IDs = get_track_IDs(all_items)
    all_info = get_track_metrics(IDs)
    E,V = get_energy_X_valence(all_info,X,Y)
    fig, ax = plt.subplots()
    plt.scatter(E,V,s = (plt.rcParams['lines.markersize'] ** 2)/4, c = spotify_green)
    #set up colours
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.tick_params(axis='x', colors='white', which="both")
    ax.tick_params(axis='y', colors='white', which="both")
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    #set labels
    plt.xlabel(X)
    plt.ylabel(Y)
    plt.title(X+" vs "+Y+" scatterplot")
    fig.set_size_inches(5, 5)
    return
    
    
def plot_artist_pi(all_items):
    fig, ax = plt.subplots()
    output = get_artist_names(all_items)
    data, data_labels = get_top_from_freq_dict(count_frequency(output),30)
    data.append(num-sum(data))
    data_labels.append("Other")
    plt.pie(data,labels=data_labels)
    plt.title("Saved Tracks Top Artist Breakdown")
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    ax.title.set_color('white')
    fig.set_size_inches(12, 8)
    plt.savefig('artist_pie.png', dpi = 500)
    return

def get_labels(all_dates, bar_width, number_of_labels=5):
    number_of_labels += 1 #correction
    number_of_dates = len(all_dates)
    total_width = number_of_dates*bar_width
    label_locations = [x for x in range(0,total_width, (total_width//number_of_labels)+1)] + [total_width]
    
    labels = [all_dates[index] for index in range(0,number_of_dates,number_of_dates//number_of_labels)] + [all_dates[number_of_dates-1]]
    return labels, label_locations
    
def plot_bar_chart(all_items,period=1): #period = days per bar (1 = daily, 7 = weekly, etc)
    raw_data = get_play_dates(all_items)
    freq_dict = count_frequency(raw_data)
    bar_width = 10 #must be integer for range reasons down the line
    bin_width = period*bar_width
    all_dates = add_blank_days(raw_data)
    #get label locations
    number_of_bins = len(all_dates)//period + 1
    data = []
    buffer = []
    for date in all_dates:
        if date in freq_dict.keys():
            buffer.append(freq_dict[date])
        else:
            buffer.append(0)
        if len(buffer) == period:
            data.append(sum(buffer))
            buffer = []
    if buffer != []: #clean remainder into final bin
        data.append(sum(buffer))
            
        #add labels
    fig, ax = plt.subplots()
    #get bar locations:
    x = [i for i in range(0,bin_width*number_of_bins,bin_width)]
    #if the period doesnt subdivide the time period, fix mismatch by cleaning up x
    if len(x) - len(data) == 1:
        x.remove(x[-1])
     
    #ACTUAL PLOT
    plt.bar(x,data,width=bin_width,align = "edge", color=spotify_green)
    
    #set labels, colours
    labels, label_locations = get_labels(all_dates, bar_width,3)
    ax.set_xticks(label_locations)
    ax.set_xticklabels(labels)
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white', which="both")
    ax.tick_params(axis='y', colors='white', which="both")
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    #set title
    if period == 1:
        period_string = "day"
    elif period == 7:
        period_string = "month"
    elif period == 30 or period == 31:
        period_string = "month"
    else:
        period_string = str(period)+" days"     
    plt.xlabel('Date')
    plt.ylabel('No. of new tracks per '+period_string)
    plt.title("Track Discovery / "+period_string)
    fig.set_size_inches(20, 8)
#    plt.savefig('bar_chart.png', dpi = 100)
#    plt.show()
    return

def plot_all_scatters(all_items):
    #<TODO> 4-way subplot figure
    return

def basic_UI(): #simple CLI program flow
    CLIENT_ID, CLIENT_SECRET,REDIRECT,USER_NAME = scraperconfig.get_secret_info()
    scope = 'user-library-read user-top-read'
    
    USER_NAME = "mrsnail4"
    #get auth token, make client object called "spotify"
    global token
    token = util.prompt_for_user_token(USER_NAME, scope,CLIENT_ID,CLIENT_SECRET,REDIRECT)
    global spotify
    spotify = spotipy.Spotify(auth=token)
    global spotify_green
    spotify_green = "#1DB954"
    current_num = None
    max_num = get_number_of_tracks()
    print("Spotify Scraper - by Henry")
    print("--------------------------")
    while True:
        print("Current User: ",USER_NAME)
        print("\t 1. Newly Saved Tracks/Day")
        print("\t 2. Plot Scatterplot of top tracks' Energy/Valence")
        print("\t 3. Output average metric data")
        print("\t 4. Quit")
        user_input = int(input("\t>:"))
        if user_input == 1:
            num = choose_num()
            if num == "maximum":
                num = max_num
            if num != current_num:
                print("\tGetting data, please be patient...")
            all_items = get_library(num)
            current_num = num
            print("\tData collected. Plotting...")
            plot_bar_chart(all_items)
            plt.show()
        elif user_input == 2:
            num = choose_num()
            if num == "maximum":
                num = max_num
            if num != current_num:
                print("\tGetting data, please be patient...")
                all_items = get_library(num)
                current_num = num
            print("\tData collected. Plotting...")
            plot_scatter(all_items)
            plt.show()
        elif user_input == 3:
            num = choose_num()
            if num == "maximum":
                num = max_num
            if num != current_num:
                print("\tGetting data, please be patient...")
                all_items = get_library(num)
                current_num = num
            get_average_metrics(all_items)
        elif user_input == 4:
            print("Program exited.")
            return
        input("press any key to continue\t")
            
def choose_num():
    print("Choose settings:")
    print("\t1. default\n\t2. custom\ ")
    user_input = int(input())
    if user_input == 1:
        num = "maximum"
    return num

def simple_test():
    all_items = get_library(2790)
    t0 = time.time()
    plot_bar_chart(all_items)
    print("time_taken:  ",round(time.time()-t0,5)," seconds")
    return

basic_UI()
#all_items = get_library(300)
#plot_mood_trends(all_items)
