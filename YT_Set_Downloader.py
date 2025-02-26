import os
import re
import time
import yt_dlp
import subprocess

def ensure_folder_exists(folder_path):
    """Ensure the folder exists using a reliable method."""
    try:
        os.makedirs(folder_path, exist_ok=True)  # Standard method
    except Exception as e:
        print(f"⚠️ os.makedirs failed: {e}")
        print("🔄 Trying system mkdir instead...")
        subprocess.run(["mkdir", "-p", folder_path])  # Use system mkdir if needed

    # Verify folder creation
    if os.path.exists(folder_path):
        print(f"✅ Confirmed: Folder exists - {folder_path}")
    else:
        print(f"❌ ERROR: Folder still not found - {folder_path}")
        
def extract_tracks_from_description(description):
    """Extracts track names from the video description based on timestamps."""
    if not description:
        return []

    # Updated regex: Matches timestamps (like 5:50 or 01:20:15) and track names correctly.
    pattern = r"(?m)^\s*\d{1,2}:\d{2}(:\d{2})?\s+(.+)$"
    matches = re.findall(pattern, description)

    # Extract only track names, ignoring timestamps
    tracks = [match[1].strip() + " Extended Mix" for match in matches]

    return tracks if tracks else []

def extract_tracks_from_chapters(video_info):
    """Extracts track names from video chapters."""
    chapters = video_info.get("chapters", [])
    return [chapter['title'] + " Extended Mix" for chapter in chapters] if chapters else []

def extract_tracks_from_music_metadata(video_info):
    """Extracts track names from the auto-generated 'Music' section."""
    metadata = video_info.get("automatic_captions", {})
    return [entry['title'] + " Extended Mix" for entry in metadata.values()] if metadata else []

def search_youtube(track_name):
    """Search for a track on YouTube and return the first result URL."""
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            search_result = ydl.extract_info(f"ytsearch:{track_name}", download=False)
            if "entries" in search_result and search_result["entries"]:
                return search_result["entries"][0]["webpage_url"]
    except Exception as e:
        print(f"⚠️ Error searching YouTube for {track_name}: {e}")
    return None

def download_mp3(video_url, track_name, download_path):
    """Download an MP3 file from YouTube."""
    ensure_folder_exists(download_path)
    
    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(download_path, f"{track_name}.mp3"),
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

def process_dj_mix(youtube_url, base_download_path):
    """Main function to extract tracklist, search, and download tracks as MP3."""
    try:
        ydl_opts = {
            'quiet': True,
            'force_generic_extractor': True,
            'skip_download': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False) or {}
            set_name = re.sub(r'[^\w\s-]', '', info.get('title', 'Unknown_Set')).replace(' ', '_')
            description = info.get('description', '')

        destination_folder = os.path.join(base_download_path, set_name)
        ensure_folder_exists(destination_folder)

        # Extract tracklist in priority order
        tracks = extract_tracks_from_description(description)
        if not tracks:
            tracks = extract_tracks_from_chapters(info)
        if not tracks:
            tracks = extract_tracks_from_music_metadata(info)

        if not tracks:
            print("❌ No tracklist found in description, chapters, or metadata. Manual extraction required.")
            return

        print(f"✅ Found {len(tracks)} tracks. Saving in: {destination_folder}")

        for track in tracks:
            print(f"🔍 Searching YouTube for: {track}")
            track_url = search_youtube(track)

            if track_url:
                print(f"⬇️ Found: {track_url}. Downloading...")
                download_mp3(track_url, track, destination_folder)
            else:
                print(f"❌ Could not find a good match for {track}, skipping.")

            time.sleep(2)  # Avoid rate-limiting
        
        print("✅ Process complete.")
    
    except Exception as e:
        print(f"❌ An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    YOUTUBE_URL = "https://www.youtube.com/watch?v=vBCNlxFTkJk&t=91s"  # Replace with your DJ set link
    DOWNLOAD_BASE_PATH = "/Users/your_username/Downloaded_Music/DJ_Sets"  # Change this to your preferred path
    process_dj_mix(YOUTUBE_URL, DOWNLOAD_BASE_PATH)



