#!/anaconda3/bin/python

import requests 
import json
import sys
from imgcat import imgcat

auth_token= GENIUS_API_TOKEN

headers = {'Authorization': 'Bearer ' + auth_token}

def getData(url):
	response = requests.get(url = url, headers = headers)

	parsed_json = response.json()

	return parsed_json

def getArtistById(artist_id):
	URL = "https://api.genius.com/artists/{}".format(artist_id)

	artist_data = getData(URL)

	return artist_data

def isArtistDrummer(artist_data):
	#print(artist_data)
	artist_data_string = json.dumps(artist_data)
	return "drummer" in artist_data_string

def printDrummer(drummer_name):
	print(drummer_name, u'\U0001f918')

def downAndDisplayArtistImage(image_url):
	#print("Downloading image", image_url)
	r = requests.get(image_url)
	with open('artist_image.jpg', 'wb') as outfile:
	    outfile.write(r.content)

	imgcat(open("./artist_image.jpg"))

def getDrummerBySongID(song_id):
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
			printDrummer(artist_info['response']['artist']['name'])
			downAndDisplayArtistImage(artist_info['response']['artist']['image_url'])
			break


	for custom_artist in song['custom_performances']:
		if "Drums" in custom_artist['label']:
	  		#print(json.dumps(artist, indent=4))
	  		for drummer in custom_artist['artists']:
	  			printDrummer(drummer['name'])
	  			downAndDisplayArtistImage(drummer['image_url'])
	  			#print(drummer['url'])
	  			#print(drummer['image_url'])
	  			#print(drummer['api_path'])

def main():
	song_name = ' '.join(sys.argv[1:])

	print('Getting drummer for : {}'.format(song_name))

	SEARCH_URL = "https://api.genius.com/search?q={}".format(song_name)

	search_results = requests.get(url = SEARCH_URL, headers = headers)

	results = search_results.json()

	song_id = results['response']['hits'][0]['result']['id']

	getDrummerBySongID(song_id)


main()



