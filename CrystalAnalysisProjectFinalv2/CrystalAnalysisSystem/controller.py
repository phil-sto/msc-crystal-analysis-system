import os

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from CrystalAnalysisSystem.video_processor import VideoProcessor
from CrystalAnalysisSystem.frame_display import FrameDisplay
from CrystalAnalysisSystem.crop_display import CropDisplay


class CrystalAnalysisController(tk.Tk):
    """
    Main application class for the Crystal Analysis System.
    Initializes the GUI components and sets up event handlers.
    """
    def __init__(self):
        super().__init__()

        # Set up all the UI Stuff here
        # Create a style
        style = ttk.Style(self)
        # Set the theme with the theme_use method
        style.theme_use('alt')  # put the theme name here, that you want to use

        # Title and window geometry
        self.title("Phil's Crystal Analysis System")
        self.geometry("980x900")

        # Status and frame variables
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.current_frame_var = tk.StringVar()
        self.current_frame_var.set("Frame: 0")

        # Menu bar setup
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Upload Video", command=self.upload_video)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Show Original", command=self.show_original_frames)
        self.view_menu.add_command(label="Show Hough", command=self.show_hough_frames)
        self.view_menu.add_command(label="Show Contour", command=self.show_contour_frames)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.about_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)

        self.config(menu=self.menu_bar)

        # Status bar setup
        self.status_bar_frame = tk.Frame(self, relief=tk.SUNKEN)
        self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.progress_bar = ttk.Progressbar(self.status_bar_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=5)
        self.status_bar = tk.Label(self.status_bar_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.current_frame_label = tk.Label(self.status_bar_frame, textvariable=self.current_frame_var, anchor=tk.E)
        self.current_frame_label.pack(side=tk.RIGHT, padx=5, pady=5)

        # Frame display setup
        self.frame_display = FrameDisplay(self, None, self.current_frame_var)
        self.frame_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Video processor setup
        self.video_processor = VideoProcessor(self.frame_display, self.status_var, self.progress_bar)
        self.frame_display.video_processor = self.video_processor

        # Buttons for Hough transform, contouring, and cropping
        self.hough_button = tk.Button(self.status_bar_frame, text="Apply Hough Transform",
                                      command=self.apply_hough_transform)
        self.hough_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.contour_button = tk.Button(self.status_bar_frame, text="Apply Contouring", command=self.apply_contouring)
        self.contour_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.crop_button = tk.Button(self.status_bar_frame, text="OpenCV Analysis (Crop)", command=self.toggle_cropping)
        self.crop_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Button for running crystal detection model
        self.crystal_detection_button = tk.Button(self.status_bar_frame, text="Run Crystal Detection", command=self.run_crystal_detection)
        self.crystal_detection_button.pack(side=tk.LEFT, padx=5, pady=5)

    def upload_video(self):
        """
        Open a file dialog to upload a video file for processing.
        """
        self.video_processor.upload_video()

    def apply_hough_transform(self):
        """
        Apply Hough Transform to the uploaded video frames.
        """
        self.video_processor.apply_hough_to_frames()

    def apply_contouring(self):
        """
        Apply contouring to the uploaded video frames.
        """
        self.video_processor.apply_contour_to_frames()

    def start_cropping(self):
        """
        Starts cropping of the video frames.
        """
        self.frame_display.start_cropping()

    def toggle_cropping(self):
        """
        Toggle the cropping mode on or off.
        """
        if self.frame_display.is_cropping:
            self.frame_display.stop_cropping()
            self.crop_button.config(text="Crop Image")
        else:
            self.frame_display.start_cropping()
            self.crop_button.config(text="Stop Cropping")

    def run_crystal_detection(self):
        """
        Run the crystal detection model on a specified range of frames.
        """
        # move this out of controller.
        start_frame = simpledialog.askinteger("Input", "Enter start frame:")
        end_frame = simpledialog.askinteger("Input", "Enter end frame:")

        if start_frame is not None and end_frame is not None:
            self.video_processor.detect_crystals_in_range(start_frame, end_frame)

    def show_original_frames(self):
        """
        Display the original video frames.
        """
        self.frame_display.show_original_frames()


    def show_hough_frames(self):
        """
        Display the video frames with hough transform applied.
        """
        # self.frame_display.show_hough_frames()
        self.frame_display.show_frames('hough')

    def show_contour_frames(self):
        """
        Display the video frames with contouring applied.
        """
        # self.frame_display.show_contour_frames()
        self.frame_display.show_frames('contour')

    def show_about(self):
        """
        Display the "about" information for the application.
        """
        messagebox.showinfo("About", "Phil's Crystal Analysis System\nVersion 1.0\nDeveloped by Phil")
