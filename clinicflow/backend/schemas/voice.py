from pydantic import BaseModel

class VoiceUploadResponse(BaseModel):
    visit_id: int
    transcript: str
