# -*- coding: utf-8 -*-

from typing import Any
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


ENVIRONMENT: Any = os.getenv("ENVIRONMENT", "")

ENCRYPTATION_KEY: Any = os.getenv("ENCRYPTATION_KEY", "")

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
