import json
import os

# CONFIGURATION
file = '../meal_recommender/data/recipes_group_preprocessed.json'  # Path to the JSON file
image_folder = '../data/raw/images/images'  
stays = False  # True = Only print names. False = Actually DELETE.

def clean_images():
    # 1. Get names from JSON
    try:
        with open(file, 'r', encoding="utf-8") as f:
            data = json.load(f)
            # This creates a list of all names in the "image_filename" field
            valid_names = {item['image_filename'] for item in data if 'image_filename' in item}
    except Exception as e:
        print(f"Error: Could not read JSON file. {e}")
        return

    print(f"Loaded {len(valid_names)} image names from JSON.")

    # 2. Check the folder
    if not os.path.exists(image_folder):
        print(f"Error: Folder '{image_folder}' not found.")
        return

    deleted_count = 0
    
    for filename in os.listdir(image_folder):
        #only  .jpg files
        if filename.lower().endswith(".jpg"):
            
            # Remove .jpg to compare with the string
            name_only = os.path.splitext(filename)[0]

            if name_only not in valid_names:
                file_path = os.path.join(image_folder, filename)
                
                if stays:
                    print(f"WOULD DELETE: {filename}")
                else:
                    print(f"DELETING: {filename}")
                    os.remove(file_path)
                
                deleted_count += 1

    if stays:
        print(f"\n Finished. Would have deleted {deleted_count} images.")
        print("Change stays = False to actually delete them.")
    else:
        print(f"\nFinished. Deleted {deleted_count} unused images.")

if __name__ == "__main__":
    clean_images()