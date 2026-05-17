import requests
import time
import random

PLAYLIST_ID = "4hAcPDgrjwpAFkZlno7w9o"
CLIENT_TOKEN = "AAAm3VOKdmQit2+VxsK7JphMTzx0Jl8CIummXoPd/r2Ge7g4NHpq4Fqw01SxPfIFhwJZyY+0fZqBjuTvwl2UkXOVTelhUBGXWXWFXEe3VrMnzcHYB18FqYIKRMyQHngYvuagfFVpJ/udCfYC3zxzBcxZim7V44s8tuzNjIdaDL2vNXjMjQ+Zrc/E1kQtL7HttN9qr9uHFetEDNDEkicPgCXG7Mwz5tEHTAIbOjg5uOqvcTDdcWiEwOzCqou9RTSNc62uraqxV57DUe3GWa55l3bxx1iZW0oemA5e6DaOz1KGxrfjs0/yNj2Ag100cdi+aQTZ03p+V+ly/PCXP31E73IA5C8="
BEARER_TOKEN = "BQAsRUikbrSJ3eYsg22iv33s8308r_RRqVDE4M5bpd_J5XB1qQuQWiHgPqOAngc_FkBthApBQAzxQOLIY_NEEwJv4VWiX4pR9R8-8b2ArxbCZoHGRUbSF3XswhHuc3XNDH1Js9U5HczM5iWjqsH-lwOCg19eh1Lb5ZEOuM_jCc10lRelFmJhzSDM9DUG4K7YXAB-sc1483_uNCZ7hDEFkb6wY3AA_qvJ4RJ7FynWMlF0lO-i_h3mm7KzJhgqvKJckDLByVhnlc3K8En6KdLM_wDBvZmIiqnLiMKBXLbenBCLU7WSyCV48Pw2vnXJzRIDoGvr78J82nqvXhflDIEE6k8F6oB5xIUwfMvhq5fu35Zt4le5UOGcV6CBFU-MivL1GtdQcwtpYAKxa2WNcA"

TEST_TRACK = "spotify:track:7o2AeQZzfCERsRmOM86EcB"

_API_URL = "https://api-partner.spotify.com/pathfinder/v2/query"
_SPOTIFY_VERSION = "1.2.90.25.g97ec8403"
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
_HASH_ADD_REMOVE = "47b2a1234b17748d332dd0431534f22450e9ecbb3d5ddcdacbd83368636a0990"
_HASH_FETCH = "a65e12194ed5fc443a1cdebed5fabe33ca5b07b987185d63c72483867ad13cb4"

def _headers():
    return {
        "Accept": "application/json",
        "Accept-Language": "en",
        "app-platform": "WebPlayer",
        "client-token": CLIENT_TOKEN,
        "authorization": f"Bearer {BEARER_TOKEN}",
        "content-type": "application/json;charset=UTF-8",
        "spotify-app-version": _SPOTIFY_VERSION,
        "Origin": "https://open.spotify.com",
        "Referer": "https://open.spotify.com/",
        "User-Agent": _USER_AGENT,
    }

def fetch_all_tracks():
    all_tracks = []
    offset = 0
    while True:
        body = {
            "variables": {
                "uri": f"spotify:playlist:{PLAYLIST_ID}",
                "offset": offset,
                "limit": 25,
                "includeEpisodeContentRatingsV2": False,
            },
            "operationName": "fetchPlaylistContents",
            "extensions": {"persistedQuery": {"version": 1, "sha256Hash": _HASH_FETCH}},
        }
        r = requests.post(_API_URL, json=body, headers=_headers())
        if not r.text:
            print(f"Empty response at offset {offset}")
            break
        items = r.json()['data']['playlistV2']['content']['items']
        for item in items:
            track_id = item['itemV2']['data']['uri'].split(':')[-1]
            uid = item['uid']
            all_tracks.append((track_id, uid))
        print(f"  Fetched {len(all_tracks)} tracks so far...")
        if len(items) < 25:
            break
        offset += 25
    return all_tracks

def remove_track(uid):
    body = {
        "variables": {
            "playlistUri": f"spotify:playlist:{PLAYLIST_ID}",
            "uids": [uid],
        },
        "operationName": "removeFromPlaylist",
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": _HASH_ADD_REMOVE}},
    }
    r = requests.post(_API_URL, json=body, headers=_headers())
    return r.status_code

# --- Phase 0: Clear all existing tracks ---
print("\n=== PHASE 0: Clearing playlist ===\n")
tracks = fetch_all_tracks()
print(f"Found {len(tracks)} tracks to remove\n")

for i, (track_id, uid) in enumerate(tracks):
    status = remove_track(uid)
    print(f"  [{i+1}/{len(tracks)}] Removed {track_id} → {status}")
    if status == 401:
        print("  Token expired — aborting")
        exit()
    time.sleep(random.uniform(0.3, 0.5))

print(f"\nPlaylist cleared.\n")

# --- Phase 1: Add 5000 tracks ---
print("=== PHASE 1: Adding 5000 tracks ===\n")
add_results = {"200": 0, "other": {}}
start = time.time()

for i in range(5000):
    body = {
        "variables": {
            "playlistItemUris": [TEST_TRACK],
            "playlistUri": f"spotify:playlist:{PLAYLIST_ID}",
            "newPosition": {"moveType": "BOTTOM_OF_PLAYLIST", "fromUid": None},
        },
        "operationName": "addToPlaylist",
        "extensions": {"persistedQuery": {"version": 1, "sha256Hash": _HASH_ADD_REMOVE}},
    }
    r = requests.post(_API_URL, json=body, headers=_headers())
    status = r.status_code
    if status == 200:
        add_results["200"] += 1
    else:
        add_results["other"][status] = add_results["other"].get(status, 0) + 1
        print(f"  ⚠ Request {i+1}: status {status}")
        if status == 401:
            print("  Token expired — stopping add phase")
            break
    
    interval = random.uniform(0.3, 0.5)
    print(f"  [{i+1}/5000] → {status} (wait {interval:.2f}s)")
    time.sleep(interval)

add_time = time.time() - start
print(f"\n--- Add results ---")
print(f"Successful: {add_results['200']}/5000")
print(f"Failed: {add_results['other']}")
print(f"Total time: {add_time:.1f}s")

# --- Token refresh before remove phase ---
print("\n=== TOKEN REFRESH ===")
print("Grab fresh tokens from DevTools before continuing.")
new_bearer = input("Enter fresh Bearer token (or press Enter to keep current): ").strip()
if new_bearer:
    BEARER_TOKEN = new_bearer
new_client = input("Enter fresh Client token (or press Enter to keep current): ").strip()
if new_client:
    CLIENT_TOKEN = new_client

# --- Phase 2: Fetch UIDs ---
print("\n=== Fetching UIDs ===\n")
all_tracks = fetch_all_tracks()
print(f"\nTotal tracks: {len(all_tracks)}")
print(f"Tracks to remove: {len(all_tracks)}")

# --- Phase 3: Remove all tracks ---
print(f"\n=== PHASE 3: Removing {len(all_tracks)} tracks ===\n")
remove_results = {"200": 0, "other": {}}
start = time.time()

for i, (track_id, uid) in enumerate(all_tracks):
    status = remove_track(uid)
    if status == 200:
        remove_results["200"] += 1
    else:
        remove_results["other"][status] = remove_results["other"].get(status, 0) + 1
        print(f"  ⚠ Request {i+1}: status {status}")
        if status == 401:
            print("  Token expired — stopping remove phase")
            break
    
    interval = random.uniform(0.3, 0.5)
    print(f"  [{i+1}/{len(all_tracks)}] Removed {track_id} → {status} (wait {interval:.2f}s)")
    time.sleep(interval)

remove_time = time.time() - start
print(f"\n--- Remove results ---")
print(f"Successful: {remove_results['200']}/{len(all_tracks)}")
print(f"Failed: {remove_results['other']}")
print(f"Total time: {remove_time:.1f}s")

print(f"\n=== SUMMARY ===")
print(f"Added:   {add_results['200']}/5000 successful")
print(f"Removed: {remove_results['200']}/{len(all_tracks)} successful")
print(f"Total time: {add_time + remove_time:.1f}s")