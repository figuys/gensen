# -*- coding: utf-8 -*-

import datetime
import pytz
import asyncio
from pathlib import Path

from infra import log, ENVIRONMENT, COINGECKO_API_KEY
from apis import Firebase, Foxbit, Coingecko
from predictions import PriceIndicator
from utils import Encryptor


class MarketConditionsEvaluator:
    def __init__(self):
        self.current_dir = Path(__file__).resolve().parent
        self.beta_feature_cryptos: list = ["bitcoin", "ethereum", "solana"]

    async def evaluate_market_conditions(self):
        log.info(f"[background_tasks] market_conditions_evaluator: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        firebase = Firebase()

        connection = firebase.firebase_connection("root")

        users = connection.child("users").get()

        if not users:
            return

        for user in users.keys():
            user_credentials = connection.child(
                f"users/{user}/exchanges/foxbit/credentials"
            ).get()

            if not user_credentials:
                continue

            for exchange in users[user]["exchanges"].keys():
                if not "cryptocurrencies" in users[user]["exchanges"][exchange].keys():
                    continue

                for cryptocurrency in users[user]["exchanges"][exchange]["cryptocurrencies"].keys():
                    asset = users[user]["exchanges"][exchange]["cryptocurrencies"][cryptocurrency]

                    foxbit = Foxbit(
                        api_key=Encryptor().decrypt_api_key(user_credentials["FOXBIT_ACCESS_KEY"]),
                        api_secret=Encryptor().decrypt_api_key(user_credentials["FOXBIT_SECRET_KEY"])
                    )

                    accounts = foxbit.request("GET", "/rest/v3/accounts", None, None)

                    for account in accounts["data"]:
                        if account["currency_symbol"] == cryptocurrency:
                            params = {
                                "side": "buy",
                                "base_currency": cryptocurrency,
                                "quote_currency": "brl",
                                "amount": "1"
                            }

                            quote_sell = foxbit.request(
                                "GET", "/rest/v3/markets/quotes", params=params, body=None
                            )

                            asset_available_value_brl = foxbit.convert_asset_to_brl(
                                brl_asset=float(account["balance_available"]),
                                available_balance_brl=float(quote_sell["price"])
                            )

                            difference_check: float = round(
                                float(asset_available_value_brl) -
                                float(asset["base_balance"]), 4
                            )
                            
                            percentage_of_profit: float = (
                                (difference_check * 100) / float(asset["base_balance"])
                            )

                            log.info(f"Percentage of profit: {percentage_of_profit:.1f}%")

                            log.info(f"{difference_check}: {cryptocurrency} -> {user}")

                            if (
                                percentage_of_profit >= 10.0 and
                                float(asset_available_value_brl) >=
                                float(asset["base_balance"]) + (float(asset["fixed_profit_brl"]) + 0.3)
                            ):
                                timestamp = datetime.datetime.now(
                                    pytz.timezone("America/Sao_Paulo")
                                ).strftime("%Y-%m-%d %H:%M:%S")

                                if ENVIRONMENT == "SERVER":
                                    order = {
                                        "market_symbol": f"{cryptocurrency}brl",
                                        "side": "SELL",
                                        "type": "INSTANT",
                                        "amount": str(float(asset_available_value_brl - 5.3))
                                    }

                                    order_response = foxbit.request("POST", "/rest/v3/orders", None, body=order)

                                    log.info(f"[{timestamp}] SELL ORDER: {order}")
                                    log.info(f"[{timestamp}] ORDER RESPONSE: {order_response}")

                                    await asyncio.sleep(1)

                                log.info(f"[INSTANT ORDER NOTIFICATION] {cryptocurrency} -> {user}")

                                firebase = Firebase()

                                name_timestamp = str(
                                    datetime.datetime.now(
                                        pytz.timezone("America/Sao_Paulo")
                                ).strftime("%Y%m%d%H%M%S")
                                )

                                connection.child(f"users/{user}/messages/gensen/{name_timestamp}").set(
                                    {
                                        "title": f'Short-term profit of {cryptocurrency.upper()} (+**{difference_check:.2f}**)!',
                                        "description": f"At this very moment I made a **sale** of R$**{float(asset_available_value_brl - 5.3):.2f}** worth of {asset['name']}!!"
                                    }
                                )
                            elif float(asset_available_value_brl) < 10.0 and cryptocurrency in self.beta_feature_cryptos:
                                coingecko: object = Coingecko(
                                    coingecko_api_key=COINGECKO_API_KEY
                                )

                                crypto_history_df = coingecko.get_crypto_history(
                                    crypto=cryptocurrency, days=365
                                )

                                predictor = PriceIndicator(crypto_history_df)

                                percent_difference, status, double_percent_difference, double_status, prediction_difference, prediction_status = (
                                    predictor.run()
                                )

                                if status == "below" and double_status == "below" and prediction_status == "below":
                                    if percent_difference <= -5.0 and double_percent_difference <= -5.0 and prediction_difference <= -5.0:
                                        order = {
                                            "market_symbol": f"{cryptocurrency}brl",
                                            "side": "BUY",
                                            "type": "INSTANT",
                                            "amount": str(asset["base_balance"])
                                        }

                                        order_response = foxbit.request("POST", "/rest/v3/orders", None, body=order)

                                        log.info(f"[{timestamp}] BUY ORDER: {order}")
                                        log.info(f"[{timestamp}] ORDER RESPONSE: {order_response}")

                                        await asyncio.sleep(1)


async def main():
    evaluator = MarketConditionsEvaluator()
    while True:
        try:
            await evaluator.evaluate_market_conditions()
            await asyncio.sleep(30)
        except Exception as error:
            log.error(f"[UNEXPECTED ERROR] {error}")
            await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())
