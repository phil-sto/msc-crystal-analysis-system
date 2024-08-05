import unittest
import numpy as np

from CrystalAnalysisSystem.shape_analyser import ShapeAnalyser

class TestShapeAnalyser(unittest.TestCase):

    def setUp(self):
        self.image = np.zeros((480, 640, 3), dtype=np.uint8)
        self.shape_analyser = ShapeAnalyser(self.image)

    def test_resize_image(self):
        resized_image = self.shape_analyser.resize_image()
        self.assertTrue(resized_image.shape[1] <= 800 and resized_image.shape[0] <= 600)

    def test_process_image(self):
        width, height, angle = self.shape_analyser.process_image()
        self.assertIsNotNone(width)
        self.assertIsNotNone(height)
        self.assertIsNotNone(angle)

if __name__ == '__main__':
    unittest.main()