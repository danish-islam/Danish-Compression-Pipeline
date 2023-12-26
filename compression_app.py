import tifffile
import numpy as np
import os
import h5py
import time
import shutil 

compression_value = 9

tif_folder = 'test_imgs'
hdf5_file_path = 'output/video.h5'

def create_video_hdf5(tif_folder, hdf5_file_path,compression_value):

    # Find number of files in folder
    ls = os.listdir(tif_folder)
    num_files = len(ls)
    count = 0

    output_directory = os.path.dirname(hdf5_file_path)
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    os.makedirs(output_directory)
    
    # Make hdf5 file
    with h5py.File(hdf5_file_path,'a') as hdf5_file:
        video_dataset = hdf5_file.require_dataset('video_frames',shape=(0,2048,2048),maxshape=(None,2048,2048), compression="gzip", compression_opts=compression_value,chunks=True,dtype='i1')

        # Loop through all files in folder
        ls = os.listdir(tif_folder)
        for filename in ls:
            s = time.time()
            file_path = os.path.join(tif_folder,filename)
            tif_array = tifffile.imread(file_path)
            current_size = video_dataset.shape[0]
            video_dataset.resize(current_size + 1, axis=0)
            video_dataset[current_size, :, :] = tif_array

            # Status update
            print("Progress: " + str(count) + "\\" + str(num_files))
            count = count + 1
            e = time.time()
            print("Time taken: " + str(e-s))

        print("Progress: " + str(count) + "\\" + str(num_files))

create_video_hdf5(tif_folder,hdf5_file_path,compression_value)

