# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:36:11 2020

@author: Timothe
"""

import scipy.misc
import imageio
import numpy as np
from skimage.draw import line_aa

def Empty_img(X,Y):

    img = np.zeros((X, Y), dtype=np.uint8)
    rr, cc, val = line_aa(0, 0, X-1, Y-1)
    img[rr, cc] = val * 255
    rr, cc, val = line_aa(0, Y-1, X-1, 0)
    img[rr, cc] = val * 255

    return img

if __name__ == "__main__":
    img = Empty_img(500,800)
    imageio.imwrite("out.png", img)