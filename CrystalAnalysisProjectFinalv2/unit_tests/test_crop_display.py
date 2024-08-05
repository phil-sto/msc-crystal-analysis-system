import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

from CrystalAnalysisSystem.shape_analyser import ShapeAnalyser
from CrystalAnalysisSystem.crop_display import CropDisplay


class TestCropDisplay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the root window

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.cropped_frames = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(5)]  # Create dummy frames
        self.video_processor = MagicMock()
        self.crop_display = CropDisplay(self.root, self.cropped_frames, self.video_processor)

    def tearDown(self):
        self.crop_display.destroy()

    def test_initial_setup(self):
        self.assertEqual(self.crop_display.current_frame_index, 0)
        self.assertEqual(self.crop_display.current_stage_index, 0)
        self.assertIsInstance(self.crop_display.canvas, tk.Canvas)
        self.assertIsInstance(self.crop_display.controls_frame, tk.Frame)

    def test_display_frame(self):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        self.crop_display.display_frame(frame)
        self.assertIsInstance(self.crop_display.canvas.image, ImageTk.PhotoImage)

    @patch('CrystalAnalysisSystem.utils.save_analysis_to_csv')
    def test_save_analysis_data(self, mock_save_analysis_to_csv):
        self.crop_display.analysis_data = [
            {'Frame Index': 0, 'Width': 50, 'Height': 50, 'Angle': 45},
            {'Frame Index': 1, 'Width': 60, 'Height': 60, 'Angle': 30}
        ]
        self.crop_display.save_analysis_data()
        self.assertTrue(mock_save_analysis_to_csv.called)

    def test_next_frame(self):
        self.crop_display.next_frame()
        self.assertEqual(self.crop_display.current_frame_index, 1)
        self.crop_display.next_frame()
        self.assertEqual(self.crop_display.current_frame_index, 2)

    def test_prev_frame(self):
        self.crop_display.current_frame_index = 2
        self.crop_display.prev_frame()
        self.assertEqual(self.crop_display.current_frame_index, 1)
        self.crop_display.prev_frame()
        self.assertEqual(self.crop_display.current_frame_index, 0)

    # @patch('CrystalAnalysisSystem.shape_analyser.ShapeAnalyser')
    # def test_update_for_new_frame(self, MockShapeAnalyser):
    #     mock_analyser = MockShapeAnalyser.return_value
    #     self.crop_display.update_for_new_frame()
    #     self.assertEqual(self.crop_display.current_stage_index, 0)
    #     self.assertTrue(isinstance(self.crop_display.analyser, MockShapeAnalyser))

    def test_show_next_stage(self):
        self.crop_display.stages = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(3)]
        self.crop_display.show_next_stage()
        self.assertEqual(self.crop_display.current_stage_index, 1)
        self.crop_display.show_next_stage()
        self.assertEqual(self.crop_display.current_stage_index, 2)

    def test_show_previous_stage(self):
        self.crop_display.stages = [np.zeros((100, 100, 3), dtype=np.uint8) for _ in range(3)]
        self.crop_display.current_stage_index = 2
        self.crop_display.show_previous_stage()
        self.assertEqual(self.crop_display.current_stage_index, 1)
        self.crop_display.show_previous_stage()
        self.assertEqual(self.crop_display.current_stage_index, 0)


if __name__ == '__main__':
    unittest.main()