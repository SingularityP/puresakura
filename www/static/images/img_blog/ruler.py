from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os,logging
logging.basicConfig(level=logging.DEBUG)

def zoom(img_path, img_name, box):
    logging.debug("[RULER] Open image file at : " + os.path.join(img_path, img_name))
    img = Image.open(os.path.join(img_path, img_name))
    img.thumbnail(box)
    try:
        img.save(os.path.join(img_path, 'imgS_' + img_name))
    except OSError as e:
        logging.warn('[RULER] Image error : ' + os.path.join(img_path, 'imgS_' + img_name))
        print(e)

if __name__ == '__main__':
    path = os.path.split(os.path.realpath(__file__))[0]
    for i in [x for x in os.listdir(path) if os.path.isfile(x) and os.path.splitext(x)[1] in ('.jpg', '.png', '.gif')]:
        zoom(path, i, (192, 108))