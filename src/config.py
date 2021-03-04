''' MRVC/config.py '''

import cv2

# Number of frames to compress.
#n_frames = 3
#n_frames = 36
n_frames = 500

# Input, output, and codestream prefixes.
prefix = "/media/sdc1/Q8L3_LP"
#prefix = "/media/sdc1/Q54L3_DWT"
input_video = f"{prefix}/original_"
codestream = f"{prefix}/codestream_"
output_video = f"{prefix}/reconstructed_"

# Number of spatial resolution levels = n_levels + 1
n_levels = 3
#n_levels = 5
#n_levels = 7
#n_levels = 9

# Frames per second.
fps = 30

print("Number of frames to encode =", n_frames)
print("Original video =", input_video)
print("Codestream =", codestream)
print("Reconstructed video =", output_video)
print("Number of spatial resolution levels =", n_levels)
print("Frames per second =", fps)
