# -*- coding: utf-8 -*-

from typing import Any
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


ENVIRONMENT: str = os.getenv("ENVIRONMENT", "")

ENCRYPTATION_KEY: str = os.getenv("ENCRYPTATION_KEY", "")

FIREBASE_URL: str = os.getenv("FIREBASE_URL", "")

FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")

COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
