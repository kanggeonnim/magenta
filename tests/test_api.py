from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_music_generate_success():
    response = client.get("/music/magenta", params={"chords": "C G Am G"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "foo",
        "title": "Foo",
        "description": "There goes my hero",
    }


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


def test_create_item():
    response = client.post(
        "/items/",
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "error": "Empty Chord"
    }
