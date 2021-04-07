''' MRVC/MP4.py '''

import os
import colors

# Only I and P blocks are allowed.

def encode(video,    # Prefix of the original sequence of PNG images 
           n_frames, # Number of frames to process
           q_step):  # Quantization step
    try:
        command = f"ffmpeg -y -i {video}%3d.png -crf {q_step} -frames:v {n_frames} -g {n_frames} -bf 0 /tmp/output.mp4"
        os.system(command)

        command = f"ffmpeg -y -i /tmp/output.mp4 ${video}reconstructed_%03d.png"
        os.system(command)
        
    except:
        print(colors.red(f'MP4.encode(video="{video}", n_frames={n_frames}, q_step={q_step})'))
        raise

def compute_br(prefix, frames_per_second, frame_shape, n_frames):
    frame_height = frame_shape[0]
    frame_width = frame_shape[1]
    n_channels = frame_shape[2]
    sequence_time = n_frames/frames_per_second
    print(f"height={frame_height} width={frame_width} n_channels={n_channels} sequence_time={sequence_time}")
    
    total_bytes = os.path.getsize("/tmp/output.mp4")
    kbps = total_bytes*8/sequence_time/1000
    bpp = total_bytes*8/(frame_width*frame_height*n_channels*n_frames)
    return kbps, bpp
