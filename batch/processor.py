import time

import requests
import pandas as pd


class FileProcessor:
    """
    A class to process files. This is a placeholder for the actual file processing logic.
    The process_file method should be implemented to handle the specific file processing needs.
    """

    def __init__(self, file_path: str, ml_host: str, ml_port: int):
        self.file_path = file_path
        self.ml_host = ml_host
        self.ml_port = ml_port

    def process_file(self, file_name: str):
        """
        Process the file with the given file_name.
        This method reads the file, processes it, and saves the result to a new file.
        Args:
            file_name (str): The name of the file to process.
        Returns:
            None
        """
        # Read the file
        file_path = f"{self.file_path}/{file_name}"
        print(f"Processing file: {file_path}")

        df = pd.read_excel(file_path, engine="openpyxl")
        print(f"DataFrame shape: {df.shape}")

        start = time.time()

        # Process the file
        for index, row in df.iterrows():
            response = requests.post(
                f"http://{self.ml_host}:{self.ml_port}/predict/onnx", json=row.to_dict()
            )
            if response.status_code == 200:
                prediction = response.json()
                # Update the DataFrame with the prediction result
                df.at[index, "predicted_price"] = prediction["predicted_price"]
            else:
                print(f"Error: {response.status_code} - {response.text}")

        print("File processing completed.")

        # Save the processed file
        output_file_name = f"processed_{file_name}"
        output_file_path = f"{self.file_path}/{output_file_name}"
        df.to_excel(output_file_path, index=False)

        print(f"Processed file saved as: {output_file_path}")

        end = time.time()

        print(f"Processing time: {end - start:.2f} seconds")


# if __name__ == "__main__":
#     # Example usage
#     file_processor = FileProcessor(file_path="data", ml_host="ml-inference", ml_port=5000)
#     file_processor.process_file("Book1.xlsx")
