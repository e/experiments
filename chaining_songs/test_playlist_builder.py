# run this test by using py.test:
# (pip install pytest)
# $> py.test -k test_playlist_builder


from playlist_builder import PlaylistBuilder


def test_playlist_builder():
    playlist_builder = PlaylistBuilder()
    first_song = 'Rock Me, Amadeus'
    last_song = 'Go Tell It on the Mountain'
    playlist = playlist_builder.get_shortest_playlist(first_song, last_song)
    for index, item in enumerate(playlist):
        if index < len(playlist) - 1:
            assert item[0][-1].lower() == playlist[index+1][0][0].lower()

