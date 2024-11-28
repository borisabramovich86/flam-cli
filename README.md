Who's the Drummer

A CLI to determine the drummer of a given song

Installation  
Make file executable: `chmod +x flam`  
Add file to path: `export PATH="/path/to/flam-cli:$PATH"`

Set ENV variables:  
SPOTIFY_USER_NAME  
SPOTIPY_CLIENT_ID  
SPOTIPY_CLIENT_SECRET  
SPOTIPY_REDIRECT_URI  
GENIUS_API_TOKEN

Usage  

`flam --help `   
`flam 'Ride on ACDC'` - Get drummer for the song  
`flam -g 'Ride on ACDC'` - Get guitarists for the song  
`flam -b 'Ace of spades'` - Get bassist for the song  
`flam -p 'One and the same audioslave'` - Create playlist for artist results