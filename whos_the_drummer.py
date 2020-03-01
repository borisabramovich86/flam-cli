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
MAX_RESULT_PAGES = 3
create_artist_playlist = False
get_artist_songs = False
spotify_username = "SPOTIFY_USER_NAME"

headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
spotify_client = None
track_list = []
drummer_name = ""

def authenticate_spotify():
	scope = "playlist-modify-public"
	sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope,username=spotify_username))
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

def isArtistDrummer(artist_data):
	artist_data_string = json.dumps(artist_data)
	return "drummer" in artist_data_string

def printDrummer(name):
	print(name, u'\U0001f918')

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

	print("Also played on:")

	while(hasMoreSongs and page <= MAX_RESULT_PAGES):
		URL = "https://api.genius.com/artists/{}/songs?sort=popularity&page={}".format(drummer_id, page)
		response = getData(URL)

		for song in response['response']['songs']:
			song_title = song['full_title']
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

def getDrummerBySongID(song_id):
	global drummer_name
	URL = "https://api.genius.com/songs/{}".format(song_id)
	song_data = getData(URL)
	song = song_data['response']['song']

	print(song_id, song['full_title'])

	for featured_artist in song['featured_artists']:
		artist_info = getArtistById(featured_artist['id'])
		isArtistDrummer(artist_info)

	for writer_artist in song['writer_artists']:
		artist_info = getArtistById(writer_artist['id'])
		if isArtistDrummer(artist_info):
			drummer = artist_info['response']['artist']
			drummer_name = drummer['name']
			printDrummer(drummer_name)
			downAndDisplayArtistImage(drummer['image_url'])
			if get_artist_songs:
				getDrummerSongs(drummer['id'])
			break

	if(drummer_name == ""):
		for custom_artist in song['custom_performances']:
			if "Drums" in custom_artist['label']:
				for drummer in custom_artist['artists']:
					drummer_name = drummer['name']
					printDrummer(drummer_name)
					downAndDisplayArtistImage(drummer['image_url'])
					if get_artist_songs:
						getDrummerSongs(drummer['id'])

def create_playlist():
	playlist_name = "Drummer " + drummer_name + " Playlist"
	print("Creating playlist: " + playlist_name)
	print("Spotify username: " + spotify_username)

	new_playlist = spotify_client.user_playlist_create(spotify_username, playlist_name)
	playlist_id = new_playlist['id']
	split_track_list = chunks(track_list, 100)
	for track in split_track_list:
		results = spotify_client.user_playlist_add_tracks(spotify_username, playlist_id, track)

def main(args):
	song_name = args.song

	print("List songs: " + str(get_artist_songs))
	print("Create Playlist: " + str(create_artist_playlist))
	print("Max song pages to get: " + str(MAX_RESULT_PAGES))

	print('Getting drummer for : {}'.format(song_name))

	SEARCH_URL = "https://api.genius.com/search?q={}".format(song_name)
	search_results = requests.get(url = SEARCH_URL, headers = headers)
	results = search_results.json()
	song_id = results['response']['hits'][0]['result']['id']

	getDrummerBySongID(song_id)

	if(len(track_list) > 0):
		print("Found {} songs on Spotify".format(len(track_list)))

	if create_artist_playlist:
		create_playlist()

def setArgs(args):
	global create_artist_playlist
	global spotify_username
	global MAX_RESULT_PAGES
	global get_artist_songs

	if args.list_songs:
		get_artist_songs = True

	if args.playlist:
		create_artist_playlist = True
		get_artist_songs = True

	if args.username:
		spotify_username = args.username

	if (args.max_pages == 0):
		MAX_RESULT_PAGES = 100000
		
	if (args.max_pages):
		MAX_RESULT_PAGES = args.max_pages

parser = argparse.ArgumentParser(description="Who's the drummer")
parser.add_argument("song", type=str, help='song and/or band name')
parser.add_argument("-p", "--playlist", action="store_true", default=False, help='create artist playlist on Spotify. Default is False')
parser.add_argument("-u", "--username", type=str, help='Spotify username')
parser.add_argument("-m", "--max_pages", type=int, help='maximum number of pages to list for artist songs. Default is 3. Set 0 for no limit')
parser.add_argument("-l", "--list_songs", action="store_true", default=False, help='Get list of songs that artist played on')
args = parser.parse_args()

setArgs(args)
main(args)



