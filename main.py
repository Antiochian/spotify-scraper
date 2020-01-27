# -*- coding: utf-8 -*- python3
"""
Created on Sun Jan 26 23:30:59 2020

@author: Antiochian
"""


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
import matplotlib.pyplot as plt
import fileinput

from data_analysis_and_display import *
from get_data import *
from csv_exporter import *
import scraperconfig
#this info is contained inside a seperate config file called scraperconfig.py
#(this is not included here for security reasons)


def basic_UI():
    current_num = None
    max_num = get_number_of_tracks()
    print("Spotify Scraper - by Henry")
    print("--------------------------")
    while True:
        print("Current User: ",USER_NAME)
        print("\t 1. Newly Saved Tracks/Day")
        print("\t 2. Plot Scatterplot of tracks' Energy/Valence")
        print("\t 3. Plot Lineplot of Average Metrics / Time")
        print("\t 4. Output average metric data")
        print("\t 5. Backup library to CSV")
        print("\t 6. Quit")
        user_input = int(input("\t>:"))
        if user_input == 1:
            num = max_num
            all_items = get_library(num)
            current_num = num
            print("\tData collected. Plotting...")
            plot_bar_chart(all_items)
            plt.show()
        elif user_input == 2:
            num = choose_num()
            if num == "maximum":
                num = max_num
                print("\tGetting data, please be patient...")
                all_items = get_library(num)
                current_num = num
            elif num == "top 50":
                print("\tGetting data, please be patient...")
                all_items = get_top(50)
                current_num = num
            print("\tData collected. Plotting...")
            plot_scatter(all_items)
            plt.show()
        elif user_input == 3:
            print("\tGetting data, please be patient...")  
            all_items = get_library(max_num)
            print("\tData collected. Plotting...")
            multiple_line_chart(all_items)
            plt.show()
        elif user_input == 4:
            num = choose_num()
            if num == "maximum":
                num = max_num
                all_items = get_library(max_num)
            if num == "top 50":
                print("\tGetting data, please be patient...")
                all_items = get_top(50)
                current_num = num
            get_average_metrics(all_items)
        elif user_input == 5:
            print("\tGetting data, please be patient...")            
            export_backup(USER_NAME)
            print("\tBackup completed (/output_"+USER_NAME+".csv)")   
        elif user_input == 6:
            print("Program exited.")
            return
        cont = input("\tPress any key to continue or Q to quit ")
        if cont == "Q" or cont == "q":
            return
    return
            
def choose_num():
    print("Choose settings:")
    print("\t1. all tracks\n\t2. top 50\ ")
    user_input = int(input())
    if user_input == 1:
        num = "maximum"
    else:
        num = "top 50"
    return num



def manual_setup():
    #for debug purposes
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
    return

if __name__ == "__main__":
    basic_UI()