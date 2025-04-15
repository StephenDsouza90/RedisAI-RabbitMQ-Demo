"""
Constants for the ETL process.
This module contains constants used throughout the ETL process, including
column names, categorical and numerical columns, and the request model for inference.
"""

from pydantic import BaseModel


class Columns:
    """
    Class to hold column names for the dataset.
    """

    # Target variable
    TARGET = "price_in_local_currency"

    # Independent variables
    X = [
        "model",
        "kilometers",
        "fuel_type",
        "gear_type",
        "vehicle_type",
        "age_in_months",
        "color",
        "line",
        "doors",
        "seats",
        "climate",
    ]


class CategoricalColumns:
    """
    Class to hold categorical column names for the dataset.
    """

    FUEL_TYPE = "fuel_type"
    GEAR_TYPE = "gear_type"
    VEHICLE_TYPE = "vehicle_type"
    COLOR = "color"
    LINE = "line"
    DOORS = "doors"
    SEATS = "seats"
    CLIMATE = "climate"

    def to_list(self):
        """
        Convert the categorical column names to a list.
        """
        return [
            self.FUEL_TYPE,
            self.GEAR_TYPE,
            self.VEHICLE_TYPE,
            self.COLOR,
            self.LINE,
            self.DOORS,
            self.SEATS,
            self.CLIMATE,
        ]


class NumericalColumns:
    """
    Class to hold numerical column names for the dataset.
    """

    MODEL = "model"
    KILOMETERS = "kilometers"
    AGE_IN_MONTHS = "age_in_months"

    def to_list(self):
        """
        Convert the numerical column names to a list.
        """
        return [self.MODEL, self.KILOMETERS, self.AGE_IN_MONTHS]


class ModelInferenceRequest(BaseModel):
    """
    Request model for inference.
    """

    model_group: str = "A"
    model: int = 180
    kilometers: int = 5000
    fuel_type: str = "Diesel"
    gear_type: str = "Manual"
    vehicle_type: str = "Sedan Car"
    age_in_months: int = 12
    color: str = "Black"
    line: str = "Sportline"
    doors: str = "4 to 5"
    seats: str = "1 to 3"
    climate: str = "Air Conditioning"

    @classmethod
    def validate_keys(cls):
        """
        Ensure that the keys in the model match the categorical and numerical columns.
        """
        categorical_keys = CategoricalColumns().to_list()
        numerical_keys = NumericalColumns().to_list()
        all_keys = categorical_keys + numerical_keys

        request_keys = [
            field
            for field in cls.__annotations__.keys()
            if field not in ["model_group"]
        ]
        missing_keys = set(all_keys) - set(request_keys)
        extra_keys = set(request_keys) - set(all_keys)

        if missing_keys:
            raise ValueError(f"Missing keys in ModelInferenceRequest: {missing_keys}")
        if extra_keys:
            raise ValueError(f"Extra keys in ModelInferenceRequest: {extra_keys}")
