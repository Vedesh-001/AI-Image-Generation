import torch
from diffusers import StableDiffusionPipeline
import os
from torchvision import transforms
from PIL import Image

# Load the model
api_key = "sk-nHsQZuQdOomj8L5wTU2JkoQZqZ0btUx1Lp7F6t6klNBQdbxx"  
model_id = "CompVis/stable-diffusion-v1-4"

pipe = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=api_key)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe.to(device)

def generate_images(prompt, num_images, style=None):
    output = pipe(prompt, num_inference_steps=50, guidance_scale=7.5)
    images = output["images"] if "images" in output else output["sample"]

    image_paths = []
    os.makedirs("static", exist_ok=True)

    for i, img in enumerate(images[:num_images]):
        img_path = f"static/generated_image_{i+1}.png"
        img.save(img_path)
        if style and style != "none":
            img_path = apply_style(img_path, style)
        image_paths.append(img_path)
    
    return image_paths

def apply_style(image_path, style):
    styles = {"vangogh": "models/vangogh_model.pth", "picasso": "models/picasso_model.pth"}
    if style not in styles or not os.path.exists(styles[style]):
        return image_path
    
    model = torch.load(styles[style], map_location=device)
    model.eval()
    
    image = Image.open(image_path)
    transform = transforms.Compose([transforms.Resize((256, 256)), transforms.ToTensor()])
    image = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        stylized_image = model(image).cpu()
    
    output_path = image_path.replace(".png", f"_{style}.png")
    transforms.ToPILImage()(stylized_image.squeeze()).save(output_path)
    return output_path
