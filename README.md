# Video-Recall-Matching

This code implements an automated video matching and editing functionality. It can intelligently select relevant video clips from a video library based on the given scene descriptions, and generate a complete video work.

json.py首先提取json文件中的视频地址，获取对应视频的各种信息，包括分辨率时长等，并按类别保存成新的信息更完整的json文件
dl.py是在根据json文件下载对应视频，，在命名的时候就包含了大量视频相关信息。
caption_glm-4.py以视频第一帧和粗略caption作为输入，调用多模态大模型https://github.com/THUDM/GLM-4,来完成视频精确理解。


To run the demo, execute the following command in your terminal:

```bash
python demo2.py
