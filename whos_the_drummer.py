#!/anaconda3/bin/python

import requests 
import json
import os
import sys
import spotipy
import argparse
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
from imgcat import imgcat

GENIUS_API_TOKEN=os.environ['GENIUS_API_TOKEN']
SPOTIFY_USERNAME = os.environ['SPOTIFY_USER_NAME']
MAX_RESULT_PAGES = 3
create_artist_playlist = False
get_artist_songs = False


headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
spotify_client = None
track_list = []
artist_name = ""
active_artist_types = []
exclude_song_string = ""

#TODO save image in one dir, and not wherever program is activated
#TODO create several playlists per musician type
#TODO check if musician was found (by name), to not list hom twice
#TODO create playlist with MULTIPLE excpetions

class Drummer:  
	label = "Drums"
	check_artist_label = "drummer"
	display_text = "Drummer - "
	found = False

class Bassist:
	label = "Bass"
	check_artist_label = "bassist"
	display_text = "Bassist - "
	found = False

class Keyboardist:
	label = "Keyboards"
	check_artist_label = "keyboardist"
	display_text = "Keyboardist - "
	found = False

class Guitarist:
	label = "Guitar"
	check_artist_label = "guitarist"
	display_text = "Guitarist - "
	found = False

class Vocals:
	label = "Vocals"
	check_artist_label = "singer"
	display_text = "Vocalist - "
	found = False

def authenticate_spotify():
	scope = "playlist-modify-public"
	sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope,username=SPOTIFY_USERNAME))
	return sp

def chunks(list, n):
	"""Yield successive n-sized chunks from list."""
	for i in range(0, len(list), n):
		yield list[i:i + n]

def get_song_uri(song_name):
	edited_song_name = song_name.replace('by', '')
	result = spotify_client.search(q='track:' + edited_song_name, type='track')
	tracks = result['tracks']['items']
	if(len(tracks) > 0):
		artist = tracks[0]
		name = artist['name']
		uri = artist['uri']
		return uri
	return None

def getData(url):
	response = requests.get(url = url, headers = headers)
	parsed_json = response.json()
	return parsed_json

def getArtistById(artist_id):
	URL = "https://api.genius.com/artists/{}".format(artist_id)
	artist_data = getData(URL)
	return artist_data

def checkArtistMatch(artist_label, artist_data):
	artist_data_string = json.dumps(artist_data)
	return artist_label in artist_data_string

def printDrummer(display_text, name):
	print(display_text, name, u'\U0001f918')

def downAndDisplayArtistImage(image_url):
	r = requests.get(image_url)
	with open('artist_image.jpg', 'wb') as outfile:
		outfile.write(r.content)

	imgcat(open("./artist_image.jpg"))

def getDrummerSongs(drummer_id):
	global spotify_client
	hasMoreSongs = True
	page = 1
	song_counter = 0;

	print("Also collaborated on:")

	while(hasMoreSongs and page <= MAX_RESULT_PAGES):
		URL = "https://api.genius.com/artists/{}/songs?sort=popularity&page={}".format(drummer_id, page)
		response = getData(URL)

		for song in response['response']['songs']:
			song_title = song['full_title']
			if not exclude_song_string in song_title.lower():
				print(song_title)
				song_counter += 1
				if(create_artist_playlist):
					spotify_client = authenticate_spotify()
					song_uri = get_song_uri(song_title)
					if song_uri is not None:
						track_list.append(song_uri)

		hasMoreSongs = response['response']['next_page'] != None
		page += 1
			
	print("Found {} songs for artist".format(song_counter))

def handle_match(artist_id, artist_name, artist_type, artist_image_url):
	printDrummer(artist_type.display_text, artist_name)
	downAndDisplayArtistImage(artist_image_url)
	if get_artist_songs:
		getDrummerSongs(artist_id)

def check_artist_list_for_match(artist_list):
	for featured_artist in artist_list:
		for artist_type in active_artist_types:
			artist_info = getArtistById(featured_artist['id'])
			if checkArtistMatch(artist_type.check_artist_label, artist_info):
				artist = artist_info['response']['artist']
				handle_match(artist['id'], artist['name'], artist_type, artist['image_url'])

def getArtistBySongID(song_id):
	global artist_name
	URL = "https://api.genius.com/songs/{}".format(song_id)
	song_data = getData(URL)
	song = song_data['response']['song']
	print(song_id, song['full_title'])
	check_artist_list_for_match(song['featured_artists'])
	check_artist_list_for_match(song['writer_artists'])

	#if(artist_name == ""): # TODO check found per artist type
	for custom_artist in song['custom_performances']:
		for artist_type in active_artist_types:
			if artist_type.label in custom_artist['label']:
				for artist in custom_artist['artists']:
					handle_match(artist['id'], artist['name'], artist_type, artist['image_url'])

def create_playlist():
	playlist_name = "Drummer " + artist_name + " Playlist"
	print("Creating playlist: " + playlist_name)
	print("Spotify username: " + SPOTIFY_USERNAME)

	new_playlist = spotify_client.user_playlist_create(SPOTIFY_USERNAME, playlist_name)
	playlist_id = new_playlist['id']
	split_track_list = chunks(track_list, 100)
	for track in split_track_list:
		results = spotify_client.user_playlist_add_tracks(SPOTIFY_USERNAME, playlist_id, track)

def main(args):
	song_name = args.song

	if len(active_artist_types) == 0:
		active_artist_types.append(Drummer)

	print("List songs: " + str(get_artist_songs))
	print("Create Playlist: " + str(create_artist_playlist))
	print("Max song pages to get: " + str(MAX_RESULT_PAGES))
	print("Exclude songs containing: " + exclude_song_string)

	print('Getting artists for : {}'.format(song_name))

	SEARCH_URL = "https://api.genius.com/search?q={}".format(song_name)
	search_results = requests.get(url = SEARCH_URL, headers = headers)
	results = search_results.json()
	song_id = results['response']['hits'][0]['result']['id']

	getArtistBySongID(song_id)

	if(len(track_list) > 0):
		print("Found {} songs on Spotify".format(len(track_list)))

	if create_artist_playlist:
		create_playlist()

def setArgs(args):
	global create_artist_playlist
	global SPOTIFY_USERNAME
	global MAX_RESULT_PAGES
	global get_artist_songs
	global active_artist_types
	global exclude_song_string

	if args.list_songs:
		get_artist_songs = True

	if args.playlist:
		create_artist_playlist = True
		get_artist_songs = True

	if args.username:
		SPOTIFY_USERNAME = args.username

	if (args.max_pages == 0):
		MAX_RESULT_PAGES = 100000
		
	if (args.max_pages):
		MAX_RESULT_PAGES = args.max_pages

	if(args.guitarist):
		active_artist_types.append(Guitarist)

	if(args.bass):
		active_artist_types.append(Bassist)

	if(args.drummer):
		active_artist_types.append(Drummer)

	if(args.keyboards):
		active_artist_types.append(Keyboardist)

	if(args.singer):
		active_artist_types.append(Vocals)

	if(args.all):
		active_artist_types.extend([Drummer, Guitarist, Bassist, Vocals, Keyboardist])

	if(args.exclude_songs):
		exclude_song_string = args.exclude_songs

parser = argparse.ArgumentParser(description="Who's the drummer")
parser.add_argument("song", type=str, help='song and/or band name')
parser.add_argument("-p", "--playlist", action="store_true", default=False, help='create artist playlist on Spotify. Default is False')
parser.add_argument("-g", "--guitarist", action="store_true", default=False, help='Get Guitarist/s for the song')
parser.add_argument("-k", "--keyboards", action="store_true", default=False, help='Get Keyboard player for the song')
parser.add_argument("-b", "--bass", action="store_true", default=False, help='Get Bass player for the song')
parser.add_argument("-d", "--drummer", action="store_true", default=False, help='Get Drummer for the song')
parser.add_argument("-s", "--singer", action="store_true", default=False, help='Get singer for the song')
parser.add_argument("-a", "--all", action="store_true", default=False, help='Get all musicians for song')
parser.add_argument("-u", "--username", type=str, help='Spotify username')
parser.add_argument("-e", "--exclude_songs", type=str, help='Exclude songs in playlist containing these strings')
parser.add_argument("-m", "--max_pages", type=int, help='maximum number of pages to list for artist songs. Default is 3. Set 0 for no limit')
parser.add_argument("-l", "--list_songs", action="store_true", default=False, help='Get list of songs that artist played on')
args = parser.parse_args()

setArgs(args)
main(args)



