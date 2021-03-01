''' MRVC/compute_br.py '''

import MSE
import frame
import config

total_AMSE = 0.0
for k in range(config.n_frames):
    original_fn = f"{config.input_video}{k:03d}"
    reconstructed_fn = f"{config.output_video}0_{k:03d}"
    original = frame.read(original_fn)
    reconstructed = frame.read(reconstructed_fn)
    AMSE = MSE.MSE(original, reconstructed[:original.shape[0],:original.shape[1],:])
    print(f"AMSE of frame {k} = {AMSE}")
    total_AMSE += AMSE

AMSE = total_AMSE/config.n_frames
print("Average Mean Square Error (entire sequence)=", AMSE)
