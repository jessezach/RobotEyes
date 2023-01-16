import os
import shutil

from PIL import Image


class Utils(object):
    @staticmethod
    def cleanup_files(file_paths=[]):
        for path in file_paths:
            if os.path.exists(path):
                shutil.rmtree(path)

    @staticmethod
    def fix_base_img_size_if_needed(base_image, actual_image):
        if os.path.exists(base_image):
            im = Image.open(actual_image)
            width, height = im.size
            im.close()

            im = Image.open(base_image)
            b_width, b_height = im.size
            if width != b_width or height != b_height:
                im = im.resize((width, height), Image.ANTIALIAS)
                im.save(base_image)
