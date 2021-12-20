''' MRVC/2D_DWT.py

Provides:

1. Multichannel 1-level 2D-DWT and inverse 2D-DWT.
2. Multichannel N-levels 2D-DWT and inverse 2D-DWT.
3. Subbands gains computation.
3. Decomposition I/O.

Terminology:

* Color decomposition: a list of spatial color resolution levels.
* Color resolution level: one color subband (row, column, component) in the case of LL or a tuple of three color subbands.
* Color subband: a single 3D array indexed by (row, column, component).
* Component:  
'''

import numpy as np
import pywt
#import config
#import distortion
import image_3 as image
import L_DWT as L
import H_DWT as H

_wavelet = pywt.Wavelet("haar")
#wavelet = pywt.Wavelet("db1")
#wavelet = pywt.Wavelet("db5")
#wavelet = pywt.Wavelet("db20")
#wavelet = pywt.Wavelet("bior3.5")
#wavelet = pywt.Wavelet("bior3.7")
#wavelet = pywt.Wavelet("bior6.8")
#wavelet = pywt.Wavelet("rbio6.8")

# Number of levels of the DWT
#N_levels = config.n_levels
_N_levels = 5

# Signal extension mode
#_extension_mode = "symmetric" # default
#_extension_mode = "constant"
#_extension_mode = "reflect"
#_extension_mode = "periodic"
#_extension_mode = "smooth"
#_extension_mode = "antisymmetric"
#_extension_mode = "antireflect"
_extension_mode = "periodization" # Generates the inimal number of coeffs
#_extension_mode = config.dwt_extension_mode

print("Wavelet =", _wavelet)
print("DWT extension mode =", _extension_mode)

def analyze_step(color_image, wavelet=_wavelet) -> tuple:
    '''Color 1-levels forward 2D-DWT.

    Parameters
    ----------
    color_image : [row, column, component] np.ndarray
        Color image to be analyzed.
    wavelet : pywt.Wavelet
        Wavelet name.

    Returns
    -------
    A 1-levels color decomposition : list of spatial resolution levels.

    '''
    N_comps = color_image.shape[2]
    decomposition_by_component = [None]*N_comps
    # A color decomposition 
    for c in range(N_comps):
        decomposition_by_component[c] = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode=_extension_mode)
    assert decomposition_by_component[0][0].shape == decomposition_by_component[0][1][0].shape
    N_rows_subband, N_columns_subband = decomposition_by_component[0][0].shape # All subbands have the same shape
    LL = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    LH = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HL = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HH = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    for c in range(N_comps):
        LL[:,:,c] = decomposition_by_component[c][0][:,:]
        LH[:,:,c] = decomposition_by_component[c][1][0][:,:]
        HL[:,:,c] = decomposition_by_component[c][1][1][:,:]
        HH[:,:,c] = decomposition_by_component[c][1][2][:,:]
    return (LL, (LH, HL, HH)) # Ojo, para ser coherentes, debería
                              # retornarse una lista, no una tupla, y
                              # así tendríamos una descomposición de 1
                              # nivel

def synthesize_step(LL, H, wavelet=_wavelet):
    '''Color 1-levels backward 2D-DWT.

    Parameters
    ----------
    LL : np.ndarray
        Low-pass subband.
    H : tuple
        High-pass subbands.
    wavelet : pywt.Wavelet
        Wavelet name.

    Returns
    -------
    A color image : [row, column, component] np.ndarray 

    '''
    LH, HL, HH = H
    N_comps = LL.shape[2] #len(LL)
    _color_image = []
    for c in range(N_comps):
        image = pywt.idwt2((LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c])), wavelet=wavelet, mode=_extension_mode)
        #image = pywt.idwt2((LL[:,:,c], np.array(H)[:,:,c]), wavelet=wavelet, mode=_extension_mode)
        _color_image.append(image)
    n_rows, n_columns = _color_image[0].shape
    #n_rows = _color_image[0].shape[0]
    #n_columns = _color_image[0].shape[1]
    color_image = np.ndarray((n_rows, n_columns, N_comps), dtype=np.float64)
    for c in range(N_comps):
        color_image[:,:,c] = _color_image[c][:,:]
    return color_image

def analyze(color_image, wavelet=_wavelet, N_levels=_N_levels):
    '''Color N-levels forward 2D-DWT.

    Parameters
    ----------
    color_image : [row, column, component] np.ndarray
        Color image to be analyzed.
    wavelet : pywt.Wavelet
        Wavelet name.
    N_levels : int
        Number of levels of the transform.

    Returns
    -------
        A color decomposition : list

    '''
    N_comps = color_image.shape[2]
    decomposition_by_component = [None]*N_comps
    for c in range(N_comps):
        decomposition_by_component[c] = pywt.wavedec2(data=color_image[:,:,c], wavelet=wavelet, mode=_extension_mode, level=N_levels)

    color_decomposition = []
    # LL^N_levels and H^N_levels subbands (both have the same resolution)
    N_rows_subband, N_columns_subband = decomposition_by_component[0][0].shape # All subbands in the SRL with the same shape
    #prev_N_rows_subband = N_rows_subband
    #prev_N_columns_subband = N_columns_subband
    LL = np.empty(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    LH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HL = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    HH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
    for c in range(N_comps): # For each color component
        LL[:,:,c] = decomposition_by_component[c][0][:,:]
        LH[:,:,c] = decomposition_by_component[c][1][0][:,:]
        HL[:,:,c] = decomposition_by_component[c][1][1][:,:]
        HH[:,:,c] = decomposition_by_component[c][1][2][:,:]
    color_decomposition.append(LL)
    color_decomposition.append((LH, HL, HH))
    
    # For the rest of SRLs (have increasing resolutions)
    for r in range(2, N_levels+1):
        N_rows_subband, N_columns_subband = decomposition_by_component[0][r][0].shape
        #if prev_N_rows_subband * 2 < N_rows_subband:
        #    N_rows_subband += 1
        #prev_N_rows_subband = N_rows_subband
        #if prev_N_columns_subband * 2 < N_columns_subband:
        #    N_columns_subband += 1
        prev_N_columns_subband = N_columns_subband
        LH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        HL = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        HH = np.zeros(shape=(N_rows_subband, N_columns_subband, N_comps), dtype=np.float64)
        for c in range(N_comps):
            LH[:,:,c] = decomposition_by_component[c][r][0][:,:]
            HL[:,:,c] = decomposition_by_component[c][r][1][:,:]
            HH[:,:,c] = decomposition_by_component[c][r][2][:,:]
        color_decomposition.append((LH, HL, HH))

    return color_decomposition # [LL^n, (LH^n, HL^n, HH^n), ..., (LH^1, HL^1, HH^1)], each subband multicomponent.

def synthesize(color_decomposition:list, wavelet:pywt.Wavelet=_wavelet, N_levels:int=_N_levels) -> np.ndarray:
    _color_image = []
    N_comps = color_decomposition[0].shape[2]
    for c in range(N_comps):
        decomposition = [color_decomposition[0][:,:,c]] # LL^n
        for l in range(1, N_levels+1):
            decomposition.append((color_decomposition[l][0][:,:,c], color_decomposition[l][1][:,:,c], color_decomposition[l][2][:,:,c])) # (LH^l, HL^l, HH^l)
        _color_image.append(pywt.waverec2(decomposition, wavelet=wavelet, mode=_extension_mode))
    color_image = np.ndarray((_color_image[0].shape[0], _color_image[0].shape[1], N_comps), dtype=_color_image[0].dtype)
    #print(_color_image[0].shape, color_image.shape)
    for c in range(N_comps):
        color_image[:,:,c] = _color_image[c][:,:]
    
    #print(N_comps)
    #_color_image = []
    #for c in range(N_comps):
    #    channel = pywt.waverec2(color_decomposition[c], wavelet=wavelet, mode=_extension_mode)
    #    _color_image.append(channel)
    #n_rows = _color_image[0].shape[0]
    #n_columns = _color_image[0].shape[1]
    #color_image = np.ndarray((n_rows, n_columns, N_comps), np.float64)
    #for c in range(N_comps):
    #    color_image[:,:,c] = _color_image[c][:,:]
    return color_image

# Ojo, que esto no está terminado!!!!!!!!!!!!!!!!!!!!!!
def compute_gains(N_levels):
    gains = [1.0]*N_levels
    for l in range(1,N_levels):
        gains[l] = gains[l-1]*2
    return gains

def extract_component_decomposition(color_decomposition, component_index):
    '''Extract a component (in form of a decomposition) from a color decomposition.

    Parameters
    ----------
    color_decomposition : list
        A list of color resolutions.
    component_index : int
        The component to extract.

    Returns
    -------
    A (monochromatic) decomposition: list

    '''
    component_decomposition = [decomposition[0][..., component_index]]
    for resolution in color_decomposition[1:]:
        resolution_decomposition = [] 
        for subband in resolution:
            resolution_decomposition.append(subband[..., component_index])
    component_decomposition.append(tuple(resolution_decomposition))
    return component_decomposition

def insert_component_decomposition(color_decomposition:list, component_decomposition:list, component_index:int) -> None:
    '''Insert a decomposition (a list of tuples of 2D subbands (each one a
(row, column)-np.ndarray) in a color decomposition (a list of tuples
of 3D subbands (each one a (row, column, component)-np.ndarray).
    '''
    color_decomposition[0][..., component_index] = component_decomposition[0][:]
    for color_resolution, component_resolution in zip(color_decomposition, component_decomposition):
        color_resolution[..., component_index] = component_resolution[component_index]
    
def glue_component_decomposition(component_decomposition:list) -> (np.ndarray, list):
    '''Convert a list of (monocromatic) subbands to a 2D (rows, columns) NumPy array.'''
    glued_component_decomposition, slices = pywt.coeffs_to_array(component_decomposition))
    return glued_component_decomposition, slices

def unglue_component_decomposition(glued_component_decomposition:np.ndarray, slices:list) -> list:
    '''Convert a 2D color decomposition (a (row, column)-np.array) in a
list of tuples of 2D subbands (each one a (row,
column)-np.ndarray).'''
    component_decomposition = pywt.array_to_coeffs(glued_component_decomposition, coeff_slices=slices, output_format='wavedec2')
    return component_decomposition

def glue_color_decomposition(color_decomposition:list) -> np.ndarray:
    '''Convert a list of color subbands to a 3D (rows, columns, components) NumPy array.'''
    components_decomposition = []
    glued_components = []
    slices = [None]*3
    for component_index in range(3):
        component_decomposition, slices[component_index] = extract_component_decomposition(color_decomposition, component_index)
        components_decomposition.append(component_decomposition)
        glued_components.append(glue_component_decomposition(component_decomposition))
    glued_color_decomposition = np.empty(shape=(glued_components[0].shape[0], glued_components[0].shape[0], 3), dtype=np.float64)
    for component_index in range(3):
        glued_color_decomposition[..., component_index] = glued_component[component_index][:]
    return glued_color_decomposition, slices

def unglue_color_decomposition(glued_color_decomposition:np.ndarray, slices:list) -> list:
    '''Convert a 3D color decomposition (a (row, column,
component)-np.ndarray) in a list of tuples of 3D color subbands (each
one a (row, column, component)-np.ndarray).'''
    decomposition_by_component = []
    for component_index in range(3):
        decomposition_by_component.append(unglue_component_decomposition(glued_color_decomposition[..., component_index], slices[component_index]))
    # "decomposition_by_component" is a list with three decompositions.
    
        color_LL = np.empty(shape=(unglued_decomposition_by_component[0][0].shape[0], unglued_decomposition_by_component[0][0].shape[1], 3), dtype=np.float64)
    unglued_color_decomposition = [color_LL]
    for color_resolution in zip(*unglued_decomposition_by_component[1:]):
        color_resolution = np.empty(shape=nose
        for component_index in range(3):
            color_resolution =  
        unglued_color_decomposition.append(color_resolution)

def write_glued(color_decomposition:list, prefix=str, image_number:int=0) -> list:
    glued_color_decomposition, slices = glue_color_decomposition(color_decomposition)
    image_3.write(glued_color_decomposition, prefix, image_number)
    return slices

def read_glued(slices: list, prefix:str, image_number:int=0) -> list:
    glued_color_decomposition = image_3.read(prefix, image_number)
    color_decomposition = unglue_color_decomposition(glued_color_decomposition, slices)
    return color_decomposition

# Write each subband of a decomposition in a different PNG file using
# <prefix><image_number><LL|LH|HL|HH><level>.png filename.
def write_splitted(color_decomposition:list, prefix:str, image_number:int=0, N_levels:int=_N_levels) -> None:
    N_comps = color_decomposition[0].shape[2]
    #_color_image = [None]*N_comps
    #n_resolutions = len(color_decomposition)
    #n_resolutions = N_levels+1
    LL = color_decomposition[0]
    L.write(LL, f"{prefix}R{N_levels}", image_number)
    resolution_index = N_levels
    for resolution in color_decomposition[1:]:
        H.write(resolution, f"{prefix}R{resolution_index}", image_number)
        resolution_index -= 1
        
    #for c in range(N_comps):
    #    decomposition = [color_decomposition[0][:,:,c]]
    #    LL = decomposition[0]
    #    for l in range(1, n_levels+1):
    #        decomp.append((color_decomp[l][0][:,:,c], color_decomp[l][1][:,:,c], color_decomp[l][2][:,:,c]))
    #    _color_image[c], slices = pywt.coeffs_to_array(decomp)
    #color_image = np.ndarray((_color_image[0].shape[0], _color_image[0].shape[1], N_comps), dtype=_color_image[0].dtype)
    #for c in range(N_comps):
    #    color_image[:,:,c] = _color_image[c][:,:]
    #image.write(color_image.astype(np.int16), fn)
    #return slices

#def read(prefix:str, slices:list=None) -> np.ndarray: 
def read_splitted(prefix:str, image_number:int=0, N_levels:int=_N_levels) -> np.ndarray:
    #LL = L.read(f"{prefix}_{N_levels+1}", image_number)
    LL = L.read(f"{prefix}R{N_levels}", image_number)
    color_decomposition = [LL]
    shape = list(LL.shape)
    #for l in range(N_levels+1, 0, -1):
    for l in range(N_levels, 0, -1):
        resolution = H.read(f"{prefix}R{l}", image_number, tuple(shape))
        color_decomposition.append(resolution)
        shape[0] *= 2
        shape[1] *= 2
    return color_decomposition
    #color_image = image.read(f)
    #N_comps = color_image.shape[2]
    #color_decomp = [None]*N_comps
    #for c in range(N_comps):
    #    color_decomp[c] = pywt.array_to_coeffs(color_image[:,:,c], slices, output_format='wavedec2')
    #output = []
    #n_rows_subband, n_columns_subband = color_decomposition[0][0].shape
    #LL = np.empty(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #LH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #HL = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #HH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #for c in range(N_comps): # For each color component
    #    LL[:,:,c] = color_decomposition[c][0][:,:]
    #    LH[:,:,c] = color_decomposition[c][1][0][:,:]
    #    HL[:,:,c] = color_decomposition[c][1][1][:,:]
    #    HH[:,:,c] = color_decomposition[c][1][2][:,:]
    #output.append(LL)
    #output.append((LH, HL, HH))
    #for r in range(2, n_levels+1):
    #    n_rows_subband, n_columns_subband = color_decomposition[0][r][0].shape
    #    prev_n_columns_subband = n_columns_subband
    #    LH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #    HL = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #    HH = np.zeros(shape=(n_rows_subband, n_columns_subband, N_comps), dtype=np.float64)
    #    for c in range(N_comps):
    #        LH[:,:,c] = color_decomposition[c][r][0][:,:]
    #        HL[:,:,c] = color_decomposition[c][r][1][:,:]
    #        HH[:,:,c] = color_decomposition[c][r][2][:,:]
    #    output.append((LH, HL, HH))

    #return output

'''
def normalize_256(color_decomposition:list, n_levels:int) -> (list, float, float):
    #Normalize the decomposition to the range [0, 255]. The maximum n
and the minimum values are also returned.
    N_comps = color_decomposition[0].shape[2]
    #_color_image = [None]*N_comps
    #n_resolutions = len(color_decomposition)
    #n_resolutions = n_levels+1
    max = -100000
    min = 100000
    LL = color_decomposition[0]
    max = 
    L.write(LL, f"{prefix}_{n_levels}", image_number)
    resolution_index = n_levels
    for resolution in color_decomposition[1:]:
        H.write(resolution, f"{prefix}_{resolution_index}", image_number)
        resolution_index -= 1
'''
    
    
################

def __compute_deltas(n_levels):
    delta = []
    dims = (512, 512, 3)
    x = np.zeros(dims)
    L = DWT.analyze(x, n_levels)
    L[0][1,1,:] = [100, 100, 100]
    y = DWT.synthesize(L, l)
    e = distortion.average_energy(y)
    for l in range(1, n_levels):
        x = np.zeros(dims)
        L = LP.analyze(x, n_levels)
        L[l][1,1,:] = [100, 100, 100]
        y = DWT.synthesize(L)
        ee = distortion.average_energy(y)
        gain = e/ee
        delta.append(gain)
        print(gain)
        e = ee
    return delta

def __analyze_step(color_image, wavelet=_wavelet):
    n_rows, n_columns, N_comps = color_image.shape[0]//2, color_image.shape[1]//2, color_image.shape[2]
    LL = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    LH = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    HL = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    HH = np.empty(shape=(n_rows, n_columns, N_comps), dtype=np.float64)
    #N_comps = color_image.shape[2]
    #color_decomposition = [None]*N_comps
    for c in range(N_comps):
        #color_decomposition[c] = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode='per')
        LL[:,:,c], (LH[:,:,c], HL[:,:,c], HH[:,:,c]) = pywt.dwt2(data=color_image[:,:,c], wavelet=wavelet, mode='per')
    #return color_decomposition
    #return np.array([color_decomposition[0][0], color_decomposition[1][0], color_decomposition[2][0]]), ()
    return (LL, (LH, HL, HH))

def __synthesize_step(LL, H, wavelet=_wavelet):
    N_comps = len(color_decomposition)
    color_image = []
    for c in range(N_comps):
        channel = pywt.idwt2(color_decomposition[c], wavelet=wavelet, mode='per')
        color_image.append(channel)
    return np.array(color_image)
def __analyze(color_image, wavelet=_wavelet, levels=_N_levels):
    H = [None]*levels
    L, H[0] = analyze_step(color_image, wavelet)
    for i in range(levels-1):
        L, H[i+1] = analyze_step(L, wavelet)
    #return [L, *H[::-1]]
    return [L, *H]

def __synthesize(color_decomposition, wavelet=_wavelet, N_levels=_N_levels):
    color_image = synthesize_step(color_decomposition[0], color_decomposition[1], wavelet)
    for i in range(N_levels-1):
        color_image = synthesize_step(color_image, color_decomposition[i], wavelet)
    return color_image
