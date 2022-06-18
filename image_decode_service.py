

import b64_string

def decode(image_path):

    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read())
    return b64_string
