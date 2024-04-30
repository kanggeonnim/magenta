from fastapi import APIRouter
from starlette.responses import JSONResponse
from magenta.models.improv_rnn import improv_rnn_generate
from models import ChordsResponseSch, ChordsRequestSch

router = APIRouter()


@router.post("/music/magenta", response_model=ChordsResponseSch)
async def generate_music_by_chords(req: ChordsRequestSch):
    if len(req.chords.split()) < 2:
        return JSONResponse(content={"error": f"At least two Chords are required"}, status_code=400)

    upload_key_list = improv_rnn_generate.main(req.chords)

    return JSONResponse(content={"musicUrls": upload_key_list}, status_code=200)
