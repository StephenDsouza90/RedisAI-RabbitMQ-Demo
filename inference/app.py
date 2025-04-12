from inference.main import API

ordinal_encoder_path = '/data/ordinal_encoder.pkl'

backend = API(ordinal_encoder_path)
app = backend.app
