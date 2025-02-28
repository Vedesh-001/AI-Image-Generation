import os
from rembg import remove
from PIL import Image
import cv2
import numpy as np

def remove_background(input_path):
    """Removes background from an image and saves it as a transparent PNG."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    try:
        with Image.open(input_path).convert("RGBA") as input_image:
            output_image = remove(input_image)
            output_path = os.path.splitext(input_path)[0] + "_no_bg.png"
            output_image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Error removing background: {e}")
        return input_path  # Return original image path in case of failure

def enhance_image(image_path):
    """Enhances image resolution using OpenCV upscaling."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    try:
        image = cv2.imread(image_path)
        upscaled = cv2.resize(image, (image.shape[1] * 2, image.shape[0] * 2), interpolation=cv2.INTER_LANCZOS4)
        enhanced_path = image_path.replace(".png", "_enhanced.png")
        cv2.imwrite(enhanced_path, upscaled)
        return enhanced_path
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return image_path  # Return original if enhancement fails

def replace_background(input_path, bg_path):
    """Replaces background with a new image."""
    if not os.path.exists(input_path) or not os.path.exists(bg_path):
        raise FileNotFoundError("One or more input files do not exist.")

    try:
        with Image.open(input_path).convert("RGBA") as input_image, Image.open(bg_path).convert("RGBA") as bg_image:
            bg_image = bg_image.resize(input_image.size)
            bg_image.paste(input_image, (0, 0), input_image)

            final_path = input_path.replace(".png", "_with_bg.png")
            bg_image.save(final_path, "PNG")
        return final_path
    except Exception as e:
        print(f"Error replacing background: {e}")
        return input_path  # Return original in case of failure
