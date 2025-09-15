import os
import glob
from code.config.configuration import Config


def load_device_image(target_id):
    """
    Search for the most appropriate device_image file for the given ID.
    Priority: 'angled' > 'front'

    Args:
        target_id (int): The PCS device ID to search for.

    Returns:
        str or None: Full path to the selected image, or None if not found.
    """
    # Try both device_image directory and edited_image subdirectory
    search_dirs = [
        Config.ImagePaths.DEVICE_IMAGE_DIR,
        Config.ImagePaths.EDITED_IMAGE_DIR
    ]
    
    for base_path in search_dirs:
        if not os.path.exists(base_path):
            continue
            
        search_pattern = os.path.join(base_path, f"ID{target_id}_*.png")
        matched_files = glob.glob(search_pattern)

        # First, try to find an 'angled' image
        for file_path in matched_files:
            if "angled" in os.path.basename(file_path).lower():
                return file_path

        # Then, try to find a 'front' image if 'angled' not found
        for file_path in matched_files:
            if "front" in os.path.basename(file_path).lower():
                return file_path

    # No image found in any directory
    return None


if __name__ == "__main__":
    # Example usage: Load images for PCS device IDs 1 to 20
    targeted_ids = range(1, 21)
    for target_id in targeted_ids:
        print(load_device_image(target_id=target_id))
