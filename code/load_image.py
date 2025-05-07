import os
import glob
from configuration import Config

def load_device_image(target_id):
    """
    Search for the most appropriate device_image file for the given ID.
    Priority: 'angled' > 'front'

    Args:
        target_id (int): The PCS device ID to search for.

    Returns:
        str or None: Full path to the selected image, or None if not found.
    """
    base_path = Config.ImagePaths.EDITED_IMAGE_DIR
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

    # No image found
    return None
