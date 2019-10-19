from PIL import Image


def velocity_ocr(image, coords, f1app):
    """
    # Good example of image enhancement before recognition
    """
    # crop and convert image to greyscale
    img = Image.fromarray(image).crop(coords).convert('L')
    img = img.resize([img.width * 2, img.height * 2])

    if f1app:
        # filters for video from the f1 app
        img = ImageEnhance.Brightness(img).enhance(3.0)
        img = ImageEnhance.Contrast(img).enhance(2.0)
    else:
        # filters for onboard video graphic
        img = ImageEnhance.Brightness(img).enhance(0.1)
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = ImageEnhance.Contrast(img).enhance(4.0)
        img = ImageEnhance.Brightness(img).enhance(0.2)
        img = ImageEnhance.Contrast(img).enhance(16.0)

    try:
        # vel = pytesseract.image_to_string(img,config='digits')
        vel = pytesseract.image_to_string(img)
    except UnicodeDecodeError:
        vel = -1

    return vel