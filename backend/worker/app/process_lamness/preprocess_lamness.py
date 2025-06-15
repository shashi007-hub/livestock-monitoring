import joblib
import pandas as pd
import numpy as np
import math
import os

import json
import pandas as pd
import joblib
import os

hello = {
  "acclerometer_data": [
    {
      "Acceleration_x": 0.00759,
      "Acceleration_y": -0.004041,
      "Acceleration_z": -0.002855,
      "Gravity_x": -0.432791,
      "Gravity_y": -0.899855,
      "Gravity_z": -0.054339,
      "Rotation_x": -0.003788,
      "Rotation_y": -0.010593,
      "Rotation_z": 0.026352,
      "Roll": -1.445896,
      "Pitch": 1.119437,
      "Yaw": -2.957264
    },
    {
      "Acceleration_x": 0.004801,
      "Acceleration_y": -0.006165,
      "Acceleration_z": -0.002139,
      "Gravity_x": -0.433008,
      "Gravity_y": -0.899747,
      "Gravity_z": -0.054397,
      "Rotation_x": -0.004694,
      "Rotation_y": -0.014048,
      "Rotation_z": 0.027032,
      "Roll": -1.445825,
      "Pitch": 1.11919,
      "Yaw": -2.957447
    },
    {
      "Acceleration_x": 0.00415,
      "Acceleration_y": -0.00348,
      "Acceleration_z": -0.001406,
      "Gravity_x": -0.433227,
      "Gravity_y": -0.899641,
      "Gravity_z": -0.054412,
      "Rotation_x": -0.002938,
      "Rotation_y": -0.017322,
      "Rotation_z": 0.025516,
      "Roll": -1.445854,
      "Pitch": 1.118947,
      "Yaw": -2.957552
    },
    {
      "Acceleration_x": 0.000831,
      "Acceleration_y": -0.005299,
      "Acceleration_z": -0.001175,
      "Gravity_x": -0.433448,
      "Gravity_y": -0.899536,
      "Gravity_z": -0.054393,
      "Rotation_x": -0.004446,
      "Rotation_y": -0.017732,
      "Rotation_z": 0.027896,
      "Roll": -1.445959,
      "Pitch": 1.118705,
      "Yaw": -2.957609
    }

  ]
}

def ExtractFeaturesFromJSON(json_input):
    print("ExtractFeaturesFromJSON called")
    try:
        # Convert JSON string to Python dict if needed
        # json_input =   hello 
        # if isinstance(json_input, str):
        #     json_input = json_input.replace("'", '"')
        #     print(json_input)
        #     data_dict = json.loads(json_input)
        # elif isinstance(json_input, dict):
        #     data_dict = json_input
        # else:
        #     print("Invalid input format. Must be JSON string or dictionary.")
        #     return None

        # Check if the key 'acclerometer_data' exists
        if 'acclerometer_data' not in json_input:
            print("Key 'acclerometer_data' not found in input JSON.")
            return None

        # Extract accelerometer data from the JSON
        accelerometer_data = json_input['acclerometer_data']
        print("Accelerometer data extracted successfully.")
        # Convert   accelerometer data to a DataFrame
        df = pd.DataFrame(accelerometer_data)
        df = df.dropna()
        print("columns in df", df.columns)
        features = ['Acceleration_x', 'Acceleration_y', 'Acceleration_z',
                    'Gravity_x', 'Gravity_y', 'Gravity_z',
                    'Rotation_x', 'Rotation_y', 'Rotation_z',
                    'Roll', 'Pitch', 'Yaw']

        # Check if all required features are in the data
        if not all(feature in df.columns for feature in features):
            print("Missing required features in input data.")
            return None

        # Load the scaler
        print("Loading scaler...")
        scaler_filename = "../app/models/Scalar_lamness.pkl"
        if not os.path.exists(scaler_filename):
            print(f"Scaler file '{scaler_filename}' does not exist.")
            return None

        scaler = joblib.load(scaler_filename)
        print("Scaler loaded successfully.")

        # Scale the data
        scaled_data = scaler.transform(df[features])
        df_scaled = pd.DataFrame(scaled_data, columns=features, index=df.index)
        print("Data scaled successfully.")
        # Add cumulative sum features
        for feature in features:
            df_scaled[f'Cumsum_{feature}'] = df_scaled[feature].cumsum()
        print("Cumulative sum features added successfully.")
        # Add rolling features
        window_size = 5
        for feature in features:
            df_scaled[f'Rolling_Mean_{feature}'] = df_scaled[feature].rolling(window=window_size).mean()
            df_scaled[f'Rolling_Std_{feature}'] = df_scaled[feature].rolling(window=window_size).std()
        print("Rolling features added successfully.")
        # Drop rows with any NaN values resulting from rolling operations
        return df_scaled.dropna()

    except Exception as e:
        print(f"Error in ExtractFeaturesFromJSON: {e}")
        return None


def predict_lameness(data):
    print("predict_lameness called")
    try:
        print("transforming data")
        FEdata = ExtractFeaturesFromJSON(data)
        if FEdata is None:
            print("Feature extraction failed.")
            return None
        
        print("after FEdata", FEdata.head())
        predictions = []

        model_path = '../app/models/trained_modelnew.pkl'
        if not os.path.exists(model_path):
            print(f"Model file '{model_path}' does not exist.")
            return None

        loaded_model = joblib.load(model_path)
        print("Model loaded successfully.")

        try:
            for i in range(len(FEdata)):
                pred = loaded_model.predict(FEdata.iloc[[i]])
                predictions.append(pred[0])
        except Exception as e:
            print(f"Error during model prediction: {e}")
            return None

        mean_prediction = np.mean(predictions)
        print(f"Mean prediction: {mean_prediction}")
        prediction = math.ceil(mean_prediction)
        print(f"Final prediction (rounded): {prediction}")
        
        return prediction
    except Exception as e:
        print(f"Error in predict_lameness: {e}")
        return None