import cv2
import numpy as np
from math import radians, atan2, degrees


class ShapeAnalyser:
    """
    Class for analyzing the shape of crystals in the image using OpenCV pre-processing and hough transform. PS 2024
    """
    def __init__(self, image):
        self.original_image = image
        self.stages = []

    def resize_image(self, max_width=800, max_height=600):
        """
        Resize the image to fit within the specified dimensions while maintaining the aspect ratio.
        """
        height, width = self.original_image.shape[:2]
        aspect_ratio = width / height

        if width > max_width or height > max_height:
            if width > height:
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
            resized_image = cv2.resize(self.original_image, (new_width, new_height))
        else:
            resized_image = self.original_image

        self.stages.append(resized_image)
        return resized_image

    def rotate_point(self, point, angle, center):
        """
        Rotate a point around a given center.
        """
        angle_rad = radians(angle)
        ox, oy = center
        px, py = point

        qx = ox + np.cos(angle_rad) * (px - ox) - np.sin(angle_rad) * (py - oy)
        qy = oy + np.sin(angle_rad) * (px - ox) + np.cos(angle_rad) * (py - oy)
        return int(qx), int(qy)

    def draw_rotated_box(self, image, rect):
        """
        Draw a rotated bounding box on the image.
        """
        box = cv2.boxPoints(rect)
        box = np.intp(box)  # should be intp I think.
        cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
        self.stages.append(image)

    def preprocess_image(self, resized_image):
        """
        Preprocess the image for bounding box calculation.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        self.stages.append(gray)

        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        self.stages.append(enhanced)

        # Apply Gaussian Blur
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        self.stages.append(blurred)

        # Apply Adaptive Thresholding
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        self.stages.append(thresh)

        # Apply Morphological Transformations (Closing)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        self.stages.append(closed)

        # Perform Canny edge detection
        edges = cv2.Canny(closed, 50, 150)
        self.stages.append(edges)

        return edges

    def calculate_bounding_box(self, resized_image, edges):
        """
        Draw and rotate the bounding box on the processed image.
        """
        # Perform Hough Line Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10)
        line_image = np.copy(resized_image) * 0

        # Extract Line Coordinates and Draw Lines:
        x_coords = []
        y_coords = []
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    x_coords.extend([x1, x2])
                    y_coords.extend([y1, y2])

        # Combine Original and Line Images
        combined_image = cv2.addWeighted(resized_image, 0.8, line_image, 1, 0)
        self.stages.append(combined_image)

        # Get the bounding box coordinates by finding extremes
        if x_coords and y_coords:
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)

            # Determine the furthest points on the x-axis
            furthest_points = [(x_coords[i], y_coords[i]) for i in range(len(x_coords))]
            max_distance = 0
            point1, point2 = (0, 0), (0, 0)
            for i in range(len(furthest_points)):
                for j in range(i + 1, len(furthest_points)):
                    dist = np.linalg.norm(np.array(furthest_points[i]) - np.array(furthest_points[j]))
                    if dist > max_distance:
                        max_distance = dist
                        point1, point2 = furthest_points[i], furthest_points[j]

            # Calculate the angle of the line connecting the furthest points
            angle = degrees(atan2(point2[1] - point1[1], point2[0] - point1[0]))

            # Rotate all points based on the calculated angle
            center = ((x_min + x_max) / 2, (y_min + y_max) / 2)
            rotated_coords = [self.rotate_point((x, y), -angle, center) for x, y in zip(x_coords, y_coords)]

            # Get the bounding box coordinates of the rotated points
            if rotated_coords:
                rotated_x_coords, rotated_y_coords = zip(*rotated_coords)
                rotated_x_min, rotated_x_max = min(rotated_x_coords), max(rotated_x_coords)
                rotated_y_min, rotated_y_max = min(rotated_y_coords), max(rotated_y_coords)

                # Rotate the bounding box
                rotated_width = rotated_x_max - rotated_x_min
                rotated_height = rotated_y_max - rotated_y_min
                rotated_box = ((center[0], center[1]), (float(rotated_width), float(rotated_height)), float(angle))

                # Draw the rotated bounding box
                final_image = resized_image.copy()
                self.draw_rotated_box(final_image, rotated_box)

                # Print dimensions
                print(f"Width: {rotated_width}, Height: {rotated_height}")
                print(f"Rotated Bounding Box Angle: {angle}")

                return rotated_width, rotated_height, angle

        return None, None, None

    def process_image(self):
        """
        Method for running both pre-processing steps and drawing bounding boxes.
        :return: Processed Image and Hough Transform edges.
        """
        resized_image = self.resize_image()
        edges = self.preprocess_image(resized_image)
        return self.calculate_bounding_box(resized_image, edges)