import argparse
import mmcv
from flask import Flask, request, Blueprint, render_template, flash, Response
from werkzeug.utils import secure_filename
import base64
import os
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import numpy
 
parser = argparse.ArgumentParser()
parser.add_argument('--model', required=False)

# default model from cheng
# detection model
from mmdet.apis import init_detector
from mmdet.apis import inference_detector as predict
config_file = './configs/railway.py'
weight_file = './weights/railway-epoch12.pth'
model = init_detector(config_file, weight_file, device='cuda:0')


class_names = ['hammar', 'scissors', 'knife', 'bottle', 'battery', 'firecracker', 'gun', 'grenade', 'bullet', 'lighter', 'ppball', 'baton']
class_chinese = ['锤', '剪刀', '刀', '瓶子', '电池', '烟花', '枪', '手雷', '子弹', '打火机', '乒乓球', '甩棍']
#results = inference_detector(model, 'cur.jpg')


def cv2ImgAddText(img, text, left, top, textColor=(0, 0, 0), textSize=20):
    if (isinstance(img, numpy.ndarray)):  #判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        "fonts/simhei.ttf", textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


def parse_result(results):
    boxes = []
    for class_index, result in enumerate(results):
        if len(result) == 0:
            continue
        class_name = class_chinese[class_index]
        for bounding_box in result:
            xmin, ymin, xmax, ymax, score = bounding_box
            boxes.append([class_name, score, [xmin, ymin, xmax, ymax]])
    return boxes


def detect(src):
    # src either is img_path or numpy format img
    results = predict(model, src)
    results = parse_result(results)
    return results

if __name__ == '__main__':
    pass
