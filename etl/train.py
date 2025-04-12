"""
"""

import pickle
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


class Train:
    """
    """

    def __init__(self, input_csv: str):
        """
        """
        self.input_csv = input_csv

    def load_data(self):
        """
        """
        return pd.read_csv(self.input_csv)
    
    def train_model(self, df: pd.DataFrame) -> RandomForestRegressor:
        """
        """

        # Split the data into features and target
        X = df.drop(columns=['Price'])
        y = df['Price']

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the Random Forest model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean Squared Error: {mse}")

        return model

    def save_model_with_pkl(self, model: RandomForestRegressor):
        """
        """
        model = pickle.dumps(model)
        with open("model_with_pkl.pkl", 'wb') as f:
            f.write(model)

    def save_model_with_joblib(self, model: RandomForestRegressor):
        """
        """
        with open("model_with_joblib.pkl", 'wb') as f:
            joblib.dump(model, f)

    def save_model_with_onnx(self, model: RandomForestRegressor):
        """
        Save the model using ONNX format.
        """
        total_cols = len(model.feature_importances_)
        target_opset = 8
        initial_type = [('float_input', FloatTensorType([None, total_cols]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type, target_opset=target_opset)
        with open("model_with_onnx.onnx", 'wb') as f:
            f.write(onnx_model.SerializeToString())

    def run(self):
        """
        """
        # Load the data
        df = self.load_data()

        # Train the model
        model = self.train_model(df)

        # Save the model
        self.save_model_with_pkl(model)
        self.save_model_with_joblib(model)
        self.save_model_with_onnx(model)
