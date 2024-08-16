
import os
import json
import random
from typing import Tuple
from collections import defaultdict
from PIL import Image
import moviepy.editor as mp
import numpy as np
from IPython.display import HTML
from moviepy.editor import *
import cv2
import pytesseract
import cv2
from PIL import Image
import easyocr

def detect_subtitles_watermarks(video_file):
    # Set the region of interest for subtitle and watermark detection
    subtitle_roi = (0, 0.8, 1, 0.2)  # (x, y, width, height) relative to video frame
    watermark_roi = [(0, 0, 0.2, 0.2), (0.8, 0, 0.2, 0.2)]  # List of (x, y, width, height) relative to video frame

    cap = cv2.VideoCapture(video_file)
    ret, frame = cap.read()

    if not ret:
        print("Failed to read video frame")
        return False

    has_subtitles = False
    has_watermarks = False

    # Subtitle detection
    subtitle_x, subtitle_y, subtitle_w, subtitle_h = [int(x * cap.get(cv2.CAP_PROP_FRAME_WIDTH)) for x in subtitle_roi[:2]] + [int(x * cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) for x in subtitle_roi[2:]]
    y = subtitle_y // 8
    s = 4 * subtitle_w // 5
    subtitle_roi_frame = frame[s:, y:subtitle_y]
    reader = easyocr.Reader(['en'])
    subtitle_text = reader.readtext(Image.fromarray(subtitle_roi_frame), detail=0)
    if subtitle_text:
        has_subtitles = True

    # Watermark detection
    for roi in watermark_roi:
        watermark_x, watermark_y, watermark_w, watermark_h = [int(x * cap.get(cv2.CAP_PROP_FRAME_WIDTH)) for x in roi[:2]] + [int(x * cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) for x in roi[2:]]
        watermark_roi_frame = frame[watermark_y:watermark_y + watermark_h, watermark_x:watermark_x + watermark_w]
        reader = easyocr.Reader(['en'])
        watermark_text = reader.readtext(Image.fromarray(watermark_roi_frame), detail=0)
        if watermark_text:
            has_watermarks = True
            break

    cap.release()

    return has_subtitles or has_watermarks

# scenes = [
# "Sunlight falls on a white beach, waves lapping at the shore.",
# "A path winds through colorful trees, mountains rise in the back.",
# "Roofs and trees fill the view."
# ]
# scenes = [
# "Tranquil seaside scene - Sunlight on white sand, waves lapping the shore, people relaxing in chairs, distant seagull cries.",
# "Winding forest path - Camera panning through colorfully-dyed trees, occasional bird darting from the bushes, distant snow-capped mountains coming into view.",
# "Aerial city panorama - High-angle shot revealing the cityscape, red-tiled roofs nestled among verdant trees.",
# "Towering city landmark - Tall church steeple standing watch over the serene city.",
# "Lingering city vista - Final slow camera movement capturing the picturesque urban landscape."
# ]

scenes = [
    "Ancient architecture, Historical landmarks, Museums",
    "Narrow streets, Arches, Stone buildings, Street art",
    "Spacious squares, Sculptures",
    "Museum interiors, Art appreciation, Sculptures, Paintings, Historical artifacts",
    "Local cuisine, Traditional cooking, Restaurant interiors, Dish presentations, Food tasting",
    "Music performances, Theatrical shows, Festival celebrations"
]

scenes = [
    # Scene 1: Alex's Home
    "Alex discovers a map that leads to a hidden treasure, Alex decides to embark on an adventure to find the treasure.",

      # Scene 2: Enchanted Forest
    "Alex enters an enchanted forest with magical creatures, Alex encounters a mischievous fairy who offers guidance.",

     # Scene 3: Treacherous Mountains
    "Alex faces dangerous obstacles in the mountains, Alex meets a wise hermit who provides valuable advice.",

     # Scene 4: Guardian's Lair
    "Alex reaches the lair of a powerful guardian, Alex engages in a series of tests to prove worthiness.",

      # Scene 5: Unveiling the Treasure
    "The guardian awards Alex the key, Alex unlocks the hidden door and reveals the magnificent treasure.",

     # Scene 6: Homecoming
    "Alex returns home with the treasure, Friends and family celebrate Alex's success."
]

time = [3, 4, 5, 4, 4, 4]
video_dir = "/home/cone/team/user/Cone/DATA/18M-aes-Videos-class"
video_info = defaultdict(dict)
total_videos = 0
videos_with_watermark_or_subtitle = 0

for filename in os.listdir(video_dir):
    if filename.endswith(".mp4") or filename.endswith(".webm") or filename.endswith(".mkv"):
        total_videos += 1
        video_id = filename.split("-")[-1][:-6]
        filename_parts = filename.split("-")
        category = filename_parts[0]
        # Reconstruct the caption by joining the parts except the last 3
        caption = "-".join(filename_parts[1:-5])

        # Check if the caption is not empty
        if caption:
            is_numeric = caption[0].isdigit()
        else:
            print("caption wrong")
            pass

        if is_numeric:
            print("G")
        else:
            try:
                if len(filename_parts) >= 5:
                    duration = float(filename_parts[-5])
                    height = filename_parts[-4]

                    if int(height) < 1080:
                        print(f"height {height} < 1080")
                        pass

                    aesthetic_score = float(filename_parts[-3])
                    clip_score = float(filename_parts[-2])

                    # has_watermark, has_subtitle = detect_subtitles_watermarks(os.path.join(video_dir, filename))
                    # if has_watermark or has_subtitle:
                    #     videos_with_watermark_or_subtitle += 1
                    #     print(f"Skipping file '{filename}' due to watermark or subtitle.")
                    #     continue

                    video_info[video_id] = {
                        "title": filename,
                        "video_id": video_id,
                        "category": category,
                        "caption": caption,
                        "duration": duration,
                        "height": height,
                        "aesthetic_score": aesthetic_score,
                        "text-video_score": clip_score,
                        "filepath": filename,
                    }
            except ValueError:
                # Skip the file if the caption cannot be converted to a float
                print(f"Skipping file '{filename}' due to invalid caption.")
                pass

print(f"Total videos: {total_videos}")
print(f"Videos with watermark or subtitle: {videos_with_watermark_or_subtitle}")

# for filename in os.listdir(video_dir):
#     video_id = filename.split("-")[-1][:-6]
#     filename_parts = filename.split("-")
#     category = filename_parts[0]
#     # Reconstruct the caption by joining the parts except the last 3
#     caption = "-".join(filename_parts[1:-5])
#
#     # Check if the caption is not empty
#     is_numeric = caption[0].isdigit()
#     if is_numeric:
#         print("G")
#     else:
#         try:
#             duration = float(filename_parts[-5])
#             height = filename_parts[-4]
#             aesthetic_score = float(filename_parts[-3])
#             clip_score = float(filename_parts[-2])
#
#             video_info[video_id] = {
#                 "title": filename,
#                 "video_id": video_id,
#                 "category": category,
#                 "caption": caption,
#                 "duration": duration,
#                 "height": height,
#                 "aesthetic_score": aesthetic_score,
#                 "text-video_score": clip_score,
#                 "filepath": filename,
#             }
#         except ValueError:
#             # Skip the file if the caption cannot be converted to a float
#             print(f"Skipping file '{filename}' due to invalid caption.")
#             pass

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-mpnet-base-v2')

def match_scene_to_video(scenes, video_info) -> Tuple[str, str, str]:
    print(f"Total number of scenes: {len(scenes)}")
    matched_videos = []
    for i, scene in enumerate(scenes):
        print(f"Processing scene: {scene}")
        scene_embed = model.encode([scene])
        video_scores = []
        for video_id, info in video_info.items():
            # if info["category"] == "Entertainment" or info["category"] == "Travel & Events" or info["category"] == "Howto & Style" and info["caption"] != "":
            #     if info['duration'] < time[i]:
            #         print(f"Skipping video {video_id} with duration {info['duration']} < {time[i]}")
            #         pass
                caption_embed = model.encode([info["caption"]])
                score = np.dot(scene_embed, caption_embed[0]) / (
                            np.linalg.norm(scene_embed) * np.linalg.norm(caption_embed[0]))
                video_scores.append((video_id, score, info["duration"], info["filepath"], info["caption"]))
        video_scores.sort(key=lambda x: x[1], reverse=True)
        scene_video_matches=[]
        scene_video_matches.append([v for v in video_scores[:4]])
        # print(scene_video_matches)
        matched_videos.append((i, scene, scene_video_matches))

    selected_videos0 = []
    selected_videos = []
    count = -1
    for _, _, scene_video_matches in matched_videos:

        count = count + 1
        # for video_id in scene_video_matches:
        try:
            selected_videos0.append(random.choice(scene_video_matches[0]))
            video_id = selected_videos0[count]
            video_path = os.path.join(video_dir, video_id[3])
            if video_id[2] > time[count]:
                start = random.uniform(0, video_id[2] - time[count])
                end = start + time[count]
                # clip = mp.VideoFileClip(video_path, subclip=(start, end))
                clip = mp.VideoFileClip(video_path)
                subclip = clip.subclip(start, end)
                print(f"Clip duration: {clip.duration:.2f} seconds")
                selected_videos.append(subclip)
                print(f"scene prompt: {scenes[count]}; Selected video caption: {video_id[4]}")


            else:
                clip = mp.VideoFileClip(video_path)
                print(f"Clip duration: {clip.duration:.2f} seconds")
                selected_videos.append(clip)
                print(f"scene prompt: {scenes[count]}; Selected video: {video_id[4]}")
        except Exception as e:
            print(f"Failed to load video: {video_id}, Error: {e}")
            for video_score in scene_video_matches[0]:
                try:
                    video_path = os.path.join(video_dir, video_score[3])
                    if video_score[2] > time[count]:
                        start = random.uniform(0, video_score[2] - time[count])
                        end = start + time[count]
                        clip = mp.VideoFileClip(video_path)
                        subclip = clip.subclip(start, end)
                        print(f"Replacement caption: {video_score[4]}")
                        selected_videos.append(subclip)
                        break
                    else:
                        clip = mp.VideoFileClip(video_path)
                        # print(f"Replacement clip duration: {clip.duration:.2f} seconds")
                        print(f"Replacement caption: {video_score[4]}")
                        selected_videos.append(clip)
                        break
                except Exception as e:
                    print(f"Failed to load replacement video: {video_score}, Error: {e}")
                    continue

            continue

        if len(selected_videos) == len(scenes):
            break
        print("Concatenating video clips...")
      
        # Resize all video clips to the minimum resolution
        for i, clip in enumerate(selected_videos):
            selected_videos[i] = clip.resize(width=1920, height=1080)
        f_clip = mp.concatenate_videoclips(selected_videos)
        print(selected_videos)
      
        for i, scene in enumerate(scenes):
            final_clip = CompositeVideoClip([f_clip])

    return selected_videos, final_clip

def create_one_click_video(selected_videos, final_clip, scenes, output_path):
    print("Writing the video to file...")
    final_clip.write_videofile(output_path)
    print("Displaying the final video...")
    from IPython.display import Video
    Video(output_path, width=640)

output_dir = "/home/cone/team/user/Cone/DATA/yijianchengpian/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

selected_videos, f_clip = match_scene_to_video(scenes, video_info)

output_path = os.path.join(output_dir, f"video_long_10.webm")
create_one_click_video(selected_videos, f_clip, scenes, output_path)
