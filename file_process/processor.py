import pandas as pd


class FileProcessor:
    """
    A class to process files. This is a placeholder for the actual file processing logic.
    The process_file method should be implemented to handle the specific file processing needs.
    """
    @staticmethod
    def process_file(filename):
        """
        Process the file with the given filename.
        This method reads the file, processes it, and saves the result to a new file.

        Args:
            filename (str): The name of the file to process.
        
        Returns:
            None
        """
        filepath = f"/data/{filename}"
        content = pd.read_excel(filepath, engine="openpyxl")
        new_filename = f"processed_{filename}"
        content.to_excel(f"/data/{new_filename}", index=False)
