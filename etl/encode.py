"""
This module provides a class to encode text data into numerical format using OrdinalEncoder from sklearn.
It reads a CSV file, encodes the categorical columns, and saves the encoded data to a new CSV file.
"""

import pickle
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder


class Encode:
    """
    Class to encode text data into numerical format.
    """

    def __init__(self, input_csv: str, output_csv: str, ordinal_encoder: str):
        """
        Initialize the Encode class with input and output CSV file paths.

        :param input_csv: Path to the input CSV file.
        :param output_csv: Path to the output CSV file.
        """
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.ordinal_encoder = ordinal_encoder

    def encode(self):
        """
        Read the CSV file, encode the text data, and save it to a new CSV file.
        """
        # Read the CSV file
        df = pd.read_csv(self.input_csv)

        # Lowercase all column names
        df.columns = df.columns.str.lower()

        # Using OrdinalEncoder for all categorical columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        oe = OrdinalEncoder()
        df[categorical_columns] = oe.fit_transform(df[categorical_columns])

        # Save the encoded DataFrame to a new CSV file
        df.to_csv(self.output_csv, index=False)

        # Save the encoder
        with open(self.ordinal_encoder, 'wb') as f:
            pickle.dump(oe, f)