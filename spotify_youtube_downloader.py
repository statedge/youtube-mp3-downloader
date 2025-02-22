import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch
import yt_dlp

# ---- CONFIGURATION ----
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "http://localhost:8080/callback"
SPOTIFY_SCOPE = "playlist-read-private"
DOWNLOAD_PATH = "/Users/your_username/Downloaded_Music"

# ---- AUTHENTICATE SPOTIFY ----
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SPOTIFY_SCOPE
))

# ---- FETCH TRACKS FROM PLAYLIST ----
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    
    for item in results["items"]:
        track = item["track"]
        artist_name = track["artists"][0]["name"]
        track_name = f"{artist_name} - {track['name']} Extended Mix"
        tracks.append(track_name)
    
    return tracks

# ---- SEARCH YOUTUBE ----
def search_youtube(track_name):
    try:
        search = VideosSearch(track_name, limit=1)
        result = search.result()
        if result["result"]:
            return result["result"][0]["link"]
    except Exception as e:
        print(f"⚠️ Error searching YouTube for {track_name}: {e}")
    return None

# ---- DOWNLOAD MP3 USING YT-DLP ----
def download_mp3(video_url, track_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, f"{track_name}.mp3"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([video_url])
    except Exception as e:
        print(f"⚠️ Error downloading {track_name}: {e}")

# ---- MAIN EXECUTION ----
if __name__ == "__main__":
    playlist_id = "YOUR_SPOTIFY_PLAYLIST_ID"
    output_folder = os.path.join(DOWNLOAD_PATH, "Your_Playlist_Name")
    os.makedirs(output_folder, exist_ok=True)
    
    tracks = get_playlist_tracks(playlist_id)

    for track in tracks:
        print(f"🔍 Searching YouTube for: {track}")
        video_url = search_youtube(track)
        
        if video_url:
            print(f"📥 Downloading: {track}")
            download_mp3(video_url, track, output_folder)
        else:
            print(f"❌ No YouTube results found for {track}")
    
    print("✅ All downloads completed!")