import unittest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch

from CrystalAnalysisSystem.video_processor import VideoProcessor


class TestVideoProcessor(unittest.TestCase):

    def setUp(self):
        # Mock the CrystalDetector to avoid loading the model
        with patch('CrystalAnalysisSystem.video_processor.CrystalDetector') as MockDetector:
            self.mock_detector = MockDetector.return_value
            self.video_processor = VideoProcessor(MagicMock(), MagicMock(), MagicMock())
            self.sample_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    @patch('CrystalAnalysisSystem.video_processor.filedialog.askopenfilename', return_value='test_video.mp4')
    def test_upload_video(self, mock_filedialog):
        """
        tests if the video processor "upload_video" method sets the video_path correctly.
        :param mock_filedialog:
        :return:
        """
        self.video_processor.upload_video()
        self.assertEqual(self.video_processor.video_path, 'test_video.mp4')

    def test_convert_to_frames(self):
        # Mocking cv2.VideoCapture and its read method
        with patch('cv2.VideoCapture') as MockVideoCapture:
            mock_video_capture_instance = MockVideoCapture.return_value
            mock_video_capture_instance.read.side_effect = [
                (True, self.sample_frame),  # First call returns a valid frame
                (False, None)  # Second call simulates end of video
            ]

            self.video_processor.convert_to_frames()

            # Check if frames were added to the frames list
            self.assertEqual(len(self.video_processor.frames), 1)
            # Additional check to ensure the frame data matches
            np.testing.assert_array_equal(self.video_processor.frames[0], self.sample_frame)

    def test_apply_hough_transform(self):
        self.video_processor.frames = [self.sample_frame]
        self.video_processor.apply_hough_to_frames()
        self.assertEqual(len(self.video_processor.hough_frames), 1)

    def test_apply_contouring(self):
        self.video_processor.frames = [self.sample_frame]
        self.video_processor.apply_contour_to_frames()
        self.assertEqual(len(self.video_processor.contour_frames), 1)


if __name__ == '__main__':
    unittest.main()
