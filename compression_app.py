import tifffile
import numpy as np
import os
import h5py
import time
import shutil 
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QSlider, QHBoxLayout

class VideoHDF5App(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Video HDF5 Creator')

        # Create widgets
        self.folder_button = QPushButton('Select Folder')
        self.compression_label = QLabel('Compression Factor:')
        self.compression_slider = QSlider()
        self.compression_slider.setOrientation(1)  # Set slider orientation to vertical
        self.compression_slider.setMinimum(1)  # Set minimum value
        self.compression_slider.setMaximum(9)  # Set maximum value
        self.compression_display = QLabel('Compression Factor: 1')
        self.run_button = QPushButton('Run Function')
        self.progress_label = QLabel('Progress:')

        # Connect button clicks to functions
        self.folder_button.clicked.connect(self.select_folder)
        self.run_button.clicked.connect(self.run_function)
        self.compression_slider.valueChanged.connect(self.update_compression_display)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.folder_button)
        layout.addWidget(self.compression_label)
        layout.addWidget(self.compression_slider)
        layout.addWidget(self.compression_display)
        layout.addWidget(self.run_button)
        layout.addWidget(self.progress_label)

        self.setLayout(layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder', os.path.expanduser('~'))
        if folder_path:
            self.selected_folder = folder_path
            self.folder_button.setText(f'Selected Folder: {folder_path}')
        else:
            print("No folder selected.")

    def update_compression_display(self):
        compression_value = self.compression_slider.value()
        self.compression_display.setText(f'Compression Factor: {compression_value}')

    def run_function(self):
        # print(self.selected_folder)
        if hasattr(self, 'selected_folder'):
            compression_value = self.compression_slider.value()

            # Example output file path, adjust as needed
            hdf5_file_path = 'output/video.h5'

            # Call the modified function with progress callback
            self.create_video_hdf5_with_progress(self.selected_folder, hdf5_file_path, compression_value)

    def create_video_hdf5_with_progress(self, tif_folder, hdf5_file_path, compression_value):
        
        # Find number of files in folder
        ls = os.listdir(tif_folder)
        num_files = len(ls)
        count = 0

        output_directory = os.path.dirname(hdf5_file_path)
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)
        os.makedirs(output_directory)

        with h5py.File(hdf5_file_path, 'a') as hdf5_file:
            video_dataset = hdf5_file.require_dataset('video_frames',shape=(0,2048,2048),maxshape=(None,2048,2048), compression="gzip", compression_opts=compression_value,chunks=True,dtype='i1')

            # Loop through all files in folder
            ls = os.listdir(tif_folder)
            for filename in ls:
                s = time.time()

                file_path = os.path.join(tif_folder, filename)
                tif_array = tifffile.imread(file_path)
                current_size = video_dataset.shape[0]
                video_dataset.resize(current_size + 1, axis=0)
                video_dataset[current_size, :, :] = tif_array

                # Update progress in the GUI
                self.progress_label.setText("Progress: " + str(count) + "\\" + str(num_files))
                count = count + 1
                QApplication.processEvents()  # Ensure GUI updates

                e = time.time()
                print("Time taken: " + str(e - s))

            self.progress_label.setText("Progress: " + str(count) + "\\" + str(num_files))

if __name__ == '__main__':
    app = QApplication([])
    window = VideoHDF5App()
    window.show()
    app.exec_()