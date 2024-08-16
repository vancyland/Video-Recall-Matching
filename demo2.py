
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

# scenes = [
# "The Ritual (keywords: earth-toned garments, tumultuous sky, ritualistic blessing)",
# "The Wanderer (keywords: tattered fabrics, piercing blue eyes, fatigue, determination, sorrow)",
# "The Warrior (keywords: sleek bodysuit, metallic rods, cloud of dust, combat)",
# "The Companion (keywords: olive fatigues, tactical vest, communication device, grim focus)",
# "The Survivors (keywords: ragtag clan, unforgiving world, endure, secrets)"
# ]

scenes = ["A lone figure in dark attire traversing the crest of a sand dune under an overcast sky, with a blurred companion in the foreground suggesting solitude and introspection.",
"A figure in an earthy robe sitting in contemplation against a desert backdrop, with faint scars and silhouetted companions hinting at a narrative of survival and anticipation.",
"A solitary individual kneeling on a vast, wind-sculpted sand dune, dwarfed by the monumental landscape and evoking a sense of serene solitude.",
"An individual shrouded in textured fabric, revealing only piercing blue eyes, wearing a tactical vest and suggesting preparedness for a demanding outdoor scenario.",
"A night scene of a sandy beach with two elongated shadows resembling people lying side by side, casting an air of mystery and serenity."]

time = [2, 8, 9, 7, 4]

video_dir = "/home/cone/lun/cone/Data/film1/"
video_info = defaultdict(dict)
total_videos = 0
videos_with_watermark_or_subtitle = 0

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
                video_scores.append((video_id, score, info["name"], info["caption"]))
        video_scores.sort(key=lambda x: x[1], reverse=True)
        scene_video_matches=[]
        scene_video_matches.append([v for v in video_scores[:1]])
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
            video_path = os.path.join(video_dir, video_id[2])
            if -1 > time[count]:
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
                print(f"scene prompt: {scenes[count]}; Selected video: {video_id[2]}")
        except Exception as e:
            print(f"Failed to load video: {video_id}, Error: {e}")
            for video_score in scene_video_matches[0]:
                try:
                    video_path = os.path.join(video_dir, video_score[3])
                    if -1 > time[count]:
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

video_info = {}

with open('./video_captions1.txt', 'r') as file:
    lines = file.readlines()
    for i in range(0, len(lines)-3, 3):
        file_name = lines[i].strip()
        caption = lines[i+1].strip()
        video_info[i//3] = {
            'name': file_name,
            'caption': caption
        }

print(video_info)

selected_videos, f_clip = match_scene_to_video(scenes, video_info)

output_path = os.path.join(output_dir, f"video_long_12.webm")
create_one_click_video(selected_videos, f_clip, scenes, output_path)
