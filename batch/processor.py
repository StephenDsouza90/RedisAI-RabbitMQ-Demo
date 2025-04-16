"""
File Processor Module
This module defines a FileProcessor class that handles the processing of files.
It includes methods for loading files, sending data to a machine learning service,
and saving the processed files.
"""

import time

import requests
import pandas as pd


class FileProcessor:
    """
    A class to handle file processing tasks, including reading, processing, and saving files.
    The processing involves sending data to a machine learning service for predictions.
    """

    def __init__(self, file_directory: str, ml_url: str):
        """
        Initialize the FileProcessor with the file directory and ML service details.

        Args:
            file_directory (str): Directory where the files are located.
            ml_url (str): URL of the machine learning service for processing files.
        """
        self.file_directory = file_directory
        self.ml_url = ml_url

    def process_file(self, file_name: str):
        """
        Process the specified file by sending its rows to a machine learning service for predictions.

        Args:
            file_name (str): Name of the file to process.

        Returns:
            None
        """
        file_path = f"{self.file_directory}/{file_name}"
        print(f"Starting processing for file: {file_path}")

        # Load the file into a DataFrame
        try:
            data_frame = pd.read_excel(file_path, engine="openpyxl")
            print(f"Loaded file with shape: {data_frame.shape}")
        except Exception as e:
            print(f"Error loading file: {e}")
            return

        start_time = time.time()

        # Process each row in the DataFrame
        for index, row in data_frame.iterrows():
            try:
                response = requests.post(self.ml_url, json=row.to_dict())
                if response.status_code == 200:
                    prediction = response.json()
                    data_frame.at[index, "predicted_price"] = prediction.get("predicted_price", None)
                else:
                    print(f"Error for row {index}: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                print(f"Request error for row {index}: {e}")

        print("File processing completed.")

        # Save the processed DataFrame to a new file
        output_file_name = f"processed_{file_name}"
        output_file_path = f"{self.file_directory}/{output_file_name}"
        try:
            data_frame.to_excel(output_file_path, index=False)
            print(f"Processed file saved at: {output_file_path}")
        except Exception as e:
            print(f"Error saving processed file: {e}")

        end_time = time.time()
        print(f"Total processing time: {end_time - start_time:.2f} seconds")
