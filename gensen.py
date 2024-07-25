# -*- coding: utf-8 -*-

import datetime
import pytz
import asyncio
from pathlib import Path

from infra import log, ENVIRONMENT
from apis import Firebase, Foxbit
from utils import Encryptor


class MarketConditionsEvaluator:
    def __init__(self):
        self.current_dir = Path(__file__).resolve().parent

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

                            log.info(f"{difference_check}: {cryptocurrency} -> {user}")

                            if (
                                float(asset_available_value_brl) >=
                                float(asset["base_balance"]) +
                                (float(asset["fixed_profit_brl"]) + 0.3)
                            ):
                                timestamp = datetime.datetime.now(
                                    pytz.timezone("America/Sao_Paulo")
                                ).strftime("%Y-%m-%d %H:%M:%S")

                                if ENVIRONMENT == "SERVER":
                                    order = {
                                        "market_symbol": f"{cryptocurrency}brl",
                                        "side": "SELL",
                                        "type": "INSTANT",
                                        "amount": str(difference_check)
                                    }

                                    order_response = foxbit.request("POST", "/rest/v3/orders", None, body=order)

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
                                        "description": f"At this very moment I made a **sale** of R$**{difference_check:.3f}** worth of {asset['name']}!!"
                                    }
                                )


async def main():
    evaluator = MarketConditionsEvaluator()
    while True:
        await evaluator.evaluate_market_conditions()
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
