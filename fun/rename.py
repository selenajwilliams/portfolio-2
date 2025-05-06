## this will rename the images in the local assest folder such that
## the oldest image is 1.<ext>, 2.<ext> etc.
## and updates their file type to be .png

import os
from PIL import Image, ExifTags
import pyheif
from datetime import datetime

ASSETS_FOLDER = 'assets'

def get_date_taken(path):
    try:
        if path.lower().endswith(('.jpg', '.jpeg')):
            image = Image.open(path)
            exif_data = image._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    if ExifTags.TAGS.get(tag) == 'DateTimeOriginal':
                        return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    return datetime.fromtimestamp(os.path.getmtime(path))

def process_heic_image(heic_path):
    try:
        heif_file = pyheif.read(heic_path)
        image = Image.frombytes(
            heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride
        )
        return image
    except Exception as e:
        print(f"Failed to process HEIC file {heic_path}: {e}")
        return None

def rename_and_convert_to_png_fast(folder):
    supported_extensions = ('.jpg', '.jpeg', '.heic', '.png', '.gif', '.bmp', '.tiff')
    files = [f for f in os.listdir(folder) if f.lower().endswith(supported_extensions)]

    dated_files = []
    for file in files:
        full_path = os.path.join(folder, file)
        date_taken = get_date_taken(full_path)
        dated_files.append((file, date_taken))

    dated_files.sort(key=lambda x: x[1])

    for i, (original_file, _) in enumerate(dated_files, 1):
        old_path = os.path.join(folder, original_file)
        new_path = os.path.join(folder, f"{i}.png")

        try:
            if original_file.lower().endswith('.heic'):
                img = process_heic_image(old_path)
            else:
                img = Image.open(old_path)

            if img:
                img = img.convert('RGB')  # Convert to RGB for PNG output
                img.save(new_path, format='PNG', optimize=True)
                os.remove(old_path)  # Remove the original file
                print(f"Processed {original_file} → {i}.png")
        except Exception as e:
            print(f"Error processing {original_file}: {e}")

if __name__ == "__main__":
    rename_and_convert_to_png_fast(ASSETS_FOLDER)
