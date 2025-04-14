from encode import Encode
from train import Train


def main():

    # NOTE: Testing IT data with only 3 model groups

    x_cols = ["model", "kilometers", "fueltype", "geartype", "vehicletype", "ageinmonths", "color", "line", "doors", "seats", "climate"]
    y_cols = ["priceinlocalcurrency"]

    model_groups = [("A.csv", "180")]
    for model_group, model in model_groups:
        print(f"Processing model group: {model_group}")

        transformed_data_path = model_group # csv path
        encoded_data_path = f"encoded_{model_group}" # csv path
        ordinal_encoder_path = f"ordinal_encoder_{model_group}".replace(".csv", ".pkl") # pkl path

        # Initialize the Encode class and run the encoding process
        Encode().run(x_cols, y_cols, transformed_data_path, encoded_data_path, ordinal_encoder_path, model)

        onnx_path = f"model_{model_group}".replace(".csv", ".onnx")
        pkl_path = f"model_{model_group}".replace(".csv", ".pkl")

        # Initialize the Train class and run the training process
        Train().run(encoded_data_path, x_cols, y_cols, onnx_path, pkl_path)

        print(f"Finished processing model group: {model_group}")


if __name__ == "__main__":
    main()