"""
Module to encode text data into numerical format using OrdinalEncoder.
This module contains the Encode class, which provides methods to read a CSV file,
encode categorical columns, and save the encoded data to a new CSV file.
The encode_csv_data method reads a CSV file, encodes categorical columns using OrdinalEncoder,
and returns the encoded DataFrame and the fitted OrdinalEncoder.
The save_encoded_data method saves the encoded DataFrame to a CSV file.
The save_ordinal_encoder method saves the fitted OrdinalEncoder to a pickle file.
The run method orchestrates the encoding process by calling the encode_csv_data,
saving the encoded data, and saving the OrdinalEncoder.
"""

from typing import Tuple

import pickle
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder


class Encode:
    """
    Class to encode text data into numerical format.
    """

    @staticmethod
    def _encode_csv_data(
        x_cols: list, y_cols: list, transformed_data_path: str
    ) -> Tuple[pd.DataFrame, OrdinalEncoder]:
        """
        Reads a CSV file, encodes categorical columns using OrdinalEncoder,
        and returns the encoded DataFrame and the fitted OrdinalEncoder.
        Args:
            transformed_data_path (str): Path to the input CSV file.
        Returns:
            Tuple[pd.DataFrame, OrdinalEncoder]: A tuple containing the encoded DataFrame
            and the fitted OrdinalEncoder.
        """
        df = pd.read_csv(
            transformed_data_path, encoding="utf-8", low_memory=False
        )

        # Select only relevant columns from the DataFrame
        x_y_cols = x_cols + y_cols
        df = df[x_y_cols]

        categorical_columns = df.select_dtypes(include=["object"]).columns
        oe = OrdinalEncoder()
        df[categorical_columns] = oe.fit_transform(df[categorical_columns])

        # Limit df to 100000 rows (For testing purposes)
        if len(df) > 100000:
            df = df.sample(100000, random_state=42)

        return df, oe

    @staticmethod
    def _save_encoded_data(df: pd.DataFrame, encoded_data_path: str):
        """
        Saves the encoded DataFrame to a CSV file.
        Args:
            df (pd.DataFrame): The encoded DataFrame.
            encoded_data_path (str): Path to the output CSV file.
        """
        df.to_csv(encoded_data_path, index=False)

    @staticmethod
    def _save_ordinal_encoder(oe, ordinal_encoder_path: str):
        """
        Saves the fitted OrdinalEncoder to a pickle file.
        Args:
            oe (OrdinalEncoder): The fitted OrdinalEncoder.
            ordinal_encoder_path (str): Path to save the OrdinalEncoder.
        """
        if ".pkl" not in ordinal_encoder_path:
            ordinal_encoder_path += ".pkl"

        with open(ordinal_encoder_path, "wb") as f:
            pickle.dump(oe, f)

    def run(
        self,
        x_cols: list,
        y_cols: list,
        transformed_data_path: str,
        encoded_data_path: str,
        ordinal_encoder_path: str,
    ):
        """
        Orchestrates the encoding process by calling the encode_csv_data,
        saving the encoded data, and saving the OrdinalEncoder.
        """
        df, oe = self._encode_csv_data(x_cols, y_cols, transformed_data_path)
        self._save_encoded_data(df, encoded_data_path)
        self._save_ordinal_encoder(oe, ordinal_encoder_path)
