import os
import pathlib
from tempfile import NamedTemporaryFile

import boto3
import moto
import pytest
from config.config import settings
from s3.upload_s3 import upload_s3, upload_file_to_s3


@pytest.fixture(scope='session')
def aws_credentials():
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

    try:
        # 임시로 사용할 AWS 자격 증명 파일을 생성합니다.
        tmp = NamedTemporaryFile(delete=False)
        # 모의 AWS 자격 증명을 작성하여 임시 파일에 씁니다.
        tmp.write(b"""[aws_prof_dev_qa]
aws_access_key_id = testing
aws_secret_access_key = testing""")
        tmp.close()
        # 모의 자격 증명 파일의 경로를 환경 변수로 설정합니다.
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = str(tmp.name)
        yield
    finally:
        # 테스트가 완료된 후에 임시 파일을 삭제합니다.
        os.unlink(tmp.name)


# Fixture to create an empty S3 bucket for testing.
# 테스트용 빈 S3 버킷을 생성하는 픽스처입니다.
@pytest.fixture(scope='function')
def empty_bucket(aws_credentials):
    moto_fake = moto.mock_s3()
    try:
        # Moto를 시작합니다.
        moto_fake.start()
        # 가짜 S3 리소스를 생성합니다.
        conn = boto3.resource('s3')
        # 테스트에 사용할 가짜 S3 버킷을 생성합니다.
        conn.create_bucket(Bucket="TEST_BUCKET")  # or the name of the bucket you use
        yield conn
    finally:
        # 테스트가 완료된 후에 Moto를 중지합니다.
        moto_fake.stop()


def test_create_and_get(empty_bucket):
    with NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write('test file')
        file_path = tmp.name
        assert upload_file_to_s3(file_path, "TEST_BUCKET", tmp.name) is True
