''' MRVC/H.py '''

import numpy as np
import DWT
import cv2
import colors

def read(prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    H = []
    sb = 0
    for sbn in subband_names:
        fn = f"{prefix}{sbn}{ASCII_frame_number}.png"
        subband = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
        try:
            subband = cv2.cvtColor(subband, cv2.COLOR_BGR2RGB)
        except cv2.error:
            print(colors.red(f'H.read: Unable to read "{fn}"'))
        subband = np.array(subband, dtype=np.float64) # Ojo, quizás se pueda cambiar a np.int16
        subband -= 32768.0
        H.append(subband)
    return H # [LH, HL, HH], each one [rows, columns, components]

def write(H, prefix, frame_number):
    ASCII_frame_number = str(frame_number).zfill(3)
    subband_names = ["LH", "HL", "HH"]
    sb = 0
    for sbn in subband_names:
        subband = np.array(H[sb], dtype=np.float64) # Ojo, quizás se puede quitar
        #subband = H[i].astype(np.float32)
        subband += 32768.0
        subband = subband.astype(np.uint16)
        fn = f"{prefix}{sbn}{ASCII_frame_number}.png"
        print(subband.shape, fn)
        subband = cv2.cvtColor(subband, cv2.COLOR_RGB2BGR)
        cv2.imwrite(fn, subband)
        sb += 1

def interpolate(H):
    LL = np.zeros(shape=(H[0].shape), dtype=np.float64)
    _H_ = DWT.synthesize_step(LL, H)
    return _H_

def reduce(_H_):
    _, H = DWT.analyze_step(_H_)
    return H
