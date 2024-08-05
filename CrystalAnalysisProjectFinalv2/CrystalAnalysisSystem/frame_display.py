import cv2
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import simpledialog, messagebox


class FrameDisplay(tk.Frame):
    """
    Class for displaying and navigating through video frames.
    Handles frame display, navigation, and cropping functionality.
    """
    def __init__(self, master, video_processor, current_frame_var):
        super().__init__(master)

        # Setup
        self.video_processor = video_processor
        self.current_frame_index = 0
        self.current_frame_var = current_frame_var
        self.hold_next = False
        self.hold_prev = False
        self.frame_source = 'original'  # To track which frames to display
        self.crop_rect = None
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.scale_x = 1
        self.scale_y = 1
        self.is_cropping = False

        # Canvas setup
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(fill=tk.X)

        # Previous Button
        self.prev_button = tk.Button(self.controls_frame, text="Previous Frame")
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.prev_button.bind("<ButtonPress-1>", self.start_previous_frame)
        self.prev_button.bind("<ButtonRelease-1>", self.stop_previous_frame)

        # Next Button
        self.next_button = tk.Button(self.controls_frame, text="Next Frame")
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.next_button.bind("<ButtonPress-1>", self.start_next_frame)
        self.next_button.bind("<ButtonRelease-1>", self.stop_next_frame)

        # Move 10 frames. just get rid of this for now...
        """
        self.next_10_button = tk.Button(self.controls_frame, text=">>")
        self.next_10_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.next_10_button.bind("<ButtonPress-1>", self.start_next_frame)
        self.next_10_button.bind("<ButtonRelease-1>", self.stop_next_frame)

        self.prev_10_button = tk.Button(self.controls_frame, text="<<")
        self.prev_10_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.prev_10_button.bind("<ButtonPress-1>", self.start_previous_frame(1))
        self.prev_10_button.bind("<ButtonRelease-1>", self.stop_previous_frame)
        """

        # Bind canvas events for cropping
        self.canvas.bind("<ButtonPress-1>", self.on_crop_start)
        self.canvas.bind("<B1-Motion>", self.on_crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_crop_end)

    def update_canvas(self, frame):
        """
        Update the canvas with the given frame. See if this can be reused in crop display?
        """
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # converts to BGR to RGB
            img = Image.fromarray(frame_rgb)  # Creates image object

            # Get canvas and image dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = img.size
            self.scale_x = img_width / canvas_width  # Scaling X
            self.scale_y = img_height / canvas_height  # Scaling Y

            # Resize the image to fit the canvas
            if canvas_width / img_width < canvas_height / img_height:
                new_width = canvas_width
                new_height = int(img_height * canvas_width / img_width)
            else:
                new_height = canvas_height
                new_width = int(img_width * canvas_height / img_height)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Update scaling factors
            self.scale_x = img_width / new_width
            self.scale_y = img_height / new_height

            # Display image on canvas
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk
            self.current_frame_var.set(f"Frame: {self.current_frame_index}")

    def get_current_frame_list(self):
        """
        Return the list of frames based on the current frame source.
        """
        if self.frame_source == 'original':
            return self.video_processor.frames
        elif self.frame_source == 'hough':
            return self.video_processor.hough_frames
        elif self.frame_source == 'contour':
            return self.video_processor.contour_frames

    def show_previous_frame(self):
        """
        Show the previous frame in the sequence.
        """
        frame_list = self.get_current_frame_list()
        if self.current_frame_index > 0:
            self.current_frame_index -= 1
            frame = self.video_processor.get_frame(self.current_frame_index, frame_list)
            self.update_canvas(frame)
        if self.hold_prev:
            self.after(100, self.show_previous_frame)

    def show_next_frame(self):
        """
        Show the next frame in the sequence.
        """
        frame_list = self.get_current_frame_list()
        if self.current_frame_index < len(frame_list) - 1:
            self.current_frame_index += 1
            frame = self.video_processor.get_frame(self.current_frame_index, frame_list)
            self.update_canvas(frame)
        if self.hold_next:
            self.after(100, self.show_next_frame)

    def start_previous_frame(self, event):
        """
        Start showing previous frames continuously when button is held.
        """
        self.hold_prev = True
        self.show_previous_frame()

    def stop_previous_frame(self, event):
        """
        Stop showing previous frames when button is released.
        """
        self.hold_prev = False

    def start_next_frame(self, event):
        """
        Start showing next frames continuously when button is held.
        """
        self.hold_next = True
        self.show_next_frame()

    def stop_next_frame(self, event):
        """
        Stop showing next frames when button is released.
        """
        self.hold_next = False

    def show_frames(self, frame_source):  # show processed frames
        """
        Display frames based on the specified source.
        :param frame_source: A string specifying the type of frames to display ('original', 'hough', 'contour')
        """
        frame_list = getattr(self.video_processor, f"{frame_source}_frames", [])
        self.current_frame_index = 0
        if frame_list:
            self.update_canvas(self.video_processor.get_frame(self.current_frame_index, frame_list))

    def show_original_frames(self):
        """
        Show the original frames.
        """
        self.frame_source = 'original'
        self.current_frame_index = 0
        self.update_canvas(self.video_processor.get_frame(self.current_frame_index, self.video_processor.frames))

    def show_hough_frames(self):
        """
        Show the frames with hough transform applied.
        """
        self.frame_source = 'hough'
        self.current_frame_index = 0
        if self.video_processor.hough_frames:
            self.update_canvas(
                self.video_processor.get_frame(self.current_frame_index, self.video_processor.hough_frames))

    def show_contour_frames(self):
        """
        Show the frames with contouring applied.
        """
        self.frame_source = 'contour'
        self.current_frame_index = 0
        if self.video_processor.contour_frames:
            self.update_canvas(
                self.video_processor.get_frame(self.current_frame_index, self.video_processor.contour_frames))

    def start_cropping(self):
        """
        Start the cropping mode.
        """
        self.is_cropping = True

    def stop_cropping(self):
        self.is_cropping = False
        if self.crop_rect is not None:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None

    def on_crop_start(self, event):
        """
        Begin cropping operation by recording the starting coordinates.
        """
        if not self.is_cropping:
            return
        if self.crop_rect is not None:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None
        self.crop_start_x = event.x
        self.crop_start_y = event.y

    def on_crop_drag(self, event):
        """
        Update the cropping rectangle as the user drags the mouse.
        """
        if not self.is_cropping:
            return
        if self.crop_rect is not None:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y, event.x, event.y,
                                                      outline='red')

    def on_crop_end(self, event):
        """
        Complete the cropping operation and initiate the cropping process.
        """
        if not self.is_cropping:
            return
        x1 = min(self.crop_start_x, event.x)
        y1 = min(self.crop_start_y, event.y)
        x2 = max(self.crop_start_x, event.x)
        y2 = max(self.crop_start_y, event.y)

        frames_before = simpledialog.askinteger("Input", "Enter frames before to crop:")
        frames_after = simpledialog.askinteger("Input", "Enter frames after to crop:")

        # confirm crop box.
        if frames_before is not None and frames_after is not None:
            confirm = messagebox.askyesno("Confirm Crop",
                                          f"Crop area: ({x1}, {y1}), ({x2}, {y2})\nFrames before: {frames_before}\nFrames after: {frames_after}\nProceed with cropping?")
            if confirm:
                self.video_processor.crop_frames(x1, y1, x2, y2, frames_before, frames_after, self.scale_x,
                                                 self.scale_y)
                self.update_canvas(self.video_processor.get_frame(0, self.video_processor.frames))
