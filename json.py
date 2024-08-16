import os
from datetime import timedelta
import json
from tqdm import tqdm

import yt_dlp
input_jsonl_path = "/home/cone/team/user/Cone/InternVid/InternVid-18M-aes.jsonl"

output_jsonl_dir = "/home/cone/team/user/Cone/DATA/jsonl/"
os.makedirs(output_jsonl_dir, exist_ok=True)

from datetime import datetime, timedelta
def convert_timestamp_to_seconds(timestamp_str):
    try:
        timestamp = datetime.strptime(timestamp_str, "%H:%M:%S.%f")
        return timestamp.second + timestamp.minute * 60 + timestamp.hour * 3600
    except ValueError:
        print(f"error: {timestamp_str}")
        return None
def process_video_info(video_info):
    start_timestamp = video_info["Start_timestamp"]
    end_timestamp = video_info["End_timestamp"]
    start_seconds = convert_timestamp_to_seconds(start_timestamp)
    end_seconds = convert_timestamp_to_seconds(end_timestamp)
    if start_seconds is None or end_seconds is None:
        print("start_time or end time is None")
        return

    duration = end_seconds - start_seconds
    if duration < 3:
        print(f"duration {duration} < 3")
        return None

    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_metadata = ydl.extract_info(f"https://www.youtube.com/watch?v={video_info['YoutubeID']}", download=False)
    except Exception as e:
        print(f"Error getting video info for {video_info['YoutubeID']}: {e}")
        return None

    video_category = video_metadata.get("categories", ["Unknown"])[0]
    if video_category not in ["Entertainment", "Howto & Style", "Nonprofits & Activism-christ",
                              "Travel & Events"]:
        print(f"class {video_category} no need-----------------")
        return None
    print(video_category)
    video_width = video_metadata['width']
    video_height = video_metadata['height']
    video_duration = timedelta(seconds=video_metadata['duration'])
    video_title = video_metadata['title']

    processed_info = {
        "title": video_title,
        "video_id": video_info['YoutubeID'],
        "category": video_category,
        "width": video_width,
        "height": video_height,
        "duration": round(video_duration.total_seconds(), 4),
        "aesthetic_score": round(float(video_info['Aesthetic_Score']), 4),
        "clip_score": round(float(video_info['CLIP_Score']), 4),
        "caption": video_info['Caption'],
        "start_timestamp": start_timestamp,
        "end_timestamp": end_timestamp
    }

    return processed_info

with open(input_jsonl_path, "r") as input_file:
    video_infos = [json.loads(line) for line in input_file]
print("load json ok")

category_counts = {}
category_files = {}
total_videos = len(video_infos)
progress_bar = tqdm(total=total_videos, unit="video", desc="Processing videos")

for video_info in video_infos:
    processed_info = process_video_info(video_info)
    if processed_info:
        category = processed_info["category"]
        output_file_path = os.path.join(output_jsonl_dir, f"InternVid-18M-aes-{category}.jsonl")
        if not os.path.exists(output_file_path) or video_info['YoutubeID'] not in [json.loads(line)['video_id'] for line
                                                                                   in open(output_file_path, 'r')]:
            with open(output_file_path, "a") as category_file:
                category_file.write(json.dumps(processed_info) + "\n")
                category_counts[category] = category_counts.get(category, 0) + 1
    progress_bar.update(1)

progress_bar.close()

for output_file in category_files.values():
    output_file.close()

print("total:")
for category, count in category_counts.items():
    print(f"{category}: {count}")

