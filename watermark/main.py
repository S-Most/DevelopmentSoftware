import os
from PIL import Image, ImageDraw, ImageFont

def add_watermark(input_image_path, output_image_path, watermark_text="NexEd"):
    original_image = Image.open(input_image_path)

    width = 1024
    height = int((width / original_image.width) * original_image.height)
    resized_image = original_image.resize((width, height))

    draw = ImageDraw.Draw(resized_image)

    font = ImageFont.load_default(80)

    text_width= draw.textlength(watermark_text, font=font)
    text_height = draw.textbbox((0, 0), watermark_text, font=font)[3]

    x = resized_image.width - text_width - 30
    y = resized_image.height - text_height - 30

    draw.text((x, y), watermark_text, fill="orange", font=font)

    resized_image.save(output_image_path)
    print(f"Watermarked image saved as {output_image_path}")

if __name__ == "__main__":

    for file in os.listdir("images"):
        if file.endswith(".jpg")  or file.endswith(".png") or file.endswith(".jpeg"):
            input_path = os.path.join("images", file)
            output_path = os.path.join("watermarked", f"wm_{file}")
            add_watermark(input_path, output_path)
