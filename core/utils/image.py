from PIL import Image, ExifTags
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import imghdr, time

class Compressor:

    @classmethod
    def compress(cls,_image):
        image_format = imghdr.what(_image).upper()
        image = Image.open(_image)
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        except:
            pass

        width, height = image.size
        portrait = width < height
        if not portrait:
            base_width = 680
            if width > base_width:
                width_percent = (base_width/float(width))
                new_height = int((float(height)*float(width_percent)))
                image = image.resize((base_width,new_height),Image.HAMMING)
        else:
            base_heigth = 680
            if height > base_heigth:
                height_percent = (base_heigth/float(height))
                new_width = int((float(width)*float(height_percent)))
                image = image.resize((new_width,base_heigth),Image.HAMMING)
        # width, height after processing
        width, height = image.size

        ret_image = BytesIO()
        image.save(ret_image,format=image_format, quality=80, optimize=True)
        ret_image.seek(0)

        return ret_image,width,height,portrait
