from encode import Encode
from train import Train


def main():
    input_csv = "input.csv"
    output_csv = "output.csv"
    ordinal_encoder = 'ordinal_encoder.pkl' 
    encoder = Encode(input_csv, output_csv, ordinal_encoder)
    encoder.encode()

    trainer = Train(output_csv)
    trainer.run()


if __name__ == "__main__":
    main()