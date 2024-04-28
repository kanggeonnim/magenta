from fastapi import APIRouter
from starlette.responses import JSONResponse

from magenta.models.improv_rnn import improv_rnn_generate
from models import ChordsResponseSch, ChordsRequestSch

router = APIRouter()


@router.post("/music/generate", response_model=ChordsResponseSch)
async def translate_by_gpt_router(req: ChordsRequestSch):
    print(req)
    print(len(req.content))

    # await improv_rnn_generate
    improv_rnn_generate.main("")
    # if not pre_prompt:
    #     return JSONResponse(content={"error": f"Invalid category: {category}"}, status_code=400)

    return JSONResponse(content=req.content, status_code=200)



async def translate_by_openai(req: ChordsResponseSch, pre_prompt: str):
    # OpenAI API 키 인증
    # 모델 - GPT 3.5 Turbo 선택
    model = "gpt-3.5-turbo-0125"

    # 메시지 설정
    messages = [{
        "role": "user",
        "content": pre_prompt + req.content,
    }]

    # ChatGPT API 호출
    return ""