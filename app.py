from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import base64
import io


app = Flask(__name__)

def get_image_format(header_bytes):
    if header_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'PNG'
    elif header_bytes.startswith(b'\xff\xd8\xff'):
        return 'JPEG'
    elif header_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return 'GIF'
    else:
        return 'Unknown'

@app.route('/convert_to_3d', methods=['POST'])
def convert_to_3d():
    try:
        # Get the uploaded image
        uploaded_file = request.files['image']
        image_data = uploaded_file.read()  # Read the image data as bytes

        # Check the image format based on the header bytes
        image_format = get_image_format(image_data[:10])  # Check the first 10 bytes

        if image_format == 'Unknown':
            return jsonify({'result': 'error', 'message': 'Unknown image format'})

        # Create a PIL Image from the image data
        image = Image.open(io.BytesIO(image_data))

        # Perform 3D-like effect by displacing pixels horizontally
        displacement = 20000  # Adjust this value for the desired depth effect
        image_np = np.array(image)
        shifted_image = np.roll(image_np, displacement, axis=2)

        # Convert the shifted image to PIL Image
        shifted_image_pil = Image.fromarray(shifted_image)

        # Convert the image to JPEG format (you can also use 'PNG' for PNG format)
        output_buffer = io.BytesIO()
        shifted_image_pil.save(output_buffer, format='JPEG')  # Change 'JPEG' to 'PNG' for PNG format
        shifted_image_jpeg = output_buffer.getvalue()

        # Encode the converted image as base64
        shifted_image_base64 = base64.b64encode(shifted_image_jpeg).decode('utf-8')

        # Get the dimensions of the image
        image_width, image_height = image.size
    # Debug print statement
        print(f"First 10 bytes of image data: {image_data[:10]}")

        # Return the 3D-like image in JPEG format as base64 and its dimensions as a response
        return jsonify({'result': 'success', 'image': shifted_image_base64, 'dimensions': {'width': image_width, 'height': image_height}})
    except Exception as e:
        return jsonify({'result': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
