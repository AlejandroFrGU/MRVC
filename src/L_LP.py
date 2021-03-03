''' MRVC/L.py '''

import numpy as np
import LP
import cv2 as cv
import colors
if __debug__:
    import os

MIN = -10000 #-32768
MAX = 10000 #32767
OFFSET = 32768

def read(prefix: str, frame_number: int) -> np.ndarray: # [row, column, component]
    fn = f"{prefix}LL{frame_number:03d}.png"
    subband = cv.imread(fn, cv.IMREAD_UNCHANGED)
    subband = cv.cvtColor(subband, cv.COLOR_BGR2RGB)
    if __debug__:
        print(f"L.read({prefix}, {frame_number})", subband.shape, subband.dtype, os.path.getsize(fn))
    subband = np.array(subband, dtype=np.int32)
    subband -= OFFSET
    return subband

def write(subband: np.ndarray, prefix: str, frame_number: int) -> None:
    if __debug__:
        print(f"L.write({prefix}, {frame_number})", subband.max(), subband.min(), subband.shape, subband.dtype, end=' ')
    subband = np.array(subband, dtype=np.int32)
    subband += OFFSET
    assert (subband < 65536).all()
    assert (subband > -1).all()
    subband = subband.astype(np.uint16)
    subband = cv.cvtColor(subband, cv.COLOR_RGB2BGR)
    fn = f"{prefix}LL{frame_number:03d}.png"
    cv.imwrite(fn, subband)
    if __debug__:
        print(os.path.getsize(fn))

def interpolate(L: np.ndarray) -> np.ndarray:
    return L.astype(np.float64)

def reduce(_L_: np.ndarray) -> np.ndarray:
    return _L_
