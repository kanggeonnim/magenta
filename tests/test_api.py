from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app

client = TestClient(app)


@patch("magenta.models.improv_rnn.improv_rnn_generate.main")
def test_music_generate_success(mock_main):
    mock_main.return_value = ["https.test-return-url.mp3"]
    response = client.get("/music/magenta", params={"chords": "C,G,Am,G"}, )
    assert response.status_code == 200
    assert "musicUrls" in response.json()

    # 정규식 패턴을 사용하여 URL 추출
    music_urls = response.json()["musicUrls"]
    # 응답에 포함된 URL이 패턴과 일치하는지 확인
    for url in music_urls:
        assert url == "https.test-return-url.mp3"


def test_music_generate_fail_zero_chord():
    response = client.post("/music/magenta", json={"chords": ""}, )
    assert response.status_code == 400
    assert response.json() == {
        "error": "At least two Chords are required"
    }


def test_music_generate_fail_one_chord():
    response = client.post("/music/magenta", json={"chords": "C"}, )
    assert response.status_code == 400
    assert response.json() == {
        "error": "At least two Chords are required"
    }
