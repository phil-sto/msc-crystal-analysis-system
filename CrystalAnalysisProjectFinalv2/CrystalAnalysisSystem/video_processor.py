import os

import cv2
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox

from CrystalAnalysisSystem.utils import apply_hough_transform, apply_contouring
from CrystalAnalysisSystem.crop_display import CropDisplay
from CrystalAnalysisSystem.crystal_detector import CrystalDetector


class VideoProcessor:
    """
    Handles video processing tasks such as uploading, frame extraction,
    applying hough transform, contouring, cropping, and crystal detection.
    """
    def __init__(self, frame_display, status_var, progress_bar):
        self.video_path = ""
        self.frames = []
        self.hough_frames = []
        self.contour_frames = []
        self.status_var = status_var
        self.progress_bar = progress_bar
        self.frame_display = frame_display
        self.cache_dir = "cache"
        self.log_dir = "log"

        self.detector = CrystalDetector(model_path='models/best.pt')  # Initialize the detector

        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def upload_video(self):
        """
        Open a file dialog to select a video file and convert it to frames.
        """
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov")]
        )
        if not self.video_path:
            messagebox.showerror("Error", "No video selected")
        else:
            self.convert_to_frames()

    def convert_to_frames(self):
        """
        Convert the selected video into individual frames.
        """
        if not self.video_path:
            messagebox.showerror("Error", "No video uploaded")
            return

        self.status_var.set("Converting video to frames...")
        cap = cv2.VideoCapture(self.video_path)
        self.frames = []
        self.hough_frames = []
        self.contour_frames = []
        frame_index = 0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.progress_bar["maximum"] = total_frames

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            self.frames.append(frame)
            frame_index += 1
            self.progress_bar["value"] = frame_index
            self.progress_bar.update()

        cap.release()
        self.status_var.set("Conversion Completed")
        self.progress_bar["value"] = 0

        messagebox.showinfo("Conversion Completed", f"Converted to {frame_index} frames")
        self.frame_display.update_canvas(self.get_frame(0, self.frames))

    def get_frame(self, index, frame_list):
        """
        Get a frame from the specified frame list by index.
        """
        if 0 <= index < len(frame_list):
            return frame_list[index]
        else:
            return None

    def get_total_frames(self):
        """
        Get the total number of frames in the video.
        """
        return len(self.frames)

    def apply_hough_to_frames(self):
        """
        Apply hough transform to all frames in the video.
        """
        self.status_var.set("Applying Hough Transform...")
        self.hough_frames = []

        for i, frame in enumerate(self.frames):
            processed_frame = apply_hough_transform(frame.copy())
            self.hough_frames.append(processed_frame)
            cv2.imwrite(os.path.join(self.cache_dir, f"hough_frame_{i}.png"), processed_frame)
            self.progress_bar["value"] = i + 1
            self.progress_bar.update()

        self.status_var.set("Hough Transform Applied")
        self.progress_bar["value"] = 0
        messagebox.showinfo("Hough Transform", "Hough Transform applied to all frames and saved to cache.")

    def apply_contour_to_frames(self):
        """
        Apply contouring to all frames in the video.
        """
        self.status_var.set("Applying Contouring...")
        self.contour_frames = []

        for i, frame in enumerate(self.frames):
            processed_frame = apply_contouring(frame.copy())
            self.contour_frames.append(processed_frame)
            cv2.imwrite(os.path.join(self.cache_dir, f"contour_frame_{i}.png"), processed_frame)
            self.progress_bar["value"] = i + 1
            self.progress_bar.update()

        self.status_var.set("Contouring Applied")
        self.progress_bar["value"] = 0
        messagebox.showinfo("Contouring", "Contouring applied to all frames and saved to cache.")

    def crop_frames(self, x1, y1, x2, y2, frames_before, frames_after, scale_x, scale_y):
        """
        Crop frames within a specified range and save them to the cache directory. For use with YOLO crystal detection.
        """
        self.status_var.set("Cropping frames...")
        cropped_frames = []

        start_index = max(0, self.frame_display.current_frame_index - frames_before)
        end_index = min(len(self.frames), self.frame_display.current_frame_index + frames_after + 1)

        # Scale crop coordinates back to original image size
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)

        for i in range(start_index, end_index):
            frame = self.frames[i]
            cropped_frame = frame[y1:y2, x1:x2]
            cropped_frames.append(cropped_frame)
            cv2.imwrite(os.path.join(self.cache_dir, f"cropped_frame_{i}.png"), cropped_frame)

        self.status_var.set("Cropping Completed")
        messagebox.showinfo("Cropping Completed", f"Cropped frames from index {start_index} to {end_index - 1}")

        # Pass all cropped frames to CropDisplay for analysis
        if cropped_frames:
            CropDisplay(self.frame_display.master, cropped_frames, self)

    def detect_crystals_in_range(self, start_frame, end_frame):
        """
        Detect crystals in the specified range of frames.
        """
        # Check if there are frames to process.
        if not self.frames:
            messagebox.showerror("Error", "No frames available")
            return

        # validate provided frame range
        if start_frame < 0 or end_frame >= len(self.frames) or start_frame > end_frame:
            messagebox.showerror("Error", "Invalid frame range")
            return

        # updates status bar
        self.status_var.set("Detecting crystals...")
        crystal_data = []

        # loop through each frame in range
        for i in range(start_frame, end_frame + 1):
            frame = self.frames[i]
            detections = self.detector.detect(frame)
            # process each detection in current form
            for detection in detections:
                x1, y1, x2, y2, _, class_id = detection  # unpack
                width = x2 - x1
                height = y2 - y1
                crystal_data.append({
                    'frame': i,
                    'class': self.detector.class_names[int(class_id)],
                    'width': width,
                    'height': height
                })

                # Draw detection boxes on the frame
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                # adds label with class name and dimensions of crystal
                # cv2.putText(frame, f'{self.detector.class_names[int(class_id)]} ({width}x{height})',
                #             (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(frame, f'{self.detector.class_names[int(class_id)]}',
                            (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the frame with detections
            self.frame_display.update_canvas(frame)
            self.frame_display.master.update_idletasks()
            self.frame_display.master.update()

        # update status to show complete
        self.status_var.set("Detection completed")
        # calculate growth rate
        self.calculate_growth_rate(crystal_data)

    def calculate_growth_rate(self, crystal_data):
        """
        Calculate and display the growth rate of crystals. Maybe move to its own class
        """
        df = pd.DataFrame(crystal_data)  # Convert crystal data to a pandas DataFrame
        df['size'] = df['width'] * df['height']   # Calculate the size of each crystal (width * height)

        # Group the data by frame and sum the sizes to get the total size per frame
        df_grouped = df.groupby('frame').agg({'size': 'sum'}).reset_index()

        # Calculate the percentage change in size between frames to get the growth rate
        df_grouped['growth_rate'] = df_grouped['size'].pct_change() * 100

        average_growth_rate = df_grouped['growth_rate'].mean()
        messagebox.showinfo("Growth Rate", f"Average Growth Rate: {average_growth_rate:.2f}%")

        # Save log to file
        log_file = os.path.join(self.log_dir, "crystal_analysis_data.csv")
        df.to_csv(log_file, index=False)

        # Plot the growth rate
        import matplotlib.pyplot as plt
        plt.plot(df_grouped['frame'], df_grouped['growth_rate'], marker='o')
        plt.xlabel('Frame')
        plt.ylabel('Growth Rate (%)')
        plt.title('Crystal Growth Rate Over Frames')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # Save the plot as an image file
        graph_file = os.path.join(self.log_dir, "crystal_growth_rate.png")
        plt.savefig(graph_file)

        plt.show()
        cv2.destroyAllWindows()