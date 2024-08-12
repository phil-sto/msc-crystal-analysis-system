import csv
import cv2
import numpy as np

"""
Helper functions. PS 2024
"""


def apply_hough_transform(image):
    """
    Apply hough transform to detect lines in the given image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    edges = cv2.Canny(blurred, 100, 200)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    lines = cv2.HoughLinesP(closed, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
    return lines


def apply_contouring(image):
    """
    Detect and draw contours of crystals in the given image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    edges = cv2.Canny(blurred, 100, 200)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def filter_regions(contours):
    """
    Filter contours based on a specified area threshold.
    """
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # Filter based on area threshold
            filtered_contours.append(contour)
    return filtered_contours


def combine_results(image):
    """
    Combine the results of hough transform and contour detection to create a final image.
    """
    lines = apply_hough_transform(image)
    contours = apply_contouring(image)
    contours = filter_regions(contours)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) > 6 and cv2.contourArea(contour) > 100:
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)

    # Create bounding box from combined results
    x_min, y_min, x_max, y_max = float('inf'), float('inf'), float('-inf'), float('-inf')
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            x_min = min(x_min, x1, x2)
            y_min = min(y_min, y1, y2)
            x_max = max(x_max, x1, x2)
            y_max = max(y_max, y1, y2)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)

    width = x_max - x_min
    height = y_max - y_min

    return image, (x_min, y_min, width, height)

# def preprocess_image(image):
#     """
#     preprocess the image for further analysis.
#     """
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (11, 11), 0)
#     edges = cv2.Canny(blurred, 50, 150)
#     kernel = np.ones((5, 5), np.uint8)
#     dilated = cv2.dilate(edges, kernel, iterations=1)
#     closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
#     return closed
