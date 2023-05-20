import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt


class Analytics:
    def __init__(self, data):
        self.data = data

        self.data.drop(
            ['username', 'platform', 'conn_country', 'ip_addr_decrypted', 'user_agent_decrypted', 'shuffle', 'skipped',
             'offline', 'offline_timestamp', 'incognito_mode', 'episode_name', 'episode_show_name',
             'spotify_episode_uri'], axis=1, inplace=True)
        na_ind = list(self.data[self.data['master_metadata_track_name'].isna()].index)
        self.data.drop(na_ind, inplace=True)
        self.data['ts'] = pd.to_datetime(self.data['ts'], infer_datetime_format=True)
        self.data.sort_values(by=['ts'], inplace=True)
        self.data.index = range(0, self.data.shape[0])
        self.data['date'] = [d.date() for d in self.data['ts']]
        self.data['time'] = [d.time() for d in self.data['ts']]
        self.data['day_of_week'] = [d.day_name() for d in self.data['ts']]
        self.data['year'] = [d.year for d in self.data['ts']]

        self.yearly_data = list()
        self.years = self.data['year'].unique()
        for i in range(0, len(self.years)):
            temp = self.data[self.data['year'] == self.years[i]]
            self.yearly_data.append(temp)

        self.tot_artist_overall = self.data['master_metadata_album_artist_name'].unique()
        self.tot_songs_overall = self.data['master_metadata_track_name'].unique()
        self.tot_albums_overall = self.data['master_metadata_album_album_name'].unique()
        self.dates_unique = self.data['date'].unique()

        self.morn = [dt.time(6, 0, 0), dt.time(11, 59, 59)]
        self.afnoon = [dt.time(12, 0, 0), dt.time(17, 59, 59)]
        self.eve = [dt.time(18, 0, 0), dt.time(23, 59, 59)]
        self.night = [dt.time(0, 0, 0), dt.time(5, 59, 59)]
        self.time_of_day = [self.morn, self.afnoon, self.eve, self.night]
        self.td = ['Morning', 'Afternoon', 'Evening', 'Night']

    def listening_time(self):
        tot_listening_time = 'Total listening time from ' + str(self.data['date'].min()) + ' to ' + \
                             str(self.data['date'].max()) + ' in minutes is ' + \
                             str(round(self.data['ms_played'].sum() / 60000, 2))

        listenting_time_yearly = list()
        for i in range(0, len(self.yearly_data)):
            listenting_time_yearly.append(self.yearly_data[i]['ms_played'].sum())
        df_listening_time_yearly = pd.DataFrame(list(zip(self.years, listenting_time_yearly)),
                                                columns=['Year', 'Total_listening_time_in_ms'])

        return tot_listening_time, df_listening_time_yearly

    def songs_listened(self):
        tot_songs_listened = 'Total number of songs listened is ' + str(len(self.tot_songs_overall))

        songs_yearly = list()
        for i in range(0, len(self.yearly_data)):
            songs_yearly.append(self.yearly_data[i]['master_metadata_track_name'].unique().shape[0])
        df_songs_yearly = pd.DataFrame(list(zip(self.years, songs_yearly)), columns=['Year', 'Total_songs_listened'])

        new_songs_yearly = list()
        new_songs_yearly_count = list()
        for i in range(0, len(self.yearly_data)):
            temp = self.yearly_data[i]['master_metadata_track_name'].unique()
            new_songs_yearly_count.append(np.setdiff1d(temp, new_songs_yearly).shape[0])
            new_songs_yearly.extend(temp)
        df_new_songs_yearly = pd.DataFrame(list(zip(self.years, new_songs_yearly_count)),
                                           columns=['Year', 'New_songs_discovered'])

        return tot_songs_listened, df_songs_yearly, df_new_songs_yearly

    def artists_listened(self):
        tot_artists_listened = 'Total number of artists listened to is ' + str(len(self.tot_artist_overall))

        artists_yearly = list()
        for i in range(0, len(self.yearly_data)):
            artists_yearly.append(self.yearly_data[i]['master_metadata_album_artist_name'].unique().shape[0])
        df_artists_yearly = pd.DataFrame(list(zip(self.years, artists_yearly)),
                                         columns=['Year', 'Total_artists_listened_to'])

        new_artists_yearly = list()
        new_artists_yearly_count = list()
        for i in range(0, len(self.yearly_data)):
            temp = self.yearly_data[i]['master_metadata_album_artist_name'].unique()
            new_artists_yearly_count.append(np.setdiff1d(temp, new_artists_yearly).shape[0])
            new_artists_yearly.extend(temp)
        df_new_artist_yearly = pd.DataFrame(list(zip(self.years, new_artists_yearly_count)),
                                            columns=['Year', 'New_artists_discovered'])

        return tot_artists_listened, df_artists_yearly, df_new_artist_yearly

    def favorite_artist(self):
        artist_listentime_overall = list()
        artist_totsongs_overall = list()
        artist_songsplayed_overall = list()

        for i in range(0, len(self.tot_artist_overall)):
            temp = self.data[self.data['master_metadata_album_artist_name'] == self.tot_artist_overall[i]]
            artist_listentime_overall.append(temp['ms_played'].sum())
            artist_totsongs_overall.append(temp['master_metadata_track_name'].unique().shape[0])
            artist_songsplayed_overall.append(temp.shape[0])

        df = pd.DataFrame(list(
            zip(self.tot_artist_overall, artist_listentime_overall, artist_totsongs_overall, artist_songsplayed_overall)),
                          columns=['Artist', 'Total_listening_time_in_ms', 'Total_no_of_songs_listened',
                                   'No_of_times_played'])

        df['fav_artist_score'] = 1.5 * ((df['Total_listening_time_in_ms'] - df['Total_listening_time_in_ms'].min()) / (
                    df['Total_listening_time_in_ms'].max() - df['Total_listening_time_in_ms'].min())) + \
                    1.2 * ((df['Total_no_of_songs_listened'] - df['Total_no_of_songs_listened'].min()) /
                           (df['Total_no_of_songs_listened'].max() - df['Total_no_of_songs_listened'].min())) + \
                            0.8 * ((df['No_of_times_played'] - df['No_of_times_played'].min()) /
                                   (df['No_of_times_played'].max() - df['No_of_times_played'].min()))

        df = df.sort_values(by=['fav_artist_score'], ascending=False).iloc[:50]
        df.index = range(0, 50)

        return df, df.iloc[:10]

    def favorite_artist_yearly(self):
        yearly_fav_artists = list()
        for i in range(0, len(self.years)):
            artist_listentime_overall = list()
            artist_totsongs_overall = list()
            artist_songsplayed_overall = list()
            yearly_artists = self.data[self.data['year'] == self.years[i]]['master_metadata_album_artist_name'].unique()
            for j in range(0, len(yearly_artists)):
                temp = self.yearly_data[i][self.yearly_data[i]['master_metadata_album_artist_name'] == yearly_artists[j]]
                artist_listentime_overall.append(temp['ms_played'].sum())
                artist_totsongs_overall.append(temp['master_metadata_track_name'].unique().shape[0])
                artist_songsplayed_overall.append(temp.shape[0])

            df = pd.DataFrame(list(
                zip(yearly_artists, artist_listentime_overall, artist_totsongs_overall,
                    artist_songsplayed_overall)),
                columns=['Artist', 'Total_listening_time_in_ms', 'Total_no_of_songs_listened',
                         'No_of_times_played'])

            df['fav_artist_score'] = 1.5 * (
                        (df['Total_listening_time_in_ms'] - df['Total_listening_time_in_ms'].min()) / (
                        df['Total_listening_time_in_ms'].max() - df['Total_listening_time_in_ms'].min())) + \
                                     1.2 * ((df['Total_no_of_songs_listened'] - df[
                'Total_no_of_songs_listened'].min()) /
                                            (df['Total_no_of_songs_listened'].max() - df[
                                                'Total_no_of_songs_listened'].min())) + \
                                     0.8 * ((df['No_of_times_played'] - df['No_of_times_played'].min()) /
                                            (df['No_of_times_played'].max() - df['No_of_times_played'].min()))

            df = df.sort_values(by=['fav_artist_score'], ascending=False).iloc[:10]
            df.index = range(0, 10)
            yearly_fav_artists.append(df)

        return yearly_fav_artists, self.years

    def favorite_song(self):
        songs_listentime_overall = list()
        songs_timesplayed_overall = list()

        for i in range(0, len(self.tot_songs_overall)):
            temp = self.data[self.data['master_metadata_track_name'] == self.tot_songs_overall[i]]
            songs_listentime_overall.append(temp['ms_played'].sum())
            songs_timesplayed_overall.append(temp.shape[0])

        df = pd.DataFrame(list(zip(self.tot_songs_overall, songs_listentime_overall, songs_timesplayed_overall)),
                          columns=['Song', 'Total_listening_time_in_ms', 'No_of_times_played'])

        df['fav_song_score'] = 1.5 * ((df['Total_listening_time_in_ms'] - df['Total_listening_time_in_ms'].min()) / (
                    df['Total_listening_time_in_ms'].max() - df['Total_listening_time_in_ms'].min())) + 1 * (
                                           (df['No_of_times_played'] - df['No_of_times_played'].min()) / (
                                               df['No_of_times_played'].max() - df['No_of_times_played'].min()))

        df = df.sort_values(by=['fav_song_score'], ascending=False).iloc[:50]
        df.index = range(0, 50)

        return df, df.iloc[:10]

    def favorite_song_yearly(self):
        yearly_fav_songs = list()
        for i in range(0, len(self.years)):
            songs_listentime_overall = list()
            songs_timesplayed_overall = list()
            yearly_songs = self.data[self.data['year'] == self.years[i]]['master_metadata_track_name'].unique()
            for j in range(0, len(yearly_songs)):
                temp = self.yearly_data[i][
                    self.yearly_data[i]['master_metadata_track_name'] == yearly_songs[j]]
                songs_listentime_overall.append(temp['ms_played'].sum())
                songs_timesplayed_overall.append(temp.shape[0])

            df = pd.DataFrame(list(zip(yearly_songs, songs_listentime_overall, songs_timesplayed_overall)),
                          columns=['Song', 'Total_listening_time_in_ms', 'No_of_times_played'])

            df['fav_song_score'] = 1.5 * ((df['Total_listening_time_in_ms'] - df['Total_listening_time_in_ms'].min()) / (
                df['Total_listening_time_in_ms'].max() - df['Total_listening_time_in_ms'].min())) + 1 * (
                                       (df['No_of_times_played'] - df['No_of_times_played'].min()) / (
                                       df['No_of_times_played'].max() - df['No_of_times_played'].min()))

            df = df.sort_values(by=['fav_song_score'], ascending=False).iloc[:10]
            df.index = range(0, 10)
            yearly_fav_songs.append(df)

        return yearly_fav_songs, self.years

    def favorite_album(self):
        albums_listentime_overall = list()
        albums_timesplayed_overall = list()

        for i in range(0, len(self.tot_albums_overall)):
            temp = self.data[self.data['master_metadata_album_album_name'] == self.tot_albums_overall[i]]
            albums_listentime_overall.append(temp['ms_played'].sum())
            albums_timesplayed_overall.append(temp.shape[0])

        df = pd.DataFrame(list(zip(self.tot_albums_overall, albums_listentime_overall, albums_timesplayed_overall)),
                          columns=['Album', 'Total_listening_time_in_ms', 'No_of_times_played'])

        df['fav_album_score'] = 1.5 * ((df['Total_listening_time_in_ms'] - df['Total_listening_time_in_ms'].min()) / (
                    df['Total_listening_time_in_ms'].max() - df['Total_listening_time_in_ms'].min())) + 1 * (
                                            (df['No_of_times_played'] - df['No_of_times_played'].min()) / (
                                                df['No_of_times_played'].max() - df['No_of_times_played'].min()))

        df = df.sort_values(by=['fav_album_score'], ascending=False).iloc[:50]
        df.index = range(0, 50)

        return df, df.iloc[:10]

    def favorite_time(self):
        time_of_day_listentime = list()
        time_of_day_songsplayed = list()

        for i in range(0, 4):
            temp = self.data[[d >= self.time_of_day[i][0] and d <= self.time_of_day[i][1] for d in self.data['time']]]
            time_of_day_songsplayed.append(temp.shape[0])
            time_of_day_listentime.append(temp['ms_played'].sum())

        df = pd.DataFrame(list(zip(self.td, time_of_day_listentime, time_of_day_songsplayed)),
                          columns=['Time_of_day', 'Total_listening_time_in_ms', 'Total_songs_listened_to'])

        df['fav_timeofday_score'] = 1.5 * ((df['Total_listening_time_in_ms'] - df['Total_listening_time_in_ms'].min()) / (
                df['Total_listening_time_in_ms'].max() - df['Total_listening_time_in_ms'].min())) + 1 * (
                                        (df['Total_songs_listened_to'] - df['Total_songs_listened_to'].min()) / (
                                        df['Total_songs_listened_to'].max() - df['Total_songs_listened_to'].min()))

        df = df.sort_values(by=['fav_timeofday_score'], ascending=False).iloc[:50]
        df.index = range(0, 4)
        return df

    def favorite_day(self):
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        favday_listentime = list()
        favday_songsplayed = list()

        for i in weekdays:
            temp = self.data[self.data['day_of_week'] == i]
            favday_listentime.append(temp['ms_played'].sum())
            favday_songsplayed.append(temp.shape[0])

        df = pd.DataFrame(list(zip(weekdays, favday_listentime, favday_songsplayed)),
                          columns=['Day_of_the_week', 'Total_listening_time_in_ms', 'Total_songs_listened_to'])

        df['fav_day_score'] = 1.5 * ((df['Total_listening_time_in_ms'] - df['Total_listening_time_in_ms'].min()) / (
                    df['Total_listening_time_in_ms'].max() - df['Total_listening_time_in_ms'].min())) + 1 * (
                                          (df['Total_songs_listened_to'] - df['Total_songs_listened_to'].min()) / (
                                              df['Total_songs_listened_to'].max() - df[
                                          'Total_songs_listened_to'].min()))

        df = df.sort_values(by=['fav_day_score'], ascending=False).iloc[:50]
        df.index = range(0, 7)

        return df

    def day_most_repeated_song(self):
        most_played_day = list()
        for i in range(0, len(self.dates_unique)):
            most_played_day.append(['nothing', 0])

        for i in range(0, len(self.dates_unique)):
            temp = self.data[self.data['date'] == self.dates_unique[i]]
            temp_songs = temp['master_metadata_track_name'].unique()
            for j in temp_songs:
                temp2 = temp[temp['master_metadata_track_name'] == j]
                if temp2.shape[0] > most_played_day[i][1]:
                    most_played_day[i][0] = j
                    most_played_day[i][1] = temp2.shape[0]

        df = pd.DataFrame(most_played_day, columns=['Name_of_song', 'No_of_times_played'])
        df.insert(loc=0, column='Date', value=self.dates_unique)
        df_most_played_singleday = df.sort_values(by=['No_of_times_played'], ascending=False).iloc[:50]
        df_most_played_singleday.index = range(0, 50)

        return df_most_played_singleday, df_most_played_singleday.iloc[:10]

    def day_highest_listening_time(self):
        day_listening_time = list()
        for i in range(0, len(self.dates_unique)):
            temp = self.data[self.data['date'] == self.dates_unique[i]]
            day_listening_time.append(temp['ms_played'].sum())

        df_day_listening_time = pd.DataFrame(list(zip(self.dates_unique, day_listening_time)),
                                             columns=['Date', 'Total_listening_time_in_ms'])
        df_day_listening_time = df_day_listening_time.sort_values(by=['Total_listening_time_in_ms'],
                                                                  ascending=False).iloc[:50]
        df_day_listening_time.index = range(0, 50)
        df_day_listening_time['Date'] = df_day_listening_time['Date'].astype('object')

        return df_day_listening_time, df_day_listening_time.iloc[:10]

    def day_most_songs_listened(self):
        day_songs_listened = list()
        for i in range(0, len(self.dates_unique)):
            temp = self.data[self.data['date'] == self.dates_unique[i]]
            day_songs_listened.append(len(temp['master_metadata_track_name'].unique()))

        df_day_songs_listened = pd.DataFrame(list(zip(self.dates_unique, day_songs_listened)),
                                             columns=['Date', 'Different_songs_listened'])
        df_day_songs_listened = df_day_songs_listened.sort_values(by=['Different_songs_listened'],
                                                                  ascending=False).iloc[:50]
        df_day_songs_listened.index = range(0, 50)
        df_day_songs_listened['Date'] = df_day_songs_listened['Date'].astype('object')

        return df_day_songs_listened, df_day_songs_listened.iloc[:10]

