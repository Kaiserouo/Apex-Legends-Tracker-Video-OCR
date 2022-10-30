import cv2 as cv
import itertools, more_itertools
import pytesseract
import string
import json
import numpy as np
from collections import defaultdict, Counter
from tqdm import tqdm

class Config:
    """
        Global config, in substitution for proper argument parsing
    """

    # video path
    VIDEO = './example/example.mkv'

    # output json file path
    OUT_FILE = './example/out.json'

    # characters that OCR recognizes
    # you could add stuff like ":'-", but this may screw some normal text up
    CHARS = string.ascii_letters + string.digits + " "


def iframes(fname):
    "generators to get frames"
    cap = cv.VideoCapture(fname)
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            yield gray
    finally:
        cap.release()

def getFrameCnt(fname):
    "get total frame count from video"
    cap = cv.VideoCapture(fname)
    n_frame = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    cap.release()
    return n_frame

def applyTransferFunction(img, coords):
    """
        Apply linear transfer function to greyscale image, to make the words to show up
        more and make OCR easier
    """
    def makePiecewiseLinearTF(pts):
        # make a piecewise linear transfer function with inflection points `pts`
        # pts is List[Tuple(int_x, int_y)] and must be sorted by their x-values

        # in case pts doesn't contain edge points ((0, 0), (255, 255)).
        # note that if pts actually have edge points, this addition won't affect correctness
        pts = [(0, 0)] + pts + [(255, 255)]

        tf = [0]
        for i, j in zip(pts[:-1], pts[1:]):
            tf.pop()
            tf.extend(list(np.linspace(i[1], j[1], j[0]-i[0]+1)))
        return np.array(tf).astype(np.uint8)

    return cv.LUT(img, makePiecewiseLinearTF(coords))

def fixImage(img):
    """
        Make an image that only contains legend name and statistics blocks.
        For easier OCR.
    """
    BOX_R, BOX_C = 68-7, 344
    L_C = 587+3
    LU_R = [273, 350, 424, 500, 578, 651, 728, 805]
    NAME_R, NAME_C = (57, 836)
    return np.vstack(
        [img[NAME_R:NAME_R+BOX_R, NAME_C:NAME_C+BOX_C]] + [
            img[r+5:r+5+BOX_R, L_C:L_C+BOX_C]
            for r in LU_R
        ]
    )

def postprocessTag(tag):
    "process tags found, in case OCR recognize those wrong"
    if tag.find('Apex') > 2:
        # e.g. "Sle Apex Kills" -> "S12 Apex Kills"
        tag = tag.replace('Sl', 'S1').replace('S1e', 'S12')
    return tag

def parseNumber(number):
    "process numbers found. if not a number then return None"
    if number == 'ie':
        # sometimes "0" will be recognized as "ie"
        return 0
    if number.replace('g', '9').isnumeric():
        # sometimes "9" will be recognized as "g"
        return int(number.replace('g', '9'))
    return None

def getTagNumberPairs(ls):
    "from list of read lines, return paired (tag, number) statistics"
    result = []
    for tag, number in zip(ls, ls[1:]):
        if (number := parseNumber(number)) is None:
            continue
        result.append((postprocessTag(tag), number))
    return result

def update(d, scanned_str):
    "given OCR result, update dict."
    ls = [s.strip() for s in scanned_str.replace('\n\n', '\n').split('\n')]
    pair_ls = getTagNumberPairs(ls)
    if len(pair_ls) < 3:
        return
    for tag, num in pair_ls:
        d[ls[0]][tag].update([num])

def cleanDict(d):
    """
        Do dict cleanup and convert to proper dict object.
        - Sometimes OCR may recognize numbers wrong, so use most common ones
        - Sometimes OCR may recognize tags wrong, but only for a short time or
          some frames, so d
    """
    result = dict()
    for legend_name, legend in d.items():
        result[legend_name] = dict()
        for key, value in legend.items():
            mc = value.most_common(1)[0]
            if mc[1] < 3:
                continue
            result[legend_name][key] = mc[0]
    return result

def main():
    d = defaultdict(lambda: defaultdict(Counter))

    for img in tqdm(iframes(Config.VIDEO), total=getFrameCnt(Config.VIDEO)):
        img = fixImage(img)
        img = applyTransferFunction(img, [(0, 0), (87, 9), (182, 237), (255, 255)])
        s = pytesseract.image_to_string(img, 'eng', config=f'--psm 4 -c tessedit_char_whitelist="{Config.CHARS}"')
        update(d, s)

    result = cleanDict(d)
    print(result)
    with open(Config.OUT_FILE, 'w') as fout:
        json.dump(result, fout)

if __name__ == '__main__':
    main()