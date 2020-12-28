import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

os.environ["SPOTIPY_CLIENT_ID"] = "edf087240ef7499184317825f5838869"
os.environ["SPOTIPY_CLIENT_SECRET"] = "a7b6c075b9fb47efaa4936c2b3fa5afc"
os.environ["SPOTIPY_REDIRECT_URI"] = "https://www.google.com"
scope = "user-library-read user-library-modify playlist-modify-public"
spotipy_auth = SpotifyOAuth(scope=scope)
sp = spotipy.Spotify(auth_manager=spotipy_auth)
access_token = spotipy_auth.get_access_token(as_dict=False)
current_user = sp.current_user()
user_id = current_user['id']
user_name = current_user['display_name']

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id, fields='items(track(id,name))')
    tracks = {}
    for item in results['items']:
        if item['track']['id'] not in tracks:
            tracks[item['track']['id']] = item['track']['name']
    
    print(f'Length of playlist: {len(tracks)}')
    return tracks

def create_new_playlist(new_playlist_name):
    results = sp.current_user_playlists()
    items = results['items']

    playlist_id = None
    for item in items:
        if item['name'] == new_playlist_name:
            playlist_id = item['id']
    
    if not playlist_id:
        sp.user_playlist_create(user_id, new_playlist_name)

        results = sp.current_user_playlists()
        items = results['items']

        for item in items:
            if item['name'] == new_playlist_name:
                playlist_id = item['id']
    
    return playlist_id

def get_tracks_with_originals(cover_tracks):
    tracks_with_originals = []

    # For each track id mapped to a name in cover_tracks
    for track_id in cover_tracks:
        print(f'Processing song {cover_tracks[track_id]}')
        # Find the first exact match in name
        clean_name = clean_song_name(cover_tracks[track_id])
        original_id = lookup_song_name(clean_name)

        tracks_with_originals.append(track_id) # add id of original track
        if original_id:
            tracks_with_originals.append(original_id)

    return tracks_with_originals

def clean_song_name(name):
    return name.upper().replace('COVER','')

def lookup_song_name(name):
    results = sp.search(name, limit=5, type='track', market='US')

    possible_tracks = results['tracks']['items']
    for track in possible_tracks:
        if check_name_match(track['name'], name):
            song_id = track['id']
            return song_id
    
    if len(possible_tracks) == 0:
        return None

    return possible_tracks[0]['id']

def check_name_match(name_query, name_result):
    query_words = name_query.split(' ')
    result_words = name_result.split(' ')
    if len(result_words) < len(query_words):
        return False

    for i in range(len(query_words)):
        if query_words[i].upper() != result_words[i].upper():
            return False
    
    return True

def add_tracks_to_playlist(playlist_id, tracks):
    sp.playlist_add_items(playlist_id, tracks)

def main():
    covers_playlist_id = '4RkDMdAFmxTp2E9FsMRq0R'
    cover_tracks = get_playlist_tracks(covers_playlist_id)
    name = 'Violin Pop Covers with Originals'
    new_playlist_id = create_new_playlist(name)
    print('Playlist created / found!')
    tracks_with_originals = get_tracks_with_originals(cover_tracks)
    add_tracks_to_playlist(new_playlist_id, tracks_with_originals)
    print('All done!')

if __name__ == '__main__':
    main()