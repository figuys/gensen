import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .infra import log, COINGECKO_API_KEY
from .apis import Coingecko


class PriceIndicator:
    """
    A class to predict crypto prices using Linear Regression.

    Attributes:
        self.history_data (pd.DataFrame): DataFrame containing the crypto price data.
        window_size (int): Number of days to consider for creating features.
        test_size (int): Number of recent days to exclude from training for testing.
        df (pd.DataFrame): DataFrame containing the crypto data.
        X (np.ndarray): Feature matrix.
        y (np.ndarray): Target vector.
        X_train (np.ndarray): Training feature matrix.
        X_test (np.ndarray): Testing feature matrix.
        y_train (np.ndarray): Training target vector.
        y_test (np.ndarray): Testing target vector.
        model (LinearRegression): The Linear Regression model.
        predictions (np.ndarray): Predictions on the test set.
        resultados (dict): Dictionary containing evaluation metrics.
    """

    def __init__(self, history_data, window_size=14, test_size=14):
        """
        Initializes the PriceIndicator with the given parameters.

        Args:
            history_data (pd.DataFrame): Dataframe containing crypto price data.
            window_size (int, optional): Number of days to consider for creating features. Defaults to 14.
            test_size (int, optional): Number of recent days to exclude from training for testing. Defaults to 14.
        """
        self.history_data = history_data
        self.window_size = window_size
        self.test_size = test_size
        self.df = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = LinearRegression()
        self.predictions = None
        self.resultados = {}

    def load_and_preprocess_data(self):
        """
        Loads the CSV data, converts the 'datetime' column to datetime type,
        sorts the DataFrame by date, and resets the index.
        """
        if type(self.history_data) == str:
            self.df = pd.read_csv(self.history_data)
        else:
            self.df = self.history_data
        
        self.df['datetime'] = pd.to_datetime(self.df['datetime'])
        self.df = self.df.sort_values(by="datetime", ascending=True)
        self.df.reset_index(drop=True, inplace=True)

    def create_features_and_target(self):
        """
        Creates the feature matrix X and target vector y using a sliding window approach.
        Each feature consists of (window_size - 1) days of prices, and the target is the price on the window_size-th day.
        """
        X = []
        y = []

        for i in range(len(self.df) - self.window_size + 1):
            features = self.df['price'].iloc[i:i + (self.window_size - 1)].values
            target = self.df['price'].iloc[i + (self.window_size - 1)]

            X.append(features)
            y.append(target)

        self.X = np.array(X)
        self.y = np.array(y)

        log.info(f"Total samples: {self.X.shape[0]}")
        log.info(f"Shape of X: {self.X.shape}, Shape of y: {self.y.shape}")

    def split_data(self):
        """
        Splits the data into training and testing sets.
        The last 'test_size' samples are reserved for testing.
        """
        self.X_train, self.X_test = self.X[:-self.test_size], self.X[-self.test_size:]
        self.y_train, self.y_test = self.y[:-self.test_size], self.y[-self.test_size:]

    def train_model(self):
        """
        Trains the Linear Regression model using the training data.
        """
        self.model.fit(self.X_train, self.y_train)

    def evaluate_model(self):
        """
        Evaluates the trained model on the test set and calculates MAE, RMSE, and R² metrics.
        """
        self.predictions = self.model.predict(self.X_test)

        mae = mean_absolute_error(self.y_test, self.predictions)
        rmse = np.sqrt(mean_squared_error(self.y_test, self.predictions))
        r2 = r2_score(self.y_test, self.predictions)

        self.resultados = {'MAE': float(mae), 'RMSE': float(rmse), 'R²': r2}
        log.info(f"\n### Evaluation Metrics on Test Set ###")
        log.info(f"MAE: {self.resultados['MAE']:.2f}")
        log.info(f"RMSE: {self.resultados['RMSE']:.2f}")
        log.info(f"R²: {self.resultados['R²']:.6f}")

    def analyze_recent_days(self):
        """
        Analyzes the last (window_size - 1) days to determine if the latest price is above or below the average.
        """
        recent_days = self.df.tail(self.window_size)

        average_recent = recent_days['price'].mean()
        latest_price = self.df['price'].iloc[-1]
        percent_difference = ((latest_price - average_recent) / average_recent) * 100

        status = "above" if latest_price > average_recent else "below"

        log.info(f"\n### Analysis of the Last {self.window_size} Days ###")
        log.info(f"Average price of the last {self.window_size} days: ${average_recent:.2f}")
        log.info(f"Latest price: ${latest_price:.2f}")
        log.info(f"Percentage difference: {percent_difference:.1f}%")
        log.info(f"The status (based on the last {self.window_size} days) is '{status}' the average.")

        ##### Double Recent Days #####

        double_average_recent = recent_days['price'].mean()
        double_latest_price = self.df['price'].iloc[-1]
        double_percent_difference = (
            (double_latest_price - double_average_recent) / double_average_recent
        ) * 100

        double_status = "above" if latest_price > average_recent else "below"

        log.info(f"\n### Analysis of the Last {self.window_size * 2} Days ###")
        log.info(f"Average price of the last {self.window_size * 2} days: ${double_average_recent:.2f}")
        log.info(f"Latest price: ${double_latest_price:.2f}")
        log.info(f"Percentage difference: {double_percent_difference:.1f}%")
        log.info(f"The status (based on the last {self.window_size * 2} days) is '{double_status}' the average.\n")

        return (
            average_recent, 
            percent_difference, status,
            double_percent_difference, double_status
        )

    def predict_next_day(self):
        """
        Predicts the price for the next day using the last (window_size - 1) days as features.
        """
        features_next_day = self.df['price'].iloc[-(self.window_size - 1):].values.reshape(1, -1)
        predicted_price = self.model.predict(features_next_day)[0]

        log.info(f"\n### Prediction for the Next Day ###")
        log.info(f"Predicted price for the next day: ${predicted_price:.2f}")

        return predicted_price

    def compare_prediction_to_average(self, predicted_price, average_recent) -> float:
        """
        Compares the predicted price to the average of the recent days and log.infos the comparison.

        Args:
            predicted_price (float): The predicted price for the next day.
            average_recent (float): The average price of the recent days.
        """
        percent_difference = ((predicted_price - average_recent) / average_recent) * 100
        status = "above" if predicted_price > average_recent else "below"

        log.info(f"\n### Comparison of Predicted Price to Average ###")
        log.info(f"Predicted price is {percent_difference:.1f}% {status} the average of the last {self.window_size - 1} days.")

        return percent_difference, status

    def run(self) -> tuple:
        """
        Executes all steps of the prediction process.
        """
        self.load_and_preprocess_data()
        self.create_features_and_target()
        self.split_data()
        self.train_model()
        self.evaluate_model()
        average_recent, percent_difference, status, double_percent_difference, double_status = self.analyze_recent_days()
        predicted_price = self.predict_next_day()
        prediction_difference, prediction_status = self.compare_prediction_to_average(
            predicted_price, average_recent
        )

        return (
            percent_difference, status, 
            double_percent_difference, double_status,
            prediction_difference, prediction_status
        )


if __name__ == "__main__":
    coingecko: object = Coingecko(
        coingecko_api_key=COINGECKO_API_KEY
    )

    crypto_history_df: pd.DataFrame = coingecko.get_crypto_history(
        crypto="bitcoin", days=365
    )

    predictor = PriceIndicator(crypto_history_df)  # csv_path="./reports/bitcoin.csv"

    percent_difference, status, double_percent_difference, double_status, prediction_difference, prediction_status = (
        predictor.run()
    )

    print(
        f"percent_difference {percent_difference:.2f}, status {status}"
    )
    print(
        f"double_percent_difference {double_percent_difference:.2f}, double_status {double_status}"
    )
    print(
        f"prediction_status {prediction_difference:.1f}%, prediction_status {prediction_status}"
    )
