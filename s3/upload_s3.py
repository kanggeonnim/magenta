import os
import subprocess
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError  # boto3에서 발생하는 예외를 처리하기 위해 추가
from pydub import AudioSegment

from config.config import settings

AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION = settings.AWS_DEFAULT_REGION
AWS_S3_BUCKET = settings.AWS_BUCKET_NAME
MIDI_FILE_PATH = settings.MIDI_FILE_PATH
MP3_FILE_PATH = settings.MP3_FILE_PATH
AWS_CLOUD_FRONT = settings.AWS_CLOUD_FRONT


def s3_connection():
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_DEFAULT_REGION)
        print("S3 bucket connected!")
        return s3
    except Exception as e:
        print(f"Error connecting to S3 bucket: {e}")
        return None


def generate_unique_id():
    return str(uuid.uuid4())  # UUID를 문자열로 변환하여 반환


def upload_file_to_s3(file_name, bucket, key):
    try:
        s3 = s3_connection()
        if s3:
            s3.upload_file(file_name, bucket, key)  # 파일 저장
            print("File uploaded to S3 successfully!")
            return True
        else:
            return False
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return False


def upload_s3(midi_file_list):
    s3_upload_key_list = []
    for path in midi_file_list:
        try:
            # S3에 파일 업로드
            unique_id = generate_unique_id()
            bucket = AWS_S3_BUCKET
            input_midi_path = MIDI_FILE_PATH + "/" + path
            output_mp3_path = MP3_FILE_PATH + "/" + unique_id + ".mp3"

            midi_to_mp3(input_midi_path, output_mp3_path)

            # 노래 S3 업로드
            s3_upload_key = "music/" + unique_id + ".mp3"
            music_upload_successful = upload_file_to_s3(output_mp3_path, bucket, s3_upload_key)

            # 업로드한 mp3 삭제
            if music_upload_successful:
                os.remove(output_mp3_path)
                
            s3_upload_key_list.append(f'https://{AWS_S3_BUCKET}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{s3_upload_key}')

        except Exception as e:
            print(f"An error occurred: {e}")

    return s3_upload_key_list


def midi_to_mp3(input_midi, output_mp3):
    # MIDI to mp3
    sound = AudioSegment.from_file(input_midi)
    sound.export(output_mp3, format="mp3")

    # delete MIDI file
    os.remove(input_midi)


if __name__ == "__main__":
    s3 = boto3.client('s3')
    s3.download_file(AWS_S3_BUCKET, "music/aeb866db-e883-4903-8a30-c877e589c068.mp3", "download.mp3")
