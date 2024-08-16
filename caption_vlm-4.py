import os
import torch
from PIL import Image
from torchvision.io import read_video
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import signal

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained("THUDM/glm-4v-9b", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    "THUDM/glm-4v-9b",
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to(device).eval()

gen_kwargs = {"max_length": 2500, "do_sample": True, "top_k": 1}

video_dir = "/home/cone/lun/cone/Data/film1/"
output_file = "video_captions1.txt"  
timeout = 60

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

with open(output_file, "a", encoding="utf-8") as f:
    video_files = [filename for filename in os.listdir(video_dir) if filename.endswith((".webm", ".mp4", ".mkv"))]
    total_files = len(video_files)
    pbar = tqdm(total=total_files, desc="Generating captions", unit="file")  
    pbar.update(0)
    for filename in video_files:
        video_path = os.path.join(video_dir, filename)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            video_tensor, _, _ = read_video(video_path)
            signal.alarm(0) 
        except TimeoutError:
            print(f"Skipping {filename} due to timeout")
            pbar.update(1)
            continue

        keyframe_indices = [0]
        keyframes = None
        if video_tensor.shape[0] < 1:
            print(f"Skipping {filename}")
            pbar.update(1) 
            continue
        else:
            kk = video_tensor[0].numpy()
            keyframes = Image.fromarray(kk)

        if keyframes is None:
            print(f" {filename} keyframes not found in {video_path}")
            pbar.update(1)  
            continue

        parts = filename.split("-")
        orig_class = parts[0]
        orig_caption = "-".join(parts[1:2])
        query = (f"Generate a more detailed caption based on the video keyframes and original caption: {orig_caption}, including information about the location, style, and era.")
        inputs = tokenizer.apply_chat_template([{"role": "user", "images": keyframes, "content": query}],
                                               add_generation_prompt=True, tokenize=True, return_tensors="pt",
                                               return_dict=True)
        inputs = inputs.to(device)
      
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            with torch.no_grad():
                outputs = model.generate(**inputs, **gen_kwargs)
                outputs = outputs[:, inputs['input_ids'].shape[1]:]
                refined_caption = tokenizer.decode(outputs[0], skip_special_tokens=True)
            signal.alarm(0) 
        except TimeoutError:
            print(f"Skipping {filename} due to timeout")
            pbar.update(1)
            continue

        result = f"{filename}\n{orig_class}\noriginal caption: {orig_caption}\nnew caption: {refined_caption}\n\n"
        print(result)
        f.write(result)
        pbar.update(1) 

    pbar.close() 
