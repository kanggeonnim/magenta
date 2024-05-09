from fastapi import APIRouter, Query
from starlette.responses import JSONResponse
from magenta.models.improv_rnn import improv_rnn_generate
from models import ChordsResponseSch, ChordsRequestSch

router = APIRouter()


@router.get("/music/magenta", response_model=ChordsResponseSch)
async def generate_music_by_chords(chords: str = Query(..., description="Comma-separated list of chords")):
    if len(chords.split(",")) < 2:
        return JSONResponse(content={"error": f"At least two Chords are required"}, status_code=400)

    chords = chords.replace(",", " ")

    upload_key_list = improv_rnn_generate.main(chords)

    # musicUrls 리스트에서 요소를 2개씩 묶기
    grouped_data = group_list_elements(upload_key_list, 2)

    return JSONResponse(content={"musicUrls": grouped_data}, status_code=200)


def group_list_elements(input_list, chunk_size):
    """
    리스트의 요소를 주어진 크기로 묶어 새로운 리스트를 생성합니다.

    :param input_list: 묶을 리스트
    :param chunk_size: 묶을 크기
    :return: 새로 생성된 리스트
    """
    return [{"midiUrl": input_list[i], "mp3Url": input_list[i + 1]} for i in range(0, len(input_list), chunk_size)]
