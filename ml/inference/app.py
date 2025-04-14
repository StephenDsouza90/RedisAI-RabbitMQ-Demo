from ml.inference.main import API

x_cols = ["model", "kilometers", "fueltype", "geartype", "vehicletype", "ageinmonths", "color", "line", "doors", "seats", "climate"]
y_cols = ["priceinlocalcurrency"]

cat_cols = ["model", "fueltype", "geartype", "vehicletype", "color", "line", "doors", "seats", "climate"]
num_cols = ["kilometers", "ageinmonths"]

if len(x_cols) != len(cat_cols) + len(num_cols):
    raise ValueError("x_cols must be the sum of cat_cols and num_cols")

backend = API(cat_cols=cat_cols, num_cols=num_cols)
app = backend.app
