# Image Watermarking Script

This Python script adds a watermark to all `.jpg`, `.png`, and `.jpeg` images in the `images/` directory and saves the processed images in the `watermarked/` directory.

## Features

- Resizes images to a width of `1024px` while maintaining the aspect ratio.
- Adds an orange watermark with the text `"NexEd"` in the bottom-right corner.
- Automatically processes all images in the `images/` folder.

## Requirements

Make sure you have Python and the required libraries installed:

```sh
pip install pillow
```

## Usage

1. Place the images you want to watermark inside the `images/` directory.
2. Run the script:

   ```sh
   python script.py
   ```

3. Watermarked images will be saved in the `watermarked/` directory with the prefix `wm_`.

## Customization

- Change the watermark text by modifying the `watermark_text` variable inside `add_watermark()`.
- Adjust font size and color as needed.

## License

This script is available under the MIT License.
