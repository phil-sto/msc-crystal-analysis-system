import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import numpy as np

# Correct imports from your working package
from CrystalAnalysisSystem.controller import CrystalAnalysisController
from CrystalAnalysisSystem.video_processor import VideoProcessor

class TestController(unittest.TestCase):

    @patch('CrystalAnalysisSystem.video_processor.CrystalDetector')
    def setUp(self, MockCrystalDetector):
        # Mock the CrystalDetector to avoid loading the model
        self.mock_detector = MockCrystalDetector.return_value
        self.app = CrystalAnalysisController()

    def test_initialization(self):
        self.assertIsInstance(self.app, CrystalAnalysisController)
        self.assertIsNotNone(self.app.menu_bar)
        self.assertIsNotNone(self.app.status_var)
        self.assertIsNotNone(self.app.current_frame_var)

    def test_upload_video_command(self):
        with patch.object(self.app.video_processor, 'upload_video') as mock_upload_video:
            self.app.upload_video()
            mock_upload_video.assert_called_once()

    @patch('CrystalAnalysisSystem.controller.simpledialog.askinteger', return_value=1)
    def test_run_crystal_detection(self, mock_askinteger):
        with patch.object(self.app.video_processor, 'detect_crystals_in_range') as mock_detect:
            self.app.run_crystal_detection()
            mock_detect.assert_called_once()

    def test_toggle_cropping(self):
        self.assertFalse(self.app.frame_display.is_cropping)
        self.app.toggle_cropping()
        self.assertTrue(self.app.frame_display.is_cropping)
        self.assertEqual(self.app.crop_button['text'], 'Stop Cropping')
        self.app.toggle_cropping()
        self.assertFalse(self.app.frame_display.is_cropping)
        self.assertEqual(self.app.crop_button['text'], 'Crop Image')

if __name__ == '__main__':
    unittest.main()