import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

def train_model():
    df = pd.read_csv("../data/solar_tracking_dataset.csv")
    print(df.shape)

    print(df["panel_zenith_deg"].describe())

    x = df[["sun_x", "sun_y", "sun_z"]]
    y = df["panel_zenith_deg"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)

    print(predictions[:10])
    print(y_test[:10].values)

    score = r2_score(y_test, predictions)
    print("Model R2 score:", score)

    print(x_train.shape)
    print(x_test.shape)

    print(x.head())
    print(y.head())

    plt.scatter(y_test, predictions)
    plt.xlabel("Real Angle")
    plt.ylabel("Predicted Angle")
    plt.title("Prediction vs Real")
    plt.show()

train_model()