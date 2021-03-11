''' MRVC/image_IPP.py '''

import DWT
import LP
import numpy as np
import L_DWT as L
import H_DWT as H
import deadzone as Q
import motion
import frame
import colors
import cv2
import YCoCg as YUV
import os

VIDEO_PREFIX = "../sequences/complete_stockholm/"
CODESTREAM_PREFIX = "/tmp/"
DECODED_VIDEO_PREFIX = "/tmp/decoder_"
#Q_STEP = 128
N_FRAMES = 16
LOG2_BLOCK_SIZE = 4 # BLOCK_SIZE = 1 << LOG2_BLOCK_SIZE
N_LEVELS = 5

def norm(x):
    return (frame.normalize(x)*255).astype(np.uint8)

def clip(x):
    return(np.clip(x, 0 ,255).astype(np.uint8))

def E_codec(E_k, n_levels, q_step, prefix, k):
    decom = DWT.analyze(E_k, n_levels)
    #print(decom[0])
    LL = decom[0]
    decom[0] = Q.quantize(LL, q_step)
    for resolution in decom[1:]:
        resolution = list(resolution)
        LH = resolution[0]
        resolution[0][:] = Q.quantize(LH, q_step)
        HL = resolution[1]
        resolution[1][:] = Q.quantize(HL, q_step)
        HH = resolution[2]
        resolution[2][:] = Q.quantize(HH, q_step)
        resolution = tuple(resolution)
    DWT.write(decom, prefix, k, n_levels)
    LL = decom[0]
    #print(LL)
    decom[0] = Q.dequantize(LL, q_step)
    #print(decom[0])
    for resolution in decom[1:]:
        resolution = list(resolution)
        LH = resolution[0]
        resolution[0][:] = Q.dequantize(LH, q_step)
        HL = resolution[1]
        resolution[1][:] = Q.dequantize(HL, q_step)
        HH = resolution[2]
        resolution[2][:] = Q.dequantize(HH, q_step)
        resolution = tuple(resolution)
    #print("->", decom[1][0])
    dq_E_k = DWT.synthesize(decom, n_levels)
    return dq_E_k
    #return E_k-dq_E_k
    #return E_k

# https://stackoverflow.com/questions/34123272/ffmpeg-transmux-mpegts-to-mp4-gives-error-muxer-does-not-support-non-seekable: ffmpeg -blocksize 1 -i /tmp/original_000.png -blocksize 1 -flush_packets 1 -movflags frag_keyframe+empty_moov -f mp4 - | ffmpeg -blocksize 1 -i - -blocksize 1 -flush_packets 1 /tmp/decoded_%3d.png

# https://video.stackexchange.com/questions/16958/ffmpeg-encode-in-all-i-mode-h264-and-h265-streams: fmpeg -i input -c:v libx264 -intra output / ffmpeg -i input -c:v libx265 -x265-params frame-threads=4:keyint=1:ref=1:no-open-gop=1:weightp=0:weightb=0:cutree=0:rc-lookahead=0:bframes=0:scenecut=0:b-adapt=0:repeat-headers=1 output
def E_codec2(E_k, prefix, k):
    print("-------------", E_k.max(), E_k.min())
    L.write(YUV.to_RGB(E_k), prefix + "_to_mp4", k)
    #frame.write(YUV.to_RGB(E_k), prefix + "_to_mp4", k)
    os.system(f"ffmpeg -y -i {prefix}_to_mp4_{k:03d}_LL.png -crf 1 {prefix}_{k:03d}.mp4")
    os.system(f"ffmpeg -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}_LL.png")
    dq_E_k = YUV.from_RGB(L.read(prefix + "_from_mp4", k))
    #dq_E_k = (YUV.from_RGB(frame.read(prefix + "_from_mp4", k)))
    return dq_E_k.astype(np.float64)

def E_codec3(E_k, prefix, k):
    print("-------------", E_k.max(), E_k.min())
    #frame.write(clip(YUV.to_RGB(E_k)), prefix + "_to_mp4", k)
    frame.write(YUV.to_RGB(E_k), prefix + "_to_mp4", k)
    os.system(f"ffmpeg -y -i {prefix}_to_mp4_{k:03d}.png -crf 35 {prefix}_{k:03d}.mp4")
    os.system(f"ffmpeg -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
    dq_E_k = (YUV.from_RGB(frame.read(prefix + "_from_mp4", k)))
    return dq_E_k.astype(np.float64)

def E_codec4(E_k, prefix, k):
    print("-------------", E_k.max(), E_k.min())
    #frame.write(clip(YUV.to_RGB(E_k)), prefix + "_to_mp4", k)
    frame.write(clip(YUV.to_RGB(E_k)+128), prefix + "_to_mp4", k)
    os.system(f"ffmpeg -y -i {prefix}_to_mp4_{k:03d}.png -crf 35 {prefix}_{k:03d}.mp4")
    os.system(f"ffmpeg -y -i {prefix}_{k:03d}.mp4 {prefix}_from_mp4_{k:03d}.png")
    dq_E_k = (YUV.from_RGB(frame.read(prefix + "_from_mp4", k)-128))
    return dq_E_k.astype(np.float64)

def V_codec(motion, n_levels, prefix, frame_number):
    pyramid = LP.analyze(motion, n_levels)
    #pyramid[0][:,:,:] = 0
    frame.write(pyramid[0][:,:,0], prefix+"_y", frame_number)
    frame.write(pyramid[0][:,:,1], prefix+"_x", frame_number)
    for resolution in pyramid[1:]:
        resolution[:,:,:] = 0
    reconstructed_motion = LP.synthesize(pyramid, n_levels)
    #print(motion-reconstructed_motion[:motion.shape[0], :motion.shape[1], :])
    return reconstructed_motion
    #decom_Y = pywt.wavedec2(motion[:,:,0], 'db1', mode='per', levels=3)
    #decom_X = pywt.wavedec2(motion[:,:,1], 'db1', mode='per', levels=3)
    #L.write(decom_Y[0], prefix, k)
    #L.write(decom_Y[1], prefix, k)
    #H_subbands_decom_Y = decom_Y[1:]
    #for resolution in H_subbands_decom_Y:
    #    resolution[0][:,:] = 0
    #    resolution[1][:,:] = 0
    #    resolution[2][:,:] = 0
    #H_subbands_decom_X = decom_X[1:]
    #for resolution in H_subbands_decom_X:
    #    resolution[0][:,:] = 0
    #    resolution[1][:,:] = 0
    #    resolution[2][:,:] = 0
    #pywt.waverec2(decom_Y, 'db1')
    #pywt.waverec2(decom_X, 'db1')
    #_motion = np.empty_like(motion)
    #_motion[:,:,0] = decom_Y[:,:]
    #_motion[:,:,0] = decom_X[:,:]
    #return _motion

def _V_codec(motion, n_levels, prefix, frame_number):
    pyramid = motion
    frame.write(pyramid[:,:,0], prefix+"_y", frame_number)
    frame.write(pyramid[:,:,1], prefix+"_x", frame_number)
    return pyramid

def encode(video=VIDEO_PREFIX, codestream=CODESTREAM_PREFIX, n_frames=N_FRAMES, q_step=Q.step):
    try:
        k = 0
        W_k = frame.read(video, k)
        flow = np.zeros((W_k.shape[0], W_k.shape[1], 2), dtype=np.float32)
        V_k = YUV.from_RGB(W_k) # (a)
        V_k_1 = V_k # (b)
        E_k = V_k # (d)
        #dequantized_E_k = E_codec(E_k, N_LEVELS, q_step, codestream, 0) # (g and h)
        dequantized_E_k = E_codec3(E_k, codestream, 0) # (g and h)
        reconstructed_V_k = dequantized_E_k # (i)
        frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}_reconstructed", k) # Decoder's output
        reconstructed_V_k_1 = reconstructed_V_k # (j)
        for k in range(1, n_frames):
            W_k = frame.read(video, k)
            V_k = YUV.from_RGB(W_k) # (a)
            flow = motion.estimate(V_k[:,:,0], V_k_1[:,:,0], flow) # (c)
            V_k_1 = V_k # (b)
            reconstructed_flow = V_codec(flow, LOG2_BLOCK_SIZE, f"{codestream}_motion", k) # (d and e)
            frame.debug_write(motion.colorize(flow), f"{codestream}_flow", k)
            prediction_V_k = motion.make_prediction(reconstructed_V_k_1, reconstructed_flow) # (j)
            print("flow.shape =", flow.shape, "reconstructed_flow.shape =", reconstructed_flow.shape)
            frame.debug_write(clip(YUV.to_RGB(prediction_V_k)), f"{codestream}_encoder_prediction", k)
            E_k = V_k - prediction_V_k[:V_k.shape[0], :V_k.shape[1], :] # (f)
            print(E_k.dtype)
            frame.debug_write(clip(YUV.to_RGB(E_k)+128), f"{codestream}_encoder_prediction_error", k)
            #dequantized_E_k = E_codec(E_k, 5, q_step, codestream, k) # (g and h)
            dequantized_E_k = E_codec4(E_k, codestream, k) # (g and h)
            #quantized_E_k = Q.quantize(E_k, step=q_step) # (e)
            #dequantized_E_k = Q.dequantize(quantized_E_k, step=q_step) # (f)
            frame.debug_write(clip(YUV.to_RGB(dequantized_E_k)), f"{codestream}_encoder_dequantized_prediction_error", k)
            reconstructed_V_k = dequantized_E_k + prediction_V_k[:dequantized_E_k.shape[0], :dequantized_E_k.shape[1], :] # (i)
            #L.write(reconstructed_V_k, video + "reconstructed", k)
            frame.debug_write(clip(YUV.to_RGB(reconstructed_V_k)), f"{video}_reconstructed", k) # Decoder's output
            reconstructed_V_k_1 = reconstructed_V_k # (j)
    except:
        print(colors.red(f'image_IPP_step.encode(video="{video}", codestream="{codestream}", n_frames={n_frames}, q_step={q_step})'))
        raise

def compute_br(prefix, frames_per_second, frame_shape, n_frames):
    #os.system(f"ffmpeg -y -i {prefix}_from_mp4_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_texture.mp4")
    #os.system(f"ffmpeg -f concat -safe 0 -i <(for f in {prefix}_*.mp4; do echo \"file '$PWD/$f'\"; done) -c copy /tmp/image_IPP_texture.mp4")
    os.system(f"ffmpeg -y -f concat -safe 0 -i <(for f in {prefix}_*.mp4; do echo \"file '$f'\"; done) -c copy /tmp/image_IPP_texture.mp4")
    os.system(f"ffmpeg -y -i {prefix}_motion_y_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_y.mp4")
    os.system(f"ffmpeg -y -i {prefix}_motion_x_%03d.png -c:v libx264 -x264-params keyint=1 -crf 0 /tmp/image_IPP_x.mp4")

    frame_height = frame_shape[0]
    frame_width = frame_shape[1]
    channels = frame_shape[2]
    sequence_time = n_frames/frames_per_second

    texture_bytes = os.path.getsize("/tmp/image_IPP_texture.mp4")
    print(f"texture: {texture_bytes} bytes, {texture_bytes*8/sequence_time/1000} kbps, {texture_bytes*8/(frame_width*frame_height*channels*n_frames)} bpp")
    total_bytes = texture_bytes
    motion_y_bytes = os.path.getsize("/tmp/image_IPP_y.mp4")
    print(f"motion (Y direction): {motion_y_bytes} bytes, {motion_y_bytes*8/sequence_time/1000} kbps")
    total_bytes += motion_y_bytes
    motion_x_bytes = os.path.getsize("/tmp/image_IPP_x.mp4")
    print(f"motion (X direction): {motion_x_bytes} bytes, {motion_x_bytes*8/sequence_time/1000} kbps")
    total_bytes += motion_x_bytes
    print(f"total: {total_bytes*8/sequence_time/1000} kbps, {total_bytes*8/(frame_width*frame_height*3*n_frames)} bpp")
