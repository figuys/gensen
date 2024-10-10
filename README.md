<h1 align="center">Gensen</h1>

<p align="center">
  <img src="https://github.com/user-attachments/assets/34527e08-605d-448a-b512-9bc21cd9aa06"
       alt="Gensen Logs" width="550" height="280">
</p>

### Overview
Gensen is an algorithm designed to perform **"long-term conservative automated trading"** on multiple cryptocurrencies through the API of a brazilian exchange. Given that the project is in its initial stages and the traded values are not very high, it takes advantage of the regulatory exemptions provided by national (brazilian) exchanges. The algorithm is very conservative, prioritizing security while ensuring profits.

### How the Algorithm Works
Core Features:<br />
Price Prediction using Linear Regression: The algorithm uses historical price data to predict future prices of cryptocurrencies. It applies a sliding window approach, where it takes the prices from the previous days and trains a Linear Regression model to forecast the price for the next day.

The PriceIndicator class performs the price prediction tasks, including data preprocessing, feature creation, model training, and evaluation using metrics such as MAE (Mean Absolute Error), RMSE (Root Mean Squared Error), and R². This ensures that the model has a reliable performance before making trading decisions.

Market Conditions Evaluation: The MarketConditionsEvaluator class monitors market conditions for various cryptocurrencies. It evaluates user portfolios stored in Firebase and checks for opportunities to sell when the profit threshold is met. The algorithm only executes a sell order if the profit is positive, meaning it avoids selling assets at a loss.

This conservative approach ensures that the algorithm doesn't lose money, as it only sells cryptocurrencies when their value is higher than the original purchase price.

Detailed Flow:
Data Collection: The algorithm collects historical data for each cryptocurrency using the Coingecko API. This data includes daily prices for the past year, allowing the model to generate reliable predictions.

Price Prediction: The PriceIndicator uses this data to predict future prices based on the last few days (adjustable via the window_size parameter). The model is trained on historical data, and the prediction for the next day is compared to the recent average price.

Profit Evaluation: For each user's cryptocurrency portfolio, the algorithm calculates the difference between the current value of the asset and the original purchase price (stored in Firebase). If the profit exceeds a predefined threshold (e.g., 10%), the algorithm places a sell order. This prevents selling during market dips, ensuring that only profitable trades are executed.

Buy Conditions: In cases where certain beta-featured cryptocurrencies (such as Bitcoin, Ethereum, and Solana) are in a downtrend and are predicted to continue dropping, the algorithm evaluates buying opportunities at lower prices, maximizing long-term profitability.

Why the Algorithm Doesn't Lose Money
The algorithm follows a conservative approach by only selling assets when they are in profit. This strategy ensures that:

No sell orders are placed if the cryptocurrency value is lower than the original purchase price, preventing any financial loss.
The algorithm continuously monitors the market and only acts when there is a strong indication that the asset has reached a profit target.
Even when market conditions are unfavorable, the algorithm holds onto the assets instead of selling at a loss, ensuring that the user doesn't lose money.

## Prerequisites

Before starting, make sure Docker is installed on your machine. If Docker is not installed, follow the instructions [here](https://docs.docker.com/get-docker/).

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/denzylegacy/gensen.git
   cd gensen
   ```

2. Build the Docker image:
   ```bash
   sudo docker build -t dc-gensen .
   ```

## Running the Project

After building the image, run the project using the following command:

```bash
sudo docker run -it dc-gensen
```

This command will start the container and run the main script `gensen.py` of the project.

## Dockerfile

The `Dockerfile` used in this project is as follows:

```Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app/gensen.py"]
```

This Dockerfile defines an environment based on the `python:3.10-slim` image, installs the dependencies listed in `requirements.txt`, and copies the project contents into the container. The default command to run is `python app/gensen.py`.

## Contributions

Feel free to open issues or pull requests. Feedback is always welcome!
