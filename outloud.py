import re
import requests
import math
import time
import random

_API_URL = "https://api-partner.spotify.com/pathfinder/v2/query"
_SPOTIFY_VERSION = "1.2.90.25.g97ec8403"
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
_MAX_ASCII = 128

_HASH_ADD_REMOVE = "47b2a1234b17748d332dd0431534f22450e9ecbb3d5ddcdacbd83368636a0990"
_HASH_FETCH     = "a65e12194ed5fc443a1cdebed5fabe33ca5b07b987185d63c72483867ad13cb4"


def printBanner():
    print("                       /$$     /$$                           /$$")
    print("                      | $$    | $$                          | $$")
    print("  /$$$$$$  /$$   /$$ /$$$$$$  | $$  /$$$$$$  /$$   /$$  /$$$$$$$")
    print(" /$$__  $$| $$  | $$|_  $$_/  | $$ /$$__  $$| $$  | $$ /$$__  $$")
    print(r"| $$  \ $$| $$  | $$  | $$    | $$| $$  \ $$| $$  | $$| $$  | $$")
    print("| $$  | $$| $$  | $$  | $$ /$$| $$| $$  | $$| $$  | $$| $$  | $$")
    print("|  $$$$$$/|  $$$$$$/  |  $$$$/| $$|  $$$$$$/|  $$$$$$/|  $$$$$$$")
    print(r" \______/  \______/    \___/  |__/ \______/  \______/  \_______/")
    print("\nA steganographic data transmission system exploiting Spotify playlist track ordering.\n")
    print("                                                                by 1kb2.xyz\n")


def menu():
    print("1. Decode message")
    print("2. Send message")
    print("0. Exit")
    print("Note: Sending a new message will result in the previous message being deleted, so make sure to decode it before sending a new one!")


def _make_headers(client_token, bearer_token):
    return {
        "Accept": "application/json",
        "Accept-Language": "en",
        "app-platform": "WebPlayer",
        "client-token": client_token,
        "authorization": f"Bearer {bearer_token}",
        "content-type": "application/json;charset=UTF-8",
        "spotify-app-version": _SPOTIFY_VERSION,
        "Origin": "https://open.spotify.com",
        "Referer": "https://open.spotify.com/",
        "User-Agent": _USER_AGENT,
    }


def add_track(track_uri, playlist_id, client_token, bearer_token):
    body = {
        "variables": {
            "playlistItemUris": [track_uri],
            "playlistUri": f"spotify:playlist:{playlist_id}",
            "newPosition": {"moveType": "BOTTOM_OF_PLAYLIST", "fromUid": None},
        },
        "operationName": "addToPlaylist",
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": _HASH_ADD_REMOVE}},
    }
    response = requests.post(_API_URL, json=body, headers=_make_headers(client_token, bearer_token))
    return response.status_code


def fetch_tracks_with_uids(playlist_id, client_token, bearer_token):
    all_tracks = []
    offset = 0
    while True:
        body = {
            "variables": {
                "uri": f"spotify:playlist:{playlist_id}",
                "offset": offset,
                "limit": 25,
                "includeEpisodeContentRatingsV2": False,
            },
            "operationName": "fetchPlaylistContents",
            "extensions": {"persistedQuery": {"version": 1, "sha256Hash": _HASH_FETCH}},
        }
        response = requests.post(_API_URL, json=body, headers=_make_headers(client_token, bearer_token))
        if not response.text:
            print(f"Empty response (status {response.status_code}) — token likely expired")
            return []
        items = response.json()['data']['playlistV2']['content']['items']
        for item in items:
            track_id = item['itemV2']['data']['uri'].split(':')[-1]
            uid = item['uid']
            all_tracks.append((track_id, uid))
        if len(items) < 25:
            break
        offset += 25
    return all_tracks


def remove_track(uid, playlist_id, client_token, bearer_token):
    body = {
        "variables": {
            "playlistUri": f"spotify:playlist:{playlist_id}",
            "uids": [uid],
        },
        "operationName": "removeFromPlaylist",
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": _HASH_ADD_REMOVE}},
    }
    response = requests.post(_API_URL, json=body, headers=_make_headers(client_token, bearer_token))
    return response.status_code


def clear_messages(playlist_id, sync_length, client_token, bearer_token):
    tracks = fetch_tracks_with_uids(playlist_id, client_token, bearer_token)
    for track_id, uid in tracks[sync_length:]:
        status = remove_track(uid, playlist_id, client_token, bearer_token)
        print(f"Removed {track_id} → status {status}")
        time.sleep(random.uniform(2, 5))


def encode_char(char, sync_length, tracks_per_char, reverse_codebook):
    value = ord(char)
    if value >= _MAX_ASCII:
        raise ValueError(f"Character {char!r} (ord {value}) is not ASCII — only 0–127 supported")
    digits = []
    for _ in range(tracks_per_char):
        value, remainder = divmod(value, sync_length)
        digits.append(remainder)
    digits.reverse()
    return [reverse_codebook[d] for d in digits]


def _tracks_per_char(sync_length):
    return math.ceil(math.log(_MAX_ASCII, sync_length))


def main():
    printBanner()

    _DEFAULT_PLAYLIST_ID = "1Ws2L2kUi8Q5m0yn5lPLqK"
    _DEFAULT_SYNC_LENGTH = "12"

    PLAYLIST_ID  = input(f"Enter Playlist ID [{_DEFAULT_PLAYLIST_ID}]: ").strip() or _DEFAULT_PLAYLIST_ID
    SYNC_LENGTH  = int(input(f"Enter Sync Length [{_DEFAULT_SYNC_LENGTH}]: ").strip() or _DEFAULT_SYNC_LENGTH)
    CLIENT_TOKEN = input("Enter Client Token [***]: ").strip()
    BEARER_TOKEN = input("Enter Bearer token [***]: ").strip()

    tpc = _tracks_per_char(SYNC_LENGTH)

    while True:
        menu()
        option = int(input("Enter your option: ").strip())

        if option == 0:
            break

        elif option == 1:
            track_pairs = fetch_tracks_with_uids(PLAYLIST_ID, CLIENT_TOKEN, BEARER_TOKEN)
            tracks = [t for t, _ in track_pairs]

            codebook = {track_id: i for i, track_id in enumerate(tracks[:SYNC_LENGTH])}

            message = ""
            for i in range(0, len(tracks[SYNC_LENGTH:]), tpc):
                chunk = tracks[SYNC_LENGTH:][i:i + tpc]
                value = 0
                for digit in chunk:
                    value = value * SYNC_LENGTH + codebook[digit]
                message += chr(value)

            print("\n\nDecoded message:", message)

        elif option == 2:
            clear_messages(PLAYLIST_ID, SYNC_LENGTH, CLIENT_TOKEN, BEARER_TOKEN)
            MESSAGE = input("Enter message: ").strip()

            track_pairs   = fetch_tracks_with_uids(PLAYLIST_ID, CLIENT_TOKEN, BEARER_TOKEN)
            sync_tracks   = [t for t, _ in track_pairs[:SYNC_LENGTH]]
            reverse_codebook = {i: track_id for i, track_id in enumerate(sync_tracks)}

            for char in MESSAGE:
                track_uris = encode_char(char, SYNC_LENGTH, tpc, reverse_codebook)
                for uri in track_uris:
                    status = add_track(f"spotify:track:{uri}", PLAYLIST_ID, CLIENT_TOKEN, BEARER_TOKEN)
                    print(f"Added track {uri} → status {status}")
                    time.sleep(random.uniform(3, 8))

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
