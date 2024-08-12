from ultralytics import YOLO


class CrystalDetector:
    """
    Class for detecting crystals using a YOLO model. PS 2024
    """
    def __init__(self, model_path):
        self.model = YOLO(model_path)  # Gets custom YOLO model
        self.class_names = self.model.names

    def detect(self, image):
        """
        Detect crystals in the given image using the YOLO model.
        """
        results = self.model(image)[0]  # Applies custom model to image
        return results.boxes.data.tolist()
