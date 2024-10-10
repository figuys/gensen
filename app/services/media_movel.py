# -*- coding: utf-8 -*-

from apis import Coingecko


class MediaMovel(Coingecko):

    def __init__(self) -> None:
        super().__init__()

    def media_move_5d(self):
        return

    def media_movel_25d(self):
        return


if __name__ == "__main__":
    media_movel = MediaMovel()

    crypto_history = media_movel.get_crypto_history(
        crypto="bitcoin"
    )
    
    print(crypto_history)

