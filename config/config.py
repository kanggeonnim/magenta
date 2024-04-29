import os, json
from pathlib import Path


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_SECRET_DIR = os.path.join(BASE_DIR, "env")
    CONFIG_SECRET_COMMON_FILE = os.path.join(CONFIG_SECRET_DIR, "setting_local.json")

    config_secret_common = json.loads(open(CONFIG_SECRET_COMMON_FILE, encoding='utf-8').read())

    MIDI_FILE_PATH: str = config_secret_common["MIDI_FILE_PATH"]
    MP3_FILE_PATH: str = config_secret_common["MP3_FILE_PATH"]
    BUNDLE_FILE_PATH: str = config_secret_common["BUNDLE_FILE_PATH"]
    AWS_ACCESS_KEY_ID: str = config_secret_common["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY: str = config_secret_common["AWS_SECRET_ACCESS_KEY"]
    AWS_DEFAULT_REGION: str = config_secret_common["AWS_DEFAULT_REGION"]
    AWS_BUCKET_NAME: str = config_secret_common["AWS_BUCKET_NAME"]
    AWS_CLOUD_FRONT: str = config_secret_common["AWS_CLOUD_FRONT"]


settings = Settings()
