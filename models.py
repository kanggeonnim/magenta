# demo=fast-apis > schemas > gpt_sch.py 파일 생성
from typing import List

from pydantic import BaseModel


# 요청시
class ChordsRequestSch(BaseModel):
    # chords: List[str]
    chords: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "chords": "C G Am C"
            }
        }


# 결과를 응답하는 경우
class ChordsResponseSch(BaseModel):
    class Config:
        orm_mode = True
        schema_extra = {
            "music_url_list": [
                "https://music-url.com"
            ]
        }
