# Video-Recall-Matching

This code implements an automated video matching and editing functionality. It can intelligently select relevant video clips from a video library based on the given scene descriptions, and generate a complete video work.

`json.py` first extracts the video addresses from the JSON file, and retrieves the corresponding video information, including resolution, duration, etc., and saves them as a new JSON file with more complete information, organized by category.

`dl.py` downloads the corresponding videos based on the JSON file. The filenames include a lot of video-related information.

`caption_glm-4.py` uses the first frame of the video and a rough caption as input, and calls the multi-modal large model https://github.com/THUDM/GLM-4 to complete the precise understanding of the video.

Finally, `demo1.py` and `demo2.py` recall and match the video clips based on the keyword input, and then assemble them into a complete video.

## Quick Start

```bash
python demo2.py
