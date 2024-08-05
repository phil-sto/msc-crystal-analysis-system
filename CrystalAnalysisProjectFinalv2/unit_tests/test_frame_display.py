import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import numpy as np

# imports modules from working package
from CrystalAnalysisSystem.frame_display import FrameDisplay

# This works!

class TestFrameDisplay(unittest.TestCase):

    def setUp(self):
        # Create a root window for the tkinter frame
        self.root = tk.Tk()

        # Mock the video processor with necessary methods
        self.mock_video_processor = MagicMock()
        self.mock_video_processor.get_frame = MagicMock(return_value=None)
        self.mock_video_processor.frames = [MagicMock() for _ in range(10)]  # Assuming 10 frames

        # Variable to hold the current frame index
        self.current_frame_var = tk.StringVar()

        # Initialize the FrameDisplay with the mocked video processor
        self.frame_display = FrameDisplay(self.root, self.mock_video_processor, self.current_frame_var)

    def tearDown(self):
        # Destroy the tkinter root window after each test
        self.root.destroy()

    def test_show_previous_frame(self):
        # Set initial frame index to a valid number greater than 0
        self.frame_display.current_frame_index = 5
        self.frame_display.show_previous_frame()

        # Check if the get_frame method was called correctly
        self.mock_video_processor.get_frame.assert_called_with(4, self.mock_video_processor.frames)

        # Check if the current frame index was decremented
        self.assertEqual(self.frame_display.current_frame_index, 4)

    def test_show_next_frame(self):
        # Set initial frame index to a valid number less than the number of frames - 1
        self.frame_display.current_frame_index = 5
        self.frame_display.show_next_frame()

        # Check if the get_frame method was called correctly
        self.mock_video_processor.get_frame.assert_called_with(6, self.mock_video_processor.frames)

        # Check if the current frame index was incremented
        self.assertEqual(self.frame_display.current_frame_index, 6)

    def test_update_canvas(self):
        # test update canvas method maybe???
        pass

    def test_on_crop_start(self):
        event = MagicMock()
        event.x = 10
        event.y = 20
        self.frame_display.is_cropping = True
        self.frame_display.on_crop_start(event)
        self.assertEqual(self.frame_display.crop_start_x, 10)
        self.assertEqual(self.frame_display.crop_start_y, 20)

    def test_on_crop_end(self):
        # test on crop end.
        pass

    def test_on_crop_drag(self):
        event = MagicMock()
        event.x = 100
        event.y = 200
        self.frame_display.is_cropping = True
        self.frame_display.crop_rect = None
        with patch.object(self.frame_display.canvas, 'create_rectangle') as mock_create_rectangle:
            self.frame_display.on_crop_drag(event)
            mock_create_rectangle.assert_called_once_with(self.frame_display.crop_start_x, self.frame_display.crop_start_y, event.x, event.y, outline='red')

if __name__ == '__main__':
    unittest.main()
