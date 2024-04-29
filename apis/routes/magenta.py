from fastapi import APIRouter
from starlette.responses import JSONResponse
from magenta.models.improv_rnn import improv_rnn_generate
from models import ChordsResponseSch, ChordsRequestSch

router = APIRouter()


@router.post("/music/magenta", response_model=ChordsResponseSch)
async def generate_music_by_chords(req: ChordsRequestSch):
    print(req.chords)
    print(len(req.chords))

    # await improv_rnn_generate
    upload_key_list = improv_rnn_generate.main(req.chords)

    if not upload_key_list:
        return JSONResponse(content={"error": f"Invalid chords: {req}"}, status_code=400)

    return JSONResponse(content={"musicUrls": upload_key_list}, status_code=200)
