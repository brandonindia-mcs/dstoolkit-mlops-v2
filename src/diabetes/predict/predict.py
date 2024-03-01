"""
This module is designed for making predictions using a machine learning model.

It includes functionality to load test data, load a pre-trained model, make predictions on the test data,
and save these predictions. The module can be run as a script, allowing users to specify the model file,
test data, and prediction output path via command-line arguments.
"""

import argparse
import pandas as pd
import os
from pathlib import Path
import pickle


def main(model_input, test_data, prediction_path):
    """Load test data, call predict function.

    Args:
        model_input (string): path to model pickle file
        test_data (string): path to test data
        prediction_path (string): path to which to write prediction
    """
    lines = [
        f"Model path: {model_input}",
        f"Test data path: {test_data}",
        f"Predictions path: {prediction_path}",
    ]

    for line in lines:
        print(line)

    test_x, testy = load_test_data(test_data)
    predict(test_x, testy, model_input, prediction_path)


def load_test_data(test_data):
    """
    Load test data and store it in two data frames.

    Parameters:
      test_data (pandas.DataFrame): input data

    Returns:
      (DataFrame, DataFrame): input data with no expected results and expected results in te second frame
    """
    print("mounted_path files: ")
    arr = os.listdir(test_data)

    print(arr)
    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        input_df = pd.read_csv((Path(test_data) / filename))
        df_list.append(input_df)

    test_data = df_list[0]
    testy = test_data["outcome"]
    test_x = test_data[
        [
            "pregnancies",
            "glucose",
            "bloodpressure",
            "skinthickness",
            "insulin",
            "bmi",
            "diabetespedigreefunction",
            "age",
        ]
    ]
    print(test_x.shape)
    print(test_x.columns)
    return test_x, testy


def predict(test_x, testy, model_input, prediction_path):
    """
    Predict results on a batch and save them into csv file altogether wit expected results.

    Parameters:
      test_x (pandas.DataFrame): input data to predict
      testy (pandas.DataFrame): expected results
      model_input (str): an input folder with the model
      prediction_path (str): a resulting folder
    """
    # Load the model from input port
    model = pickle.load(open((Path(model_input) / "model.sav"), "rb"))

    # Make predictions on test_x data and record them in a column named predicted_cost
    predictions = model.predict(test_x)
    test_x["predicted_cost"] = predictions
    print(test_x.shape)

    # Compare predictions to actuals (testy)
    output_data = pd.DataFrame(test_x)
    output_data["actual_cost"] = testy

    # Save the output data with feature columns, predicted cost, and actual cost in csv file
    output_data = output_data.to_csv((Path(prediction_path) / "predictions.csv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("predict")
    parser.add_argument("--model_input", type=str, help="Path of input model")
    parser.add_argument("--test_data", type=str, help="Path to test data")
    parser.add_argument("--predictions", type=str, help="Path of predictions")

    args = parser.parse_args()

    print("hello scoring world...")

    model_input = args.model_input
    test_data = args.test_data
    prediction_path = args.predictions
    main(model_input, test_data, prediction_path)
