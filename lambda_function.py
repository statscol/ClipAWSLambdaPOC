from PIL import Image
import requests
import json
from transformers import CLIPProcessor, CLIPModel
import torch
import os

model = CLIPModel.from_pretrained(os.environ.get("HF_MODEL_NAME","openai/clip-vit-base-patch16"),cache_dir="/tmp/")
processor = CLIPProcessor.from_pretrained(os.environ.get("HF_MODEL_NAME","openai/clip-vit-base-patch16"),cache_dir="/tmp/")

def handler(event, context):
    try:
        input_text=event.get("text_list")
        image=Image.open(requests.get(event.get("image_url"),stream=True).raw)
        inputs = processor(text=input_text, images=image, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            logits_per_image = outputs.logits_per_image  # this is the image-text similarity score

        probs = logits_per_image.softmax(dim=1)
        pred=probs.argmax(-1).item()
        return json.dumps({'code':200,'prediction':input_text[pred],'confidence':probs.squeeze()[pred].item()})
    except Exception as e:
        return json.dumps({'code':400,'details':f'{e}'})



