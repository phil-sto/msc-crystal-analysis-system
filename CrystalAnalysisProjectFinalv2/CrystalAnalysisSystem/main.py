"""
Project Name: Phil's Crystal Analysis System
Description: A prototype crystal analysis tool, utilising OpenCV image processing, Hough Transformation and
YOLO Object Detection to demonstrate the use of artificial intelligence techniques in image analysis / crystal growth
analysis.
Date Finalised: 2024-08-12
Author: Philip Stokes (Student No. 201260120)
GitHub:

Version: 3.0
Institution: University of Leeds
Purpose: This application is intended to be developed in combination with a project report
to demonstrate "the use of artificial intelligence techniques for the analysis of crystal growth"
"""

from CrystalAnalysisSystem.controller import CrystalAnalysisController

"""
    Please Run From Here!
"""

if __name__ == "__main__":
    app = CrystalAnalysisController()
    app.mainloop()
