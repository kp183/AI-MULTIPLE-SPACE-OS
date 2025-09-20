# core/biometric_auth.py

from PIL import Image
import io

def get_image_hash(image_bytes):
    """
    Generates a perceptual hash for an image.
    
    Args:
        image_bytes: The image file in bytes (from st.camera_input).

    Returns:
        A 64-character hash string.
    """
    if image_bytes is None:
        return None
    
    # Open the image using Pillow
    image = Image.open(io.BytesIO(image_bytes))
    
    # 1. Convert to grayscale
    grayscale_image = image.convert("L")
    
    # 2. Resize to a tiny 9x8 image
    resized_image = grayscale_image.resize((9, 8), Image.Resampling.LANCZOS)
    
    # 3. Calculate the difference hash
    hash_string = ""
    pixels = list(resized_image.getdata())
    
    for row in range(8):
        for col in range(8):
            left_pixel = pixels[row * 9 + col]
            right_pixel = pixels[row * 9 + col + 1]
            if left_pixel > right_pixel:
                hash_string += "1"
            else:
                hash_string += "0"
                
    return hash_string

def compare_hashes(hash1, hash2):
    """
    Compares two image hashes and returns the similarity score.
    
    Args:
        hash1: The first hash string.
        hash2: The second hash string.

    Returns:
        An integer representing the number of different bits (Hamming distance).
        A lower number means more similar.
    """
    if not hash1 or not hash2 or len(hash1) != len(hash2):
        return -1 # Indicate an error

    # Calculate the Hamming distance
    distance = sum(bit1 != bit2 for bit1, bit2 in zip(hash1, hash2))
    return distance