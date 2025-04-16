from const import Columns
from encode import Encode
from train import Train


def main():
    x_cols = Columns.X
    y_cols = [Columns.TARGET]

    pre_fix = "ml/data/"

    for model_group in ["A.csv", "B.csv", "C.csv"]:
        print(f"Processing model group: {model_group}")

        transformed_data_path = f"{pre_fix}/transformed-data/{model_group}"  # csv path
        encoded_data_path = f"{pre_fix}/encoded-data/encoded_{model_group}"  # csv path
        ordinal_encoder_path = f"{pre_fix}/encoder/ordinal_encoder_{model_group}".replace(
            ".csv", ".pkl"
        )  # pkl path

        # Initialize the Encode class and run the encoding process
        Encode().run(
            x_cols,
            y_cols,
            transformed_data_path,
            encoded_data_path,
            ordinal_encoder_path,
        )

        onnx_path = f"{pre_fix}/models/model_{model_group}".replace(".csv", ".onnx")
        pkl_path = f"{pre_fix}/models/model_{model_group}".replace(".csv", ".pkl")

        # Initialize the Train class and run the training process
        Train().run(encoded_data_path, x_cols, y_cols, onnx_path, pkl_path)

        print(f"Finished processing model group: {model_group}")


if __name__ == "__main__":
    main()
