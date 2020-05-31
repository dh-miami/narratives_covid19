import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

"""
many thanks to Amanda Iglesias Moreno for this tutorial
link: https://towardsdatascience.com/bar-chart-race-with-plotly-f36f3a5df4f1
"""

def word_to_color(words, r_min=0, r_max=255, g_min=0, g_max=255, b_min=0, b_max=255):
    """Mapping of names to random rgb colors.
    Parameters:
    df (Series): Pandas Series containing names.
    r_min (int): Mininum intensity of the red channel (default 0).
    r_max (int): Maximum intensity of the red channel (default 255).
    g_min (int): Mininum intensity of the green channel (default 0).
    g_max (int): Maximum intensity of the green channel (default 255).
    b_min (int): Mininum intensity of the blue channel (default 0).
    b_max (int): Maximum intensity of the blue channel (default 255).
    Returns:
    dictionary: Mapping of names (keys) to random rgb colors (values)
    """
    mapping_colors = dict()

    for word in words.unique():
        red = random.randint(r_min, r_max)
        green = random.randint(g_min, g_max)
        blue = random.randint(b_min, b_max)
        rgb_string = 'rgb({}, {}, {})'.format(red, green, blue)

        mapping_colors[word] = rgb_string

    return mapping_colors


def frames_animation(df, title):
    """Creation of a sequence of frames.
    Parameters:
    df (DataFrame): Pandas data frame containing the categorical variable ['Name'],
    the count ['Number'], the year ['Year'], and the color['Color'] (separated columns).
    title (string): Title of each frame.
    Returns:
    list_of_frames (list): List of frames. Each frame contains a bar plot of a year.
    """
    list_of_frames = []
    start_date = df['date'].min()
    end_date = df['date'].max()
    diff = end_date - start_date + timedelta(days=1)

    for date in (start_date + timedelta(n) for n in range(diff.days)):
            fdata = df[df['date'] == date]
            list_of_frames.append(
                go.Frame(data=[go.Bar(x=fdata['variable'], y=fdata['value'],
                                            marker_color=fdata['color'],
                                            hoverinfo='none',
                                            textposition='outside', texttemplate='%{x}<br>%{y}',
                                            cliponaxis=False)],
                         layout=go.Layout(font={'size': 14},
                                plot_bgcolor='#FFFFFF',
                                xaxis={
                                        'showline': False, 'visible': False},
                                yaxis={
                                        'showline': False, 'visible': False},
                                bargap=0.15,
                                title=title + str(date))))
    return list_of_frames


def bar_race_plot(df, title, list_of_frames):
    """Creation of the bar chart race figure.
    Parameters:
    df (DataFrame): Pandas data frame containing the categorical variable ['Name'],
    the count ['Number'], the year ['Year'], and the color ['Color'] (separated columns).
    title (string): Title of the initial bar plot.
    list_of_frames (list): List of frames. Each frame contains a bar plot of a year.
    Returns:
    fig (figure instance): Bar chart race
    """

    # initial year - names (categorical variable), number of babies (numerical variable), and color
    initial_year = df['date'].min()
    initial_names = df[df['date'] == initial_year].variable
    initial_numbers = df[df['date'] == initial_year].value
    initial_color = df[df['date'] == initial_year].color
    range_max = df['value'].max()

    fig = go.Figure(
        data=[go.Bar(x=initial_names, y=initial_numbers,
                     marker_color=initial_color, hoverinfo='none',
                     textposition='outside', texttemplate='%{x}<br>%{y}',
                     cliponaxis=False)],
        layout=go.Layout(font={'size': 14}, plot_bgcolor='#FFFFFF',
                         xaxis={'showline': False, 'visible': False},
                         yaxis={'showline': False, 'visible': False,
                                'range': (0, range_max)},
                         bargap=0.15, title=title + str(initial_year),
                         updatemenus=[dict(type="buttons",
                                           buttons=[dict(label="Play",
                                                         method="animate",
                                                         args=[None, {"frame": {"duration": 2000, "redraw": True}, "fromcurrent": True}]),
                                                    dict(label="Stop",
                                                         method="animate",
                                                         args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}])])]),
        frames=list(list_of_frames))

    return fig

def get_bar_race_plot(df, title):
    df_melt = pd.melt(df, id_vars=['date'])
    mapping_colors_words = word_to_color(
        df_melt['variable'], 0, 185, 0, 185, 125, 255)
    df_melt['color'] = df_melt['variable'].map(mapping_colors_words)

    list_of_frames = frames_animation(df_melt, title)
    return bar_race_plot(df_melt, title, list_of_frames)
