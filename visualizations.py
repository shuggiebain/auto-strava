import os
import sys
from get_data import concatenate_data
import pandas as pd
import math
import seaborn as sns
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 6
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def conversions(dataframe):
    """
    :param dataframe: Dataframe with activities represented as rows
    :return: Converted values for columns -
    average_speed from metres/second to km/hr
    distance from metres to kilometres
    elapsed_time from seconds to minutes
    moving_time from seconds to minutes

    """

    dataframe = dataframe.fillna(0)
    dataframe['average_speed'] = dataframe['average_speed'] * 16.666667
    dataframe['distance'] = dataframe['distance'] * 0.001
    dataframe['elapsed_time'] = dataframe['elapsed_time'] * 0.0166667
    dataframe['moving_time'] = dataframe['moving_time'] * 0.0166667
    return dataframe


def get_intervals(d):
    if d < 3:
        return 'Under 3'
    elif d >= 3 and d <= 5:
        return '3 to 5'
    elif d > 5 and d <= 7:
        return '5 to 7'
    elif d > 7 and d <= 10:
        return '7 to 10'
    elif d > 10 and d <= 13:
        return '10 to 13'
    elif d > 13 and d <= 17:
        return '13 to 17'
    elif d > 17:
        return 'Over 17'


def clean_df(dataframe):
    dataframe = dataframe[dataframe['distance'] != 0]
    dataframe = dataframe[dataframe.columns[~dataframe.columns.str.contains('Unnamed:')]]
    dataframe = dataframe.drop(['gear_id', 'utc_offset'], axis=1)
    dataframe['speed-seconds'] = (dataframe['elapsed_time'] / dataframe['distance']) * 60
    dataframe['speed_km/min'] = dataframe['speed-seconds'].apply(lambda x : convert(x))
    return dataframe


def monthly_mileage_viz(distance_df):

    distance = distance_df[['speed_km/min', 'distance', 'start_date', 'moving_time']]
    distance['date'] = pd.to_datetime(distance['start_date'])
    distance = distance.drop(['start_date'], axis=1)
    dist = distance[['date', 'distance']]
    dist['year'] = pd.DatetimeIndex(dist['date']).year
    dist['month'] = pd.DatetimeIndex(dist['date']).month

    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(12, 6))

    fig = sns.barplot(x='year', y='distance', data=dist, estimator=sum,
                      ci=None, ax=ax, hue='month', palette='rocket_r')

    plt.legend(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

    ax.set(xlabel='Year', ylabel='Distance KM', title='MoM Mileage')

    for p in ax.patches:
        height = p.get_height()

        if math.isnan(height):
            pass
        else:
            ax.annotate(str(int(round(p.get_height()))), (p.get_x() * 1.005, p.get_height() * 1.005))

    if not os.path.exists('./visualizations'):
        os.makedirs('./visualizations')

    plt.savefig('./visualizations/monthly_mileage.jpg')


def speed_dist_intervals(speed_df):

    speed_df = speed_df[['average_speed', 'distance', 'speed-seconds', 'speed_km/min']]
    speed_df['intervals'] = speed_df['distance'].apply(lambda x: get_intervals(x))

    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(12, 6))

    fig = sns.boxplot(x='intervals', y='speed-seconds', data=speed_df,
                      palette='rocket_r', showfliers=False,
                      order=['Under 3', '3 to 5', '5 to 7', '7 to 10', '10 to 13', '13 to 17', 'Over 17'])

    ax.set(xlabel='Intervals KM', ylabel='Seconds/KM', title='Speed Variation Over Distance Intervals')

    if not os.path.exists('./visualizations'):
        os.makedirs('./visualizations')

    plt.savefig('./visualizations/speed_over_distance.jpg')


def time_dist_intervals(time_df):

    time_df = time_df[['average_speed', 'distance', 'speed-seconds', 'moving_time']]
    time_df['intervals'] = time_df['distance'].apply(lambda x: get_intervals(x))

    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(12, 6))

    fig = sns.boxplot(x='intervals', y='moving_time', data=time_df,
                      palette='rocket_r', showfliers=False,
                      order=['Under 3', '3 to 5', '5 to 7', '7 to 10'
                          , '10 to 13', '13 to 17', 'Over 17'])

    ax.set(xlabel='Intervals KM', ylabel='Duration', title='Duration Over Distance Intervals')

    if not os.path.exists('./visualizations'):
        os.makedirs('./visualizations')

    plt.savefig('./visualizations/time_over_distance.jpg')


def run_breakdown(run_df):

    run_df = run_df[['average_speed', 'distance', 'speed-seconds', 'moving_time']]
    run_df['intervals'] = run_df['distance'].apply(lambda x: get_intervals(x))

    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(12, 6))

    fig = sns.countplot(x='intervals', data=run_df, palette='rocket_r',
                        order=['Under 3', '3 to 5', '5 to 7', '7 to 10', '10 to 13', '13 to 17', 'Over 17'])

    ax.set(xlabel='Intervals KM', ylabel='No. of Runs', title='No. of Runs over Distance')

    for p in ax.patches:
        height = p.get_height()
        if math.isnan(height):
            pass
        else:
            ax.annotate(str(int(round(p.get_height()))), (p.get_x() * 1.005, p.get_height() * 1.005))

    if not os.path.exists('./visualizations'):
        os.makedirs('./visualizations')

    plt.savefig('./visualizations/runs_breakdown.jpg')



'''
main
'''


df = concatenate_data(folder_path=os.path.join(sys.path[0], 'data'))
converted_df = conversions(df)
cleaned = clean_df(converted_df)

monthly_mileage_viz(cleaned)
speed_dist_intervals(cleaned)
time_dist_intervals(cleaned)
run_breakdown(cleaned)
