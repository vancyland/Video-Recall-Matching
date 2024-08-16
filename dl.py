
import os
import json
import concurrent.futures
from tqdm import tqdm
import yt_dlp
import subprocess

jsonl_dir = "/home/cone/team/user/Cone/DATA/jsonl/"

# output_dir = "/home/cone/team/user/Cone/DATA/18M-aes-Videos-class/"
output_dir = "/home/cone/lun/cone/Data/18M-aes-Videos-class"
os.makedirs(output_dir, exist_ok=True)
output = "/home/cone/lun/cone/Data/"
os.makedirs(output, exist_ok=True)

downloaded_video_ids = set()

if os.path.exists(os.path.join(output, "downloaded_video_ids.txt")):
    with open(os.path.join(output, "downloaded_video_ids.txt"), "r") as f:
        downloaded_video_ids = set(line.strip() for line in f)

from datetime import datetime, timedelta
def convert_timestamp_to_seconds(timestamp_str):
    try:
        timestamp = datetime.strptime(timestamp_str, "%H:%M:%S.%f")
        return timestamp.second + timestamp.minute * 60 + timestamp.hour * 3600
    except ValueError:
        print(f"error: {timestamp_str}")
        return None

def download_video_segment(video_info):
    try:
        video_id = video_info["video_id"]
        if video_id in downloaded_video_ids:
            print(f"Video {video_id} already downloaded")
            return
        start_seconds = convert_timestamp_to_seconds(video_info["start_timestamp"])
        end_seconds = convert_timestamp_to_seconds(video_info["end_timestamp"])
        if start_seconds is None or end_seconds is None:
            print("start_time or end time is None")
            return

        duration = end_seconds - start_seconds
        fileout=os.path.join(output_dir, f"{video_info['category']}-{video_info['caption']}-{duration}-{video_info['height']}-{video_info['aesthetic_score']}-{video_info['clip_score']}-{video_id}")
        try:

            ydl_opts = {
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'restrictfilenames': True,  
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                filename = ydl.prepare_filename(info)  
                print(f"Downloading {filename}.......................................")
                input_file = os.path.join(output_dir, filename)
                print(f"input_file: {input_file}")
                file_extension = os.path.splitext(input_file)[1]
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

            print("begin cut-----------------------------------------------")
            output_file = os.path.join(output_dir,
                                       f"{video_info['category']}-{video_info['caption']}-{duration}-{video_info['height']}-{video_info['aesthetic_score']}-{video_info['clip_score']}-{video_id}{file_extension}")
            subprocess.run([
                "ffmpeg",
                "-i", input_file,
                "-ss", video_info["start_timestamp"],
                "-to", video_info["end_timestamp"],
                "-c", "copy",
                output_file
            ], check=True)

            os.remove(input_file)
            downloaded_video_ids.add(video_id)
            print("remove over")
            # import time
            # time.sleep(0.1)

        except Exception as e:
            print(f"Error downloading video {video_id}: {e}")
    except KeyError as e:
        print(f"Skipping video {video_info['video_id']} due to missing field: {e}")
        return

def main():
    max_workers = 8 
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=0, unit="video",
                                                                                          desc="Downloading videos") as download_progress_bar:
    # with concurrent.futures.ThreadPoolExecutor() as executor, tqdm(total=0, unit="video", desc="Downloading videos") as download_progress_bar:
        futures = []
        for jsonl_file in os.listdir(jsonl_dir):
            # if jsonl_file == "InternVid-18M-aes-Travel & Events.jsonl":
                jsonl_path = os.path.join(jsonl_dir, jsonl_file)
                try:
                    with open(jsonl_path, "r") as f:
                        video_infos = [json.loads(line) for line in f]
                except json.JSONDecodeError:
                    print(f"Skipping {jsonl_file} due to JSON format error")
                    continue

                for video_info in video_infos:
                    video_id = video_info["video_id"]
                    if video_id not in downloaded_video_ids:
                        futures.append(executor.submit(download_video_segment, video_info))
                        download_progress_bar.update(1)

    with open(os.path.join(output, "downloaded_video_ids.txt"), "w") as f:
        f.write("\n".join(downloaded_video_ids))

if __name__ == "__main__":
    main()
