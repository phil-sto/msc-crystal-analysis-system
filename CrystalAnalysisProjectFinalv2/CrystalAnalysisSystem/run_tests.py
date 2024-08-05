import unittest

from unit_tests.test_video_processor import TestVideoProcessor
from unit_tests.test_frame_display import TestFrameDisplay
from unit_tests.test_crop_display import TestCropDisplay
from unit_tests.test_shape_analyser import TestShapeAnalyser
from unit_tests.test_controller import TestController

def make_suite():
    """
    make a unittest TestSuite object
        Returns
            (unittest.TestSuite)
    """
    suite = unittest.TestSuite()

    # Main App Tests
    suite.addTest(TestController('test_initialization'))
    suite.addTest(TestController('test_upload_video_command'))
    suite.addTest(TestController('test_run_crystal_detection'))
    suite.addTest(TestController('test_toggle_cropping'))

    # Video Processor Tests
    suite.addTest(TestVideoProcessor('test_upload_video'))
    suite.addTest(TestVideoProcessor('test_convert_to_frames'))
    suite.addTest(TestVideoProcessor('test_apply_hough_transform'))
    suite.addTest(TestVideoProcessor('test_apply_contouring'))

    # Frame Display Tests
    suite.addTest(TestFrameDisplay('test_show_previous_frame'))
    suite.addTest(TestFrameDisplay('test_show_next_frame'))
    suite.addTest(TestFrameDisplay('test_on_crop_start'))
    suite.addTest(TestFrameDisplay('test_on_crop_drag'))

    # Crop Display Tests
    suite.addTest(TestCropDisplay('test_initialization'))
    suite.addTest(TestCropDisplay('test_display_frame'))
    suite.addTest(TestCropDisplay('test_start_analysis'))
    suite.addTest(TestCropDisplay('test_stage_navigation'))

    # Shape Analyser Tests
    suite.addTest(TestShapeAnalyser('test_resize_image'))
    suite.addTest(TestShapeAnalyser('test_process_image'))

    return suite

def run_all_tests():
    """
    run all tests in the TestSuite
    """
    runner = unittest.TextTestRunner()
    runner.run(make_suite())

if __name__ == '__main__':
    run_all_tests()
