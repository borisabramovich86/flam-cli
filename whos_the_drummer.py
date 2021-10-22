
import requests 
import json

import spotify
import genius

from pprint import pprint
from imgcat import imgcat

#TODO save image in one dir, and not wherever program is activated
#TODO create several playlists per musician type
#TODO check if musician was found (by name), to not list hom twice
#TODO handle request errors
#TODO Set spotify user

class WhosTheDrummer:
	track_list = []

	def __init__(self, active_artist_types, exclude_song_string,create_artist_playlist = False,get_artist_songs = False,max_results_pages = 3):
			self.active_artist_types = active_artist_types
			self.create_artist_playlist = create_artist_playlist
			self.get_artist_songs = get_artist_songs
			self.exclude_song_string = exclude_song_string
			self.MAX_RESULT_PAGES = max_results_pages

	def __check_artist_match(self, artist_label, artist_data):
		artist_data_string = json.dumps(artist_data)
		return artist_label in artist_data_string

	def __print_drummer(self, display_text, name):
		print(display_text, name, u'\U0001f918')

	def __download_and_display_image(self, image_url):
		r = requests.get(image_url)
		with open('artist_image.jpg', 'wb') as outfile:
			outfile.write(r.content)

		imgcat(open("./artist_image.jpg"))

	def __parse_song(self, song_title):
		print(song_title)

		if(self.create_artist_playlist):
			song_uri = spotify.get_song_uri(song_title)
			if song_uri is not None:
				self.track_list.append(song_uri)

	def __get_artist_songs_by_id(self, artist_id):
		hasMoreSongs = True
		page = 1
		song_counter = 0;

		print("Also collaborated on:")

		while(hasMoreSongs and page <= self.MAX_RESULT_PAGES):
			response = genius.get_artist_songs(artist_id, page)

			for song in response["songs"]:
				song_title = song['full_title'].replace(u'\xa0', u' ').lower()
				if not self.exclude_song_string:
					song_counter += 1
					self.__parse_song(song_title)
				else:
					should_print =  all([not (exclusion in song_title) for exclusion in self.exclude_song_string])
					if should_print:
						song_counter += 1
						self.__parse_song(song_title)

			hasMoreSongs = response["next_page"] != None
			page += 1
				
		print("Found {} songs for artist".format(song_counter))

	def __handle_match(self, artist_id, name, artist_type, artist_image_url):
		global artist_name

		self.__print_drummer(artist_type.display_text, name)
		self.__download_and_display_image(artist_image_url)
		artist_name = name
		if self.get_artist_songs:
			self.__get_artist_songs_by_id(artist_id)

	def __check_artist_list_for_match(self, artist_list):
		for featured_artist in artist_list:
			for index, artist_type in enumerate(self.active_artist_types):
				artist_info = genius.get_artist_by_id(featured_artist['id'])
				if self.__check_artist_match(artist_type.check_artist_label, artist_info):
					artist = artist_info['response']['artist']
					self.active_artist_types[index].found = True
					if(self.create_artist_playlist):
						self.active_artist_types[index].spotify_uris = []
					self.__handle_match(artist['id'], artist['name'], artist_type, artist['image_url'])

	def get_artist_by_song_id(self, song_id):
		song = genius.get_song_by_id(song_id)
		print(song_id, song['full_title'])
		self.__check_artist_list_for_match(song['featured_artists'])
		self.__check_artist_list_for_match(song['writer_artists'])

		for custom_artist in song['custom_performances']:
			for index, artist_type in enumerate(self.active_artist_types):
				if artist_type.label in custom_artist['label']:
					for artist in custom_artist['artists']:
						self.active_artist_types[index].found = True
						self.__handle_match(artist['id'], artist['name'], artist_type, artist['image_url'])
		
		if(len(self.track_list) > 0):
			print("Found {} songs on Spotify".format(len(self.track_list)))

		if(self.create_artist_playlist and len(self.active_artist_types) == 1):
			spotify.create_playlist(self.track_list, artist_name)
