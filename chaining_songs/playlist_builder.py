#!/usr/bin/python

"""
Small script to chain songs
"""

import argparse
import json


class NoValidSongFound(Exception):
        pass


class PlaylistBuilder:
    """
    Provides some methods to create solid playlists
    """
    def __init__(self, song_library='song-library.json'):
        with open(song_library, 'rb') as f:
            self.data = json.load(f)
        self.song_list = [(item['song'], item['duration']) for item in self.data]
        self.songs_used = []
        self.playlists = []
        self.f = self.get_song_tuple('Rock Me, Amadeus')
        self.l = self.get_song_tuple('Hold On Loosely')
        self.playlists_to_compare = []


    def get_possible_next_songs(self, song):
        """
        Accepts a tuple (song, duration)
        Returns a list of tuples (valid next song, duration)
        """
        valid_songs = []
        for item in self.song_list:
            if item[0][0].lower() == song[0][-1].lower():
                self.song_list.remove(item)
                valid_songs.append(item)

        if not valid_songs:
            message = "No valid songs available, please get more music"
            raise NoValidSongFound(message)

        return valid_songs


    def get_shortest_playlist(self, first_song, last_song, playlist=[]):
        """
        Returns one of shortest playlists in terms of number of songs
        """
        playlist = playlist or [first_song,]
        target_letter = last_song[0][0].lower()
        possible_next_songs = self.get_possible_next_songs(playlist[-1])
        for item in possible_next_songs:
            new_playlist = list(playlist + [item,])
            if item[0][-1].lower() == target_letter:
                new_playlist.append(last_song)
                return new_playlist
            if new_playlist not in self.playlists:
                self.playlists.append(new_playlist)

        for playlist in self.playlists:
            self.get_shortest_playlist(playlist, last_song)


    def get_song_tuple(self, song_title):
        """
        Accepts a song title as a string
        Returns a tuple (song title, duration)
        """
        for song in self.song_list:
            import re
            title = re.sub("[^\w ]+", "", song[0]).lower()
            song_title = re.sub("[^\w ]+", "", song_title).lower()
            if title == song_title:
                return song[0], song[1]
        message = "No song was found with that title"
        raise NoValidSongFound(message)


    def get_most_brief_playlist(self, first_song, last_song, playlist=[]):
        """
        Returns the most brief playlist in terms of duration of all the valid
        shortest playlists in terms of number of songs
        """


        playlist = playlist or [first_song,]
        target_letter = last_song[0][0].lower()
        possible_next_songs = self.get_possible_next_songs(playlist[-1])
        for item in possible_next_songs:
            new_playlist = list(playlist + [item,])
            if item[0][-1].lower() == target_letter:
                new_playlist.append(last_song)
                self.playlists_to_compare.append(new_playlist)
            if new_playlist not in self.playlists:
                self.playlists.append(new_playlist)

        if self.playlists_to_compare:
            result = self.compare_playlists(self.playlists_to_compare)
            return result
        else:
            for playlist in self.playlists:
                self.get_most_brief_playlist(playlist, last_song)


    def compare_playlists(self, playlists=[]):
        tuples = []
        for playlist in playlists:
            tuples.append(tuple(playlist))
        duration = dict([(item, 0) for item in tuples])
        for playlist in playlists:
            t = tuple(playlist)
            for item in playlist:
                duration[t] += int(item[1])
        return min(duration, key=lambda item: item[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--first-song', dest='first_song', required=True,
        help='The desired first song')
    parser.add_argument('-l', '--last-song',  dest='last_song', required=True,
        help='The desired last song')
    args = parser.parse_args()
    p = PlaylistBuilder()
    first_song = p.get_song_tuple(args.first_song)
    last_song = p.get_song_tuple(args.last_song)
    print p.get_shortest_playlist(first_song, last_song)

