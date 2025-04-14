"""
Module to train a Random Forest model and save it in different formats.
This module contains the Train class, which provides methods to load data,
train a Random Forest model, and save the trained model in different formats.
The load_data method reads a CSV file and returns a DataFrame.
The train_model method trains a Random Forest model on the provided DataFrame
and evaluates its performance using Mean Squared Error.
The save_model_with_pkl method saves the model using pickle format.
The save_model_with_joblib method saves the model using joblib format.
The save_model_with_onnx method saves the model using ONNX format.
The run method orchestrates the training process by loading the data,
training the model, and saving it in different formats.
"""

import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


class Train:
    """
    Class to train a Random Forest model and save it in different formats.
    """

    @staticmethod
    def _load_data(encoded_data_path: str) -> pd.DataFrame:
        """
        Load the encoded data from a CSV file.

        Args:
            encoded_data_path (str): Path to the encoded CSV file.
        
        Returns:
            pd.DataFrame: The loaded DataFrame.
        """
        return pd.read_csv(encoded_data_path)
    
    @staticmethod
    def _train_model(df: pd.DataFrame, x_cols: list, y_cols: list) -> RandomForestRegressor:
        """
        Train a Random Forest model on the provided DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing the data.
            x_cols (list): List of feature column names.
            y_cols (list): List of target column names.
        
        Returns:
            RandomForestRegressor: The trained Random Forest model.
        """
        # Split the data into features and target
        X = df.drop(columns=y_cols)
        y = df[y_cols]

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the Random Forest model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        print(f"Model Score: {model.score(X_test, y_test)}")

        return model

    @staticmethod
    def _save_model_with_onnx(model: RandomForestRegressor, x_cols: list, file_path: str):
        """
        Save the model using ONNX format.

        Args:
            model (RandomForestRegressor): The trained Random Forest model.
            x_cols (list): List of feature column names.
            file_path (str): Path to save the model.
        """
        if ".onnx" not in file_path:
            file_path += ".onnx"

        initial_type = [('float_input', FloatTensorType([None, len(x_cols)]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type, target_opset=8) # ONNX opset version 8 is used

        with open(file_path, 'wb') as f:
            f.write(onnx_model.SerializeToString())

    @staticmethod
    def _save_model_with_pkl(model: RandomForestRegressor, file_path: str):
        """
        Save the model using pickle format.

        Args:
            model (RandomForestRegressor): The trained Random Forest model.
            file_path (str): Path to save the model.
        """

        if ".pkl" not in file_path:
            file_path += ".pkl"

        with open(file_path, 'wb') as f:
            pickle.dump(model, f)

    def run(self, encoded_data_path: str, x_cols: list, y_cols: list, onnx_path: str, pkl_path):
        """
        Orchestrates the training process by loading the data,
        training the model, and saving it in different formats.
        """
        df = self._load_data(encoded_data_path)
        model = self._train_model(df, x_cols, y_cols)

        self._save_model_with_onnx(model, x_cols, onnx_path)
        self._save_model_with_pkl(model, pkl_path)
