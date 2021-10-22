import os
import spotipy
import urllib.parse as urlparse
from spotipy.oauth2 import SpotifyOAuth
from utils import chunks
from pprint import pprint


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
	#TODO remove curse words for better search
	ft_index = song_name.find('ft.')
	if ft_index > 0:
		edited_song_name = song_name[0:ft_index].replace('by', '').replace("(", "").replace(")", "")
	else:
		edited_song_name = song_name.replace('by', '').replace("(", "").replace(")", "")
	result = sc.search(q='track:' + edited_song_name, type='track')
	tracks = result['tracks']['items']
	if(len(tracks) > 0):
		artist = tracks[0]
		name = artist['name']
		uri = artist['uri']
		return uri
	return None

def get_artist_uri(artist_name):
	sc = get_client()
	result = sc.search(q=artist_name, type='artist')
	artists = result['artists']['items']
	if(len(artists) > 0):
		artist = artists[0]
		name = artist['name']
		uri = artist['uri']
		return uri
	return None

def get_artist_top_tracks(artist_uri):
	sc = get_client()
	spotify_track_list = sc.artist_top_tracks(artist_uri)["tracks"]
	if len(spotify_track_list) > 0:
		spotify_track_list_uris = list(map(lambda x: x["uri"], spotify_track_list))
		return spotify_track_list_uris
	return []

def get_all_artist_tracks(artist_name):
	track_list_uris = []
	sc = get_client()
	offset = 0
	has_next = True 
	while (has_next):
		results = sc.search(q=artist_name, type='track', limit=50, offset=offset)
		for track in results['tracks']['items']:
			track_list_uris.append(track["uri"])
		has_next = results["tracks"]["next"]
		if has_next:
			par = urlparse.parse_qs(urlparse.urlparse(has_next).query)
			offset = par['offset'][0]

	return track_list_uris

def create_playlist(track_list, artist_name):
	sc = get_client()
	playlist_name = "Musician " + artist_name + " Playlist"
	print("Creating playlist: " + playlist_name)
	print("Spotify username: " + SPOTIFY_USERNAME)

	new_playlist = sc.user_playlist_create(SPOTIFY_USERNAME, playlist_name)
	playlist_id = new_playlist['id']
	artist_uri = get_artist_uri(artist_name)
	# artist_top_tracks = get_artist_top_tracks(artist_uri)
	# track_list.extend(artist_top_tracks)
	# all_artist_tracks = get_all_artist_tracks(artist_name)
	# track_list.extend(all_artist_tracks)
	split_track_list = chunks(track_list, 100)
	for track in split_track_list:
		results = sc.user_playlist_add_tracks(SPOTIFY_USERNAME, playlist_id, track)

