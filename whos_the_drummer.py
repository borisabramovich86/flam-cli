#!/anaconda3/bin/python

import requests 
import json
import sys
import os
import spotipy
import argparse

import spotify
import genius

from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
from imgcat import imgcat

from musician import Drummer, Guitarist, Vocals, Bassist, Keyboardist


MAX_RESULT_PAGES = 3
create_artist_playlist = False
get_artist_songs = False
track_list = []
artist_name = ""
active_artist_types = []
exclude_song_string = None

#TODO save image in one dir, and not wherever program is activated
#TODO create several playlists per musician type
#TODO check if musician was found (by name), to not list hom twice
#TODO handle request errors

def check_artist_match(artist_label, artist_data):
	artist_data_string = json.dumps(artist_data)
	return artist_label in artist_data_string

def print_drummer(display_text, name):
	print(display_text, name, u'\U0001f918')

def download_and_display_image(image_url):
	r = requests.get(image_url)
	with open('artist_image.jpg', 'wb') as outfile:
		outfile.write(r.content)

	imgcat(open("./artist_image.jpg"))

def parse_song(song_title):
	print(song_title)

	if(create_artist_playlist):
		song_uri = spotify.get_song_uri(song_title)
		if song_uri is not None:
			track_list.append(song_uri)

def get_artist_songs_by_id(artist_id):
	hasMoreSongs = True
	page = 1
	song_counter = 0;

	print("Also collaborated on:")

	while(hasMoreSongs and page <= MAX_RESULT_PAGES):
		response = genius.get_artist_songs(artist_id, page)

		for song in response["songs"]:
			song_title = song['full_title'].replace(u'\xa0', u' ').lower()
			if not exclude_song_string:
				song_counter += 1
				parse_song(song_title)
			else:
				should_print =  all([not (exclusion in song_title) for exclusion in exclude_song_string])
				if should_print:
					song_counter += 1
					parse_song(song_title)

		hasMoreSongs = response["next_page"] != None
		page += 1
			
	print("Found {} songs for artist".format(song_counter))

def handle_match(artist_id, artist_name, artist_type, artist_image_url):
	print_drummer(artist_type.display_text, artist_name)
	download_and_display_image(artist_image_url)
	if get_artist_songs:
		get_artist_songs_by_id(artist_id)

def check_artist_list_for_match(artist_list):
	for featured_artist in artist_list:
		for index, artist_type in enumerate(active_artist_types):
			artist_info = genius.get_artist_by_id(featured_artist['id'])
			if check_artist_match(artist_type.check_artist_label, artist_info):
				artist = artist_info['response']['artist']
				active_artist_types[index].found = True
				if(create_artist_playlist):
					active_artist_types[index].spotify_uris = []
				handle_match(artist['id'], artist['name'], artist_type, artist['image_url'])

def get_artist_by_song_id(song_id):
	global artist_name

	song = genius.get_song_by_id(song_id)
	print(song_id, song['full_title'])
	check_artist_list_for_match(song['featured_artists'])
	check_artist_list_for_match(song['writer_artists'])

	#if(artist_name == ""): # TODO check found per artist type
	for custom_artist in song['custom_performances']:
		for index, artist_type in enumerate(active_artist_types):
			if artist_type.label in custom_artist['label']:
				for artist in custom_artist['artists']:
					active_artist_types[index].found = True
					handle_match(artist['id'], artist['name'], artist_type, artist['image_url'])

def main(args):
	song_name = args.song

	if len(active_artist_types) == 0:
		active_artist_types.append(Drummer())

	print("List songs: " + str(get_artist_songs))
	print("Create Playlist: " + str(create_artist_playlist))
	print("Max song pages to get: " + str(MAX_RESULT_PAGES))
	print("Exclude songs containing: " + str(exclude_song_string))
	print('Getting artists for : {}'.format(song_name))

	song_id = genius.get_first_search_result(song_name)

	get_artist_by_song_id(song_id)

	if(len(track_list) > 0):
		print("Found {} songs on Spotify".format(len(track_list)))

	if (create_artist_playlist and len(active_artist_types) == 1):
		create_playlist("")

def set_args(args):
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
		active_artist_types.append(Guitarist())

	if(args.bass):
		active_artist_types.append(Bassist())

	if(args.drummer):
		active_artist_types.append(Drummer())

	if(args.keyboards):
		active_artist_types.append(Keyboardist())

	if(args.singer):
		active_artist_types.append(Vocals())

	if(args.all):
		active_artist_types.extend([Drummer(), Guitarist(), Bassist(), Vocals(), Keyboardist()])

	if(args.exclude_songs):
		split_exclusions = args.exclude_songs.split(",")
		exclude_song_string = list(map(lambda x: x.replace(u'\xa0', u' ').lower(), split_exclusions))

def define_args():
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
	parser.add_argument("-e", "--exclude_songs", type=str, help='Exclude songs in playlist containing these strings, seperated by comma')
	parser.add_argument("-m", "--max_pages", type=int, help='maximum number of pages to list for artist songs. Default is 3. Set 0 for no limit')
	parser.add_argument("-l", "--list_songs", action="store_true", default=False, help='Get list of songs that artist played on')
	return parser.parse_args()	

args = define_args()
set_args(args)
main(args)



