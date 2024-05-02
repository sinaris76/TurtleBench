from PIL import Image, ImageDraw, ImageFont

import os 
import cv2
import io
import base64

def watermark_image(image_path, text):
    # Open an image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Use the default font
    font_path = os.path.join('utils/Aaargh.ttf')
    font = ImageFont.truetype(font_path, size=60)

    # font = ImageFont.load_default()
    
    # Calculate text size and position
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    position = (image.width - width - 10, image.height - height - 10)
    
    # Text color
    text_color = (255, 0, 0)  # Red color
    
    # Adding text to image
    draw.text(position, text, fill=text_color, font=font)
    
    # Save the image
    image = image.convert("RGB")
    return image

# Example usage
# watermark_image("Tasks/1/image/1.png", "1")

def preprocess_and_watermark_image(image_address, text):
  watermarked_image = watermark_image(image_address, text)
  buffer = io.BytesIO()
  watermarked_image.save(buffer, format="png")
  img_byte = buffer.getvalue()
  base64_image = base64.b64encode(img_byte).decode('utf-8')
  return base64_image

def watermark_and_save(image_path, save_path, text):
  image = watermark_image(image_path, text)
  image.save(save_path + f'/{text}.jpg')
  return save_path + f'/{text}.jpg'