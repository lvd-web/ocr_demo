import cv2  # required install
import string
import random
import time
import progressbar  # required install
import pytesseract  # required install
from pytesseract import Output  # required install
from googletrans import Translator  # required install
from PIL import ImageFont, ImageDraw, Image  # required install
import numpy as np
from pdf2image import convert_from_path  # required installv
from fpdf import FPDF  # required install


# Translate text
def trans_text(textl=''):
    try:
        textl = translator.translate(textl, dest='vi').text
    except:
        textl = textl
    return textl


# Generate random name file
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# Declare pdf file to save
pdf = FPDF()
pdf.set_auto_page_break(0)

# input file
filePath = 'sample.pdf'
# set font translated
fontpath = "./font/SVN-Arial Regular.ttf"
font = ImageFont.truetype(fontpath)

# export pdf to image
docs = convert_from_path(filePath)
image_counter = 1
for page in docs:
    filename1 = "Page_no_" + str(image_counter) + " .jpg"
    page.save('./output_tmp_extract/' + filename1, 'JPEG')
    image_counter += 1

# Show process bar
bar = progressbar.ProgressBar(maxval=image_counter,
                              widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()

for k in range(1, image_counter):
    img = cv2.imread("./output_tmp_extract/Page_no_" + str(k) + " .jpg")

    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    # print(d.keys())

    n_boxes = len(d['text'])
    # font = cv2.FONT_HERSHEY_SIMPLEX
    translator = Translator()

    # result = translator.translate('http://mrsinvoice.com', dest='vi')
    test = []

    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            # get cor and width of text and draw rectangle
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            im_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(im_pil)
            # Translate text to vietnamese
            textTrans = trans_text(d['text'][i])
            # img = cv2.putText(img, textTrans, (x, y + h), font, 0.5, (0, 0, 252), 1, cv2.LINE_AA)
            draw.text((x, y + h), textTrans, font=font, fill=(255, 0, 0, 255))
            img = np.array(im_pil)
            # update progress bar
            bar.update(k + (i / n_boxes))
    # add image to pdf
    cv2.imwrite(f'./output_tmp_extract/output_{k}.jpg', img)

    # Format size pdf
    height, width, channels = img.shape
    width, height = float(width * 0.264583), float(height * 0.264583)
    # given we are working with A4 format size
    pdf_size = {'P': {'w': 210, 'h': 297}, 'L': {'w': 297, 'h': 210}}

    # get page orientation from image size
    orientation = 'P' if width < height else 'L'

    #  make sure image size is not greater than the pdf format size
    width = width if width < pdf_size[orientation]['w'] else pdf_size[orientation]['w']
    height = height if height < pdf_size[orientation]['h'] else pdf_size[orientation]['h']

    pdf.add_page(orientation=orientation)
    pdf.image(f'./output_tmp_extract/output_{k}.jpg', 0, 0, width, height)
    # cv2.imshow('img', img)

    # print(test)
    cv2.waitKey(0)

pdf.output(f"./output_final/{time.time()}_{id_generator(10)}.pdf", "F")
bar.finish()
