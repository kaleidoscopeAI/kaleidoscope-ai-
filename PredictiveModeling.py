import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from typing import Dict, List

class PredictiveModeling:
    """
    Predicts future states and trends using historical data and machine learning techniques.
    """

    def __init__(self, prediction_type: str = "linear"):
        """
        Initialize the predictive model.
        :param prediction_type: Type of model to use ('linear' or 'random_forest').
        """
        self.prediction_type = prediction_type
        self.model = self._initialize_model()

    def _initialize_model(self):
        """
        Initializes the prediction model based on the specified type.
        :return: A scikit-learn model pipeline.
        """
        if self.prediction_type == "linear":
            return Pipeline([
                ("scaler", StandardScaler()),
                ("regressor", LinearRegression())
            ])
        elif self.prediction_type == "random_forest":
            return Pipeline([
                ("scaler", StandardScaler()),
                ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
            ])
        else:
            raise ValueError("Unsupported prediction type. Use 'linear' or 'random_forest'.")

    def train(self, historical_data: np.ndarray, targets: np.ndarray):
        """
        Trains the predictive model using historical data and target values.
        :param historical_data: 2D array of historical data (features).
        :param targets: 1D array of target values.
        """
        self.model.fit(historical_data, targets)
        print(f"Predictive model ({self.prediction_type}) trained successfully.")

    def predict(self, future_data: np.ndarray) -> np.ndarray:
        """
        Predicts future states based on the trained model.
        :param future_data: 2D array of input data for prediction.
        :return: 1D array of predicted values.
        """
        predictions = self.model.predict(future_data)
        return predictions

    def validate_model(self, validation_data: np.ndarray, validation_targets: np.ndarray) -> Dict:
        """
        Validates the predictive model on a validation dataset.
        :param validation_data: 2D array of validation data (features).
        :param validation_targets: 1D array of validation target values.
        :return: Dictionary with model evaluation metrics (e.g., MAE, R2 score).
        """
        from sklearn.metrics import mean_absolute_error, r2_score

        predictions = self.model.predict(validation_data)
        mae = mean_absolute_error(validation_targets, predictions)
        r2 = r2_score(validation_targets, predictions)

        return {"MAE": mae, "R2_Score": r2}

    def adaptive_prediction(self, historical_data: np.ndarray, targets: np.ndarray, future_data: np.ndarray) -> np.ndarray:
        """
        Performs adaptive prediction by re-training the model with the latest data.
        :param historical_data: 2D array of historical data (features).
        :param targets: 1D array of target values.
        :param future_data: 2D array of input data for prediction.
        :return: 1D array of predicted values.
        """
        self.train(historical_data, targets)
        predictions = self.predict(future_data)
        return predictions

# Example usage
if __name__ == "__main__":
    # Example: Predict future trends using historical data
    historical_data = np.array([
        [1, 2],
        [2, 3],
        [3, 4],
        [4, 5],
        [5, 6]
    ])
    targets = np.array([3, 5, 7, 9, 11])

    future_data = np.array([
        [6, 7],
        [7, 8]
    ])

    # Initialize the PredictiveModeling module
    predictor = PredictiveModeling(prediction_type="linear")

    # Train the model
    predictor.train(historical_data, targets)

    # Predict future outcomes
    predictions = predictor.predict(future_data)
    print("Predictions:", predictions)

    # Validate the model
    validation_data = np.array([
        [3, 4],
        [4, 5]
    ])
    validation_targets = np.array([7, 9])
    validation_results = predictor.validate_model(validation_data, validation_targets)
    print("Validation Results:", validation_results)
