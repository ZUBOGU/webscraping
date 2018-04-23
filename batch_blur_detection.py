#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import cv2
import numpy

def find_images(input_dir):
    extensions = [".jpg", ".png", ".jpeg"]
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if os.path.splitext(file)[1].lower() in extensions:
                yield os.path.join(root, file)

def fix_image_size(image, expected_pixels=2E6):
    ratio = numpy.sqrt(float(expected_pixels) / float(image.shape[0] * image.shape[1]))
    return cv2.resize(image, (0, 0), fx=ratio, fy=ratio)

def estimate_blur(image, threshold):
    Laplacian = cv2.Laplacian(image, ddepth=cv2.CV_64F)
    score = Laplacian.var()
    std = Laplacian.std()
    mean = Laplacian.mean()
    return score, std, mean, bool(score < threshold)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='run blur detection on a single image')
    parser.add_argument('-i', '--input_dirs', nargs='+', dest="input_dirs", type=str, required=True, help="directory of images")
    args = parser.parse_args()
    for input_dir in args.input_dirs:
        for input_path in find_images(input_dir):
            try:
                input_image = cv2.imread(input_path)
                if input_image.ndim == 3:
                    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
                input_image = fix_image_size(input_image)
                print(input_image.shape)

                score, std, mean, blurry = estimate_blur(input_image, 36)
                print("input path: {4}, score: {0}, std: {1}, mean: {2}, blurry: {3}".format(score, std, mean, blurry, input_path))
            except Exception as e:
                print(e)
                pass