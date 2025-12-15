import os
import base64
import re
from PIL import Image
import io

# Configuration: Map standard image filenames to the HTML variable names
# keys: file names to look for in the current directory
# values: the JS variable name in ahe_presentation.html
IMAGE_MAPPING = {
    'insert_1.png': 'img0',
    'insert_2.png': 'img1',
    'insert_3.png': 'img2'
}

HTML_FILE = 'ahe_presentation.html'

def encode_image(filepath):
    """
    Reads an image, converts it to WebP for optimization, 
    and returns the base64 string.
    """
    try:
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found. Skipping.")
            return None
            
        # Open source image
        with Image.open(filepath) as img:
            # Keep transparency if present
            # if img.mode in ('RGBA', 'LA'):
            #     background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
            #     background.paste(img, img.split()[-1])
            #     img = background
            
            # Save as WebP to bytes buffer
            output = io.BytesIO()
            img.save(output, format='WEBP', quality=80) # Adjustable quality
            
            # Encode
            b64_data = base64.b64encode(output.getvalue()).decode('utf-8')
            return f"data:image/webp;base64,{b64_data}"
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def update_html(replacements):
    """
    Replaces the specific const definitions in the HTML file.
    """
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for var_name, b64_str in replacements.items():
            if not b64_str:
                continue
                
            # Regex to find: const img0 = "..."
            # We look for the variable assignment and the string until the next quote/semicolon
            pattern = re.compile(rf'(const\s+{var_name}\s*=\s*")([^"]+)(";)')
            
            # Check if variable exists
            if not pattern.search(new_content):
                print(f"Warning: Could not find variable '{var_name}' in HTML.")
                continue
                
            # Replace
            new_content = pattern.sub(rf'\1{b64_str}\3', new_content)
            print(f"Updated {var_name}")

        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully updated {HTML_FILE}")
        
    except FileNotFoundError:
        print(f"Error: {HTML_FILE} not found.")
    except Exception as e:
        print(f"Error updating HTML: {e}")

def main():
    print("Starting slide update...")
    
    replacements = {}
    for filename, var_name in IMAGE_MAPPING.items():
        print(f"Processing {filename}...")
        b64_str = encode_image(filename)
        if b64_str:
            replacements[var_name] = b64_str
            
    if replacements:
        update_html(replacements)
    else:
        print("No images found to update.")

if __name__ == "__main__":
    main()
