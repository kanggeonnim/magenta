import os, json
from pathlib import Path


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_SECRET_DIR = os.path.join(BASE_DIR, "env")
    CONFIG_SECRET_COMMON_FILE = os.path.join(CONFIG_SECRET_DIR, "setting_local.json")

    config_secret_common = json.loads(open(CONFIG_SECRET_COMMON_FILE, encoding='utf-8').read())

    OPENAI_API_KEY: str = config_secret_common["OPENAI_API_KEY"]
    GPT_PROMPT_BILL: str = config_secret_common["GPT_PROMPT_BILL"]
    GPT_PROMPT_ISSUE: str = config_secret_common["GPT_PROMPT_ISSUE"]
    GPT_PROMPT_NEWS: str = config_secret_common["GPT_PROMPT_NEWS"]


settings = Settings()
