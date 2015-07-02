from pandas import *
from ggplot import *

def create_dataframe(filename):
    subway_data = pandas.read_csv(filename)
    #print subway_data.columns
    return subway_data

def plot_weather_data(turnstile_weather):
    '''
    You are passed in a dataframe called turnstile_weather. 
    Use turnstile_weather along with ggplot to make a data visualization
    focused on the MTA and weather data we used in assignment #3.  
    You should feel free to implement something that we discussed in class 
    (e.g., scatterplots, line plots, or histograms) or attempt to implement
    something more advanced if you'd like.  

    Here are some suggestions for things to investigate and illustrate:
     * Ridership by time of day or day of week
     * How ridership varies based on Subway station (UNIT)
     * Which stations have more exits or entries at different times of day
       (You can use UNIT as a proxy for subway station.)

    If you'd like to learn more about ggplot and its capabilities, take
    a look at the documentation at:
    https://pypi.python.org/pypi/ggplot/
     
    You can check out:
    https://www.dropbox.com/s/meyki2wl9xfa7yk/turnstile_data_master_with_weather.csv
     
    To see all the columns and data points included in the turnstile_weather 
    dataframe. 
     
    However, due to the limitation of our Amazon EC2 server, we are giving you a random
    subset, about 1/3 of the actual data in the turnstile_weather dataframe.
    '''
    #plot = ggplot(turnstile_weather, aes('ENTRIESn_hourly', 'meantempi')) + geom_point()
    total_entries_by_hour = turnstile_weather.groupby(['hour', 'rain'], as_index = False)['ENTRIESn_hourly'].mean()
    total_entries_by_day = turnstile_weather.groupby('day_week', as_index = False)['ENTRIESn_hourly'].mean()
    #total_entries_by_rain = turnstile_weather.groupby('rain', as_index = False)['ENTRIESn_hourly'].sum()
    #print total_entries_by_hour
    #print total_entries_by_day
    #print total_entries_by_rain
    plot_by_hour = ggplot(total_entries_by_hour, aes('hour', 'ENTRIESn_hourly', color = 'rain', fill = 'rain')) + geom_point() + geom_line() + \
     ggtitle('Ridership by time-of-day on rainy vs non-rainy days') + xlab('Hour') + ylab('Mean Entries') 
    plot_by_day = ggplot(total_entries_by_day, aes('day_week', 'ENTRIESn_hourly')) + geom_bar(stat = 'bar', fill = 'green', alpha = 0.8) + \
     ggtitle('Ridership by day-of-week') + xlab('Day') + ylab('Mean Entries')    
    print plot_by_hour
    print plot_by_day


if __name__ == "__main__":
    subway_dataframe = create_dataframe('turnstile_weather_v2.csv')
    plot_weather_data(subway_dataframe)
