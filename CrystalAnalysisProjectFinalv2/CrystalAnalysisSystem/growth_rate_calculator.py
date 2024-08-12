import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
from tkinter import messagebox


class GrowthRateCalculator:
    """
    Class for calculating the growth rate based on given analysis data. PS 2024
    """
    def __init__(self, log_dir):
        self.log_dir = log_dir

    def calculate_growth_rate(self, crystal_data, use_hypotenuse=False):
        """
        Calculate and display the growth rate of crystals.

        If use_hypotenuse = True, it calculates growth rate based on the hypotenuse (width and height).
        If use_hypotenuse = False, it calculates growth rate based on width only.
        """
        df = pd.DataFrame(crystal_data)  # Convert crystal data to a pandas DataFrame

        if use_hypotenuse:
            # Calculate the hypotenuse (diagonal) for each crystal
            df['measurement'] = np.sqrt(df['width'] ** 2 + df['height'] ** 2)
            df_grouped = df.groupby('frame').agg({'measurement': 'sum', 'class': 'count'}).reset_index()
            df_grouped['average_measurement'] = df_grouped['measurement'] / df_grouped['class']  # Average hypotenuse
            base_filename = "yolo_crystal_analysis_data"
        else:
            # Use width as the measurement
            df['measurement'] = pd.to_numeric(df['width'], errors='coerce')
            df_grouped = df.groupby('frame').agg({'measurement': 'sum'}).reset_index()
            df_grouped['average_measurement'] = df_grouped['measurement']  # Since there's only one crystal
            base_filename = "opencv_crystal_analysis_data"

        # Calculate the actual change in measurement (in pixels) between frames
        df_grouped['pixel_change'] = df_grouped['measurement'].diff()

        # Convert pixel change to microns per frame
        df_grouped['micron_change'] = df_grouped['pixel_change'] * 0.25

        # Convert microns per frame to microns per second
        df_grouped['micron_per_second'] = df_grouped['micron_change'] * 8

        # Calculate the percentage change in measurement between frames to get the growth rate
        df_grouped['growth_rate'] = df_grouped['measurement'].pct_change() * 100

        # Calculate the average and median growth rate (percentage) and pixel change
        avg_growth_rate = df_grouped['growth_rate'].mean()
        med_growth_rate = df_grouped['growth_rate'].median()
        avg_pixel_change = df_grouped['pixel_change'].mean()
        med_pixel_change = df_grouped['pixel_change'].median()

        # Calculate the average and median micron change per second
        avg_micron_per_second = df_grouped['micron_per_second'].mean()
        med_micron_per_second = df_grouped['micron_per_second'].median()

        # Display the growth rate and actual pixel change
        messagebox.showinfo("Growth Rate",
                            f"Average Growth Rate: {avg_growth_rate:.2f}% or {avg_pixel_change:.2f} pixels/frame\n"
                            f"Median Growth Rate: {med_growth_rate:.2f}% or {med_pixel_change:.2f} pixels/frame\n"
                            f"Average Micron Change: {avg_micron_per_second:.2f} µm/s\n"
                            f"Median Micron Change: {med_micron_per_second:.2f} µm/s\n")

        # Generate a unique filename for log and graph files
        # Generate a unique filename for log and graph files
        log_file = self.generate_filename(self.log_dir, base_filename, extension=".csv")
        graph_file = self.generate_filename(self.log_dir, base_filename, extension=".png")

        messagebox.showinfo("Save Successful", f"Analysis data saved to" f" {log_file} and {graph_file}")

        # Save log to file
        df.to_csv(log_file, index=False)

        # Plot the growth rate (percentage)
        plt.plot(df_grouped['frame'], df_grouped['growth_rate'], marker='o')
        plt.xlabel('Frame')
        plt.ylabel('Growth Rate (%)')
        plt.title('Crystal Growth Rate Over Frames')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot as an image file BEFORE show.
        plt.savefig(graph_file)

        plt.show()

        plt.clf()  # Clear figure

        cv2.destroyAllWindows()

    def generate_filename(self, directory, base_name, extension):
        """
        Generate a unique filename by appending a number to the base_name if the file already exists.
        """
        counter = 1
        filename = f"{base_name}{extension}"
        file_path = os.path.join(directory, filename)

        # Loop to find a unique filename
        while os.path.exists(file_path):
            filename = f"{base_name}_{counter}{extension}"
            file_path = os.path.join(directory, filename)
            counter += 1

        return file_path

    # Simple Version of calculate_growth_rate below.

    # def calculate_growth_rate(self, crystal_data):
    #     """
    #     Calculate and display the growth rate of crystals.
    #     """
    #     df = pd.DataFrame(crystal_data)  # Convert crystal data to a pandas DataFrame
    #     df['size'] = df['width'] * df['height']   # Calculate the size of each crystal (width * height)
    #
    #     # Group the data by frame and sum the sizes to get the total size per frame
    #     df_grouped = df.groupby('frame').agg({'size': 'sum'}).reset_index()
    #
    #     # Calculate the percentage change in size between frames to get the growth rate
    #     df_grouped['growth_rate'] = df_grouped['size'].pct_change() * 100
    #
    #     average_growth_rate = df_grouped['growth_rate'].mean()
    #     messagebox.showinfo("Growth Rate", f"Average Growth Rate: {average_growth_rate:.2f}%")
    #
    #     # Save log to file
    #     log_file = os.path.join(self.log_dir, "crystal_analysis_data.csv")
    #     df.to_csv(log_file, index=False)
    #
    #     # Plot the growth rate
    #     plt.plot(df_grouped['frame'], df_grouped['growth_rate'], marker='o')
    #     plt.xlabel('Frame')
    #     plt.ylabel('Growth Rate (%)')
    #     plt.title('Crystal Growth Rate Over Frames')
    #     plt.xticks(rotation=45)
    #     plt.tight_layout()
    #     plt.show()
    #
    #     # Save the plot as an image file
    #     graph_file = os.path.join(self.log_dir, "crystal_growth_rate.png")
    #     plt.savefig(graph_file)
    #
    #     plt.show()
    #     cv2.destroyAllWindows()