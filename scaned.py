import cv2  # required install
import string
import random
import os
import time
import progressbar  # required install
import pytesseract  # required install
from pytesseract import Output  # required install
from googletrans import Translator  # required install
from PIL import ImageFont, ImageDraw, Image  # required install
import numpy as np
from pdf2image import convert_from_path  # required installv
from fpdf import FPDF  # required install
from langdetect import detect_langs

def detect_add_text(str = '') :
    try:
        detect_langs(ele['text'])
        textl = translator.translate(textl, dest='vi').text
    except:
        textl = str
    return str
def list_to_text(listt = []):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in listt:
        print(detect_langs(ele['text']))
        str1 = str1 + '' + ele['text']

    # return string
    return str1

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
font = ImageFont.truetype(fontpath, 13)

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

    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='jpn+eng', config='--tessdata-dir ./tessdata')
    # print(d)

    n_boxes = len(d['text'])
    # font = cv2.FONT_HERSHEY_SIMPLEX
    translator = Translator()

    # result = translator.translate('http://mrsinvoice.com', dest='vi')
    text_group = []
    texts_block = {}
    j = 0
    for i in range(n_boxes):
        data_i = {'conf': d['conf'][i], 'level': d['level'][i], 'text': d['text'][i], 'left': d['left'][i], 'top': d['top'][i], 'width': d['width'][i], 'height': d['height'][i]}
        if int(d['conf'][i]) > 60:
            if i < n_boxes - 1 and int(d['level'][i]) == int(d['level'][i + 1]):
                text_group.append(data_i)
            elif i < n_boxes - 1 and int(d['level'][i]) != int(d['level'][i + 1]):
                text_group.append(data_i)
                texts_block[j] = text_group
                j += 1
                text_group = []
            elif i == n_boxes - 1 and int(d['level'][i]) == int(d['level'][i - 1]):
                text_group.append(data_i)
                texts_block[j] = text_group
            elif i == n_boxes - 1 and int(d['level'][i]) != int(d['level'][i - 1]):
                text_group.append(data_i)
                texts_block[j] = text_group

    len_t_block = len(texts_block)

    for m in range(len_t_block):
        # get cor and width of text and draw rectangle
        x = texts_block[m][0]['left']
        y = texts_block[m][0]['top']
        w = texts_block[m][len(texts_block[m]) - 1]['left'] + texts_block[m][len(texts_block[m]) - 1]['width']
        h = texts_block[m][len(texts_block[m]) - 1]['top'] + texts_block[m][len(texts_block[m]) - 1]['height']
        # (x, y, w, h) = (texts_block[m][0]['left'], texts_block[m][0]['top'], texts_block[m][len(texts_block[m]) - 1]['width'], texts_block[m][len(texts_block[m]) - 1]['height'])
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # tap tick on pdf
        im_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(im_pil)
        # Translate text to vietnamese
        text_from_list = list_to_text(texts_block[m])
        textTrans = trans_text(text_from_list)
        print(textTrans)

        # img = cv2.putText(img, textTrans, (x, y + h), font, 0.5, (0, 0, 252), 1, cv2.LINE_AA)
        draw.text((x, y), textTrans, font=font, fill=(255, 0, 0, 255))
        img = np.array(im_pil)
        # update progress bar
        bar.update(k + (m / n_boxes))
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
