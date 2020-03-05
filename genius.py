import os
import requests

GENIUS_API_TOKEN=os.environ['GENIUS_API_TOKEN']
headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}

def get_data(url):
	response = requests.get(url = url, headers = headers)
	parsed_json = response.json()
	return parsed_json

def get_artist_by_id(artist_id):
	URL = "https://api.genius.com/artists/{}".format(artist_id)
	artist_data = get_data(URL)
	return artist_data

def get_first_search_result(song_name):
	SEARCH_URL = "https://api.genius.com/search?q={}".format(song_name)
	results = get_data(SEARCH_URL)
	song_id = results['response']['hits'][0]['result']['id']
	return song_id

def get_song_by_id(song_id):
	URL = "https://api.genius.com/songs/{}".format(song_id)
	song_data = get_data(URL)
	song = song_data['response']['song']
	return song

def get_artist_songs(artist_id, page):
	URL = "https://api.genius.com/artists/{}/songs?sort=popularity&page={}".format(artist_id, page)
	response = get_data(URL)
	response_obj = response['response']
	return {"songs": response_obj['songs'], "next_page": response_obj['next_page']}