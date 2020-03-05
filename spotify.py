import os
from utils import chunks

SPOTIFY_USERNAME = os.environ['SPOTIFY_USER_NAME']
spotify_client = None

def authenticate_spotify():
	scope = "playlist-modify-public"
	sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope,username=SPOTIFY_USERNAME))
	return sp

def get_client():
	if spotify_client:
		return spotify_client
	return authenticate_spotify()

def get_song_uri(song_name):
	sc = get_client()
	edited_song_name = song_name.replace('by', '')
	result = sc.search(q='track:' + edited_song_name, type='track')
	tracks = result['tracks']['items']
	if(len(tracks) > 0):
		artist = tracks[0]
		name = artist['name']
		uri = artist['uri']
		return uri
	return None

def create_playlist(artist_name):
	sc = get_client()
	playlist_name = "Musician " + artist_name + " Playlist"
	print("Creating playlist: " + playlist_name)
	print("Spotify username: " + SPOTIFY_USERNAME)

	new_playlist = sc.user_playlist_create(SPOTIFY_USERNAME, playlist_name)
	playlist_id = new_playlist['id']
	#spotify_track_list = spotify_client.artist_top_tracks(urn)
	split_track_list = chunks(track_list, 100)
	for track in split_track_list:
		results = spotify_client.user_playlist_add_tracks(SPOTIFY_USERNAME, playlist_id, track)