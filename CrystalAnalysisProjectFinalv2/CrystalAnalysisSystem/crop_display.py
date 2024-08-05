import tkinter as tk
from tkinter import filedialog, messagebox
import os
import cv2
import numpy as np
from PIL import Image, ImageTk

import CrystalAnalysisSystem.utils as utils
from CrystalAnalysisSystem.shape_analyser import ShapeAnalyser


class CropDisplay(tk.Toplevel):
    def __init__(self, master, cropped_frames, video_processor):
        super().__init__(master)
        # Setup
        self.title("Cropped Frames")
        self.geometry("800x600")
        self.cropped_frames = cropped_frames  # List of cropped frames
        self.current_frame_index = 0
        self.video_processor = video_processor
        self.analyser = ShapeAnalyser(self.cropped_frames[self.current_frame_index])
        self.stages = []
        self.current_stage_index = 0
        self.layer_names = [
            "Original", "Grayscale", "Contrast Enhanced", "Blurred",
            "Adaptive Thresholding", "Morphological Closing", "Canny Edges",
            "Hough Lines", "Final with Bounding Box"
        ]
        self.analysis_data = []

        # Canvas setup
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(fill=tk.X)

        # analysis button (change name)
        self.analyze_button = tk.Button(self.controls_frame, text="Start Analysis", command=self.start_analysis)
        self.analyze_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Previous layer button (change this to layer)
        self.prev_stage_button = tk.Button(self.controls_frame, text="Previous Stage", command=self.show_previous_stage,
                                           state=tk.DISABLED)
        self.prev_stage_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Next layer button (change this to layer)
        self.next_stage_button = tk.Button(self.controls_frame, text="Next Stage", command=self.show_next_stage,
                                           state=tk.DISABLED)
        self.next_stage_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.prev_frame_button = tk.Button(self.controls_frame, text="Previous Frame", command=self.prev_frame)
        self.prev_frame_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_frame_button = tk.Button(self.controls_frame, text="Next Frame", command=self.next_frame)
        self.next_frame_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Labels for displaying bounding box dimensions and current layer
        self.info_frame = tk.Frame(self)
        self.info_frame.pack(fill=tk.X)

        self.dimensions_label = tk.Label(self.info_frame, text="Dimensions: N/A")
        self.dimensions_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.layer_label = tk.Label(self.info_frame, text="Layer: Original")
        self.layer_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.display_frame(self.cropped_frames[self.current_frame_index])

    def display_frame(self, frame):
        """
        Display the given frame on the canvas.
        """
        if isinstance(frame, np.ndarray):  # Check if frame is a numpy array
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk

    def start_analysis(self):
        """
        Start the analysis for all cropped frames and save the results to a CSV file.
        """
        for index, frame in enumerate(self.cropped_frames):
            self.analyser = ShapeAnalyser(frame)
            width, height, angle = self.analyser.process_image()

            # Collect analysis data
            self.analysis_data.append({
                'Frame Index': index,
                'Width': width if width is not None else "N/A",
                'Height': height if height is not None else "N/A",
                'Angle': angle if angle is not None else "N/A",
            })

        # Save the analysis data to a CSV file
        self.save_analysis_data()

    def save_analysis_data(self):
        """
        Save the collected analysis data to a CSV file in the 'log' directory.
        """
        if not os.path.exists('log'):
            os.makedirs('log')

        file_path = os.path.join('log', 'manual_analysis_data.csv')
        headers = ['Frame Index', 'Width', 'Height', 'Angle']  # ['Frame Index', 'Width', 'Height', 'Angle', 'Layer']
        utils.save_analysis_to_csv(file_path, self.analysis_data, headers)
        messagebox.showinfo("Save Successful", f"Analysis data saved to {file_path}")

    def next_frame(self):
        """
        Display the next cropped frame.
        """
        if self.current_frame_index < len(self.cropped_frames) - 1:
            self.current_frame_index += 1
            self.update_for_new_frame()

    def prev_frame(self):
        """
        Display the previous cropped frame.
        """
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            self.update_for_new_frame()

    def update_for_new_frame(self):
        """
        Update the display and analysis for the new frame.
        """
        self.analyser = ShapeAnalyser(self.cropped_frames[self.current_frame_index])
        self.stages = []
        self.current_stage_index = 0
        self.display_frame(self.cropped_frames[self.current_frame_index])
        self.update_info()
        self.update_stage_controls()

    def show_next_stage(self):
        """
        Display the next stage of the analysis.
        """
        if self.current_stage_index < len(self.stages) - 1:
            self.current_stage_index += 1
            self.display_frame(self.stages[self.current_stage_index])
            self.update_info()

    def show_previous_stage(self):
        """
        Display the previous stage of the analysis.
        """
        if self.current_stage_index > 0:
            self.current_stage_index -= 1
            self.display_frame(self.stages[self.current_stage_index])
            self.update_info()

    def update_info(self):
        """
        Update the information displayed about the current frame.
        """
        width, height, angle = self.analyser.process_image()
        self.stages = self.analyser.stages

        if width is not None and height is not None:
            self.dimensions_label.config(text=f"Dimensions: Width={width}, Height={height}")
        else:
            self.dimensions_label.config(text="Dimensions: N/A")

        if 0 <= self.current_stage_index < len(self.layer_names):
            layer_name = self.layer_names[self.current_stage_index]
        else:
            layer_name = "Unknown"

        self.layer_label.config(text=f"Layer: {layer_name}")

    def update_stage_controls(self):
        """
        Enable or disable stage navigation buttons based on the current analysis stage.
        """
        if len(self.stages) > 1:
            self.next_stage_button.config(state=tk.NORMAL)
            self.prev_stage_button.config(state=tk.NORMAL)
        else:
            self.next_stage_button.config(state=tk.DISABLED)
            self.prev_stage_button.config(state=tk.DISABLED)
