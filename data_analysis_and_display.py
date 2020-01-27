# -*- coding: utf-8 -*- python3
"""
Created on Sun Jan 26 23:28:30 2020

@author: Antiochian

ANALYSIS/PLOTTING functions for spotify scraper
"""
from get_data import *
import matplotlib.pyplot as plt
import numpy as np

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
    data.append(len(all_items)-sum(data))
    data_labels.append("Other")
    plt.pie(data,labels=data_labels)
    plt.title("Saved Tracks Top Artist Breakdown")
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    ax.title.set_color('white')
    fig.set_size_inches(12, 8)
    plt.savefig('artist_pie.png', dpi = 500)
    return
    
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

def multiple_line_chart(all_items):
    fig, ax = plt.subplots()
    IDs = get_track_IDs(all_items)
    all_info = get_track_metrics(IDs)
    E,V = get_energy_X_valence(all_info,"energy","valence")
    D,T = get_energy_X_valence(all_info,"danceability","tempo")
    A,I = get_energy_X_valence(all_info,"acousticness","instrumentalness")
    all_dates = add_blank_days(all_items)
    x_dict = {}
    number_of_datapoints = len(all_items)
    number_of_dates = len(all_dates)
    for i in range(number_of_datapoints):
        item = all_items[i]
        date = item['added_at'][:10]
        
        if date in all_dates:
            x_pos = all_dates.index(date)
            if x_pos in x_dict.keys():
                x_dict[x_pos] += [ [ E[i], V[i], D[i], I[i] ] ]
            else:
                x_dict[x_pos] = [ [ E[i], V[i], D[i], I[i] ] ]
    x_labels = []
    x_label_locations = []
    x_values = []
    E_values = []
    V_values = []
    D_values = []
    I_values = []
    #xdict format is [Energy, Valence Danceability, Intrumentalness]
    number_of_labels = 5
    for key in x_dict.keys():
        x_values.append(key)
        E_total = 0
        V_total = 0
        D_total = 0
        I_total = 0        
        for subitem in x_dict[key]:
            E_total += subitem[0]
            V_total += subitem[1]
            D_total += subitem[2]
            I_total += subitem[3]
        E_values.append(E_total/len(x_dict[key]))
        V_values.append(V_total/len(x_dict[key]))
        D_values.append(D_total/len(x_dict[key]))
        I_values.append(I_total/len(x_dict[key]))
#        E_values.append(sum(x_dict[key][0])/len(x_dict[key][0]))
#        V_values.append(sum(x_dict[key][1])/len(x_dict[key][1]))
#        D_values.append(sum(x_dict[key][2])/len(x_dict[key][2]))
#        I_values.append(sum(x_dict[key][3])/len(x_dict[key][3]))
    
    i = 0
    for date in all_dates:
        if i % (number_of_dates//number_of_labels) == 0:
            x_labels.append(date)
            x_label_locations.append(i)
        i += 1
#    x_labels.append(all_dates[-1])
#    x_label_locations.append(number_of_dates) 
    #PLOT
    indiv_line_plot_and_trend(x_values, E_values, "g", "g", "Energy")
    indiv_line_plot_and_trend(x_values, V_values, "b", "b", "Mood")
    indiv_line_plot_and_trend(x_values, I_values, "w", "w","Instrumentalness")
    #indiv_line_plot_and_trend(x_values, D_values, "y", "y" , "Danceability")
    
    ax.set_xticks(x_label_locations)
    ax.set_xticklabels(x_labels)
    
    fig.patch.set_facecolor('black')
    ax.patch.set_facecolor('black')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white', which="both")
    ax.tick_params(axis='y', colors='white', which="both")
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    
    plt.xlabel('Date')
    plt.ylabel('Average Score (0-1)')
    plt.title("Metrics / Date")
    plt.legend(fancybox = False, framealpha = 1.0, facecolor=spotify_green, edgecolor="black")
    fig.set_size_inches(20, 8)
    return 

def indiv_line_plot_and_trend(x_values, y_values, col1, col2, linename):
    #PLOT ENERGY
    plt.plot(x_values, y_values, color=col1,alpha=0.2)
    trend = np.polyfit(x_values,y_values,12)
    p = np.poly1d(trend)
    plt.plot(x_values,p(x_values), color = col1, linestyle = "--", label=linename)
    return 