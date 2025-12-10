from pydantic import BaseModel

class VisitSummary(BaseModel):
    id: int
    title: str
    date: str
    summary: str

class VisitDetail(VisitSummary):
    subjective: str
    objective: str
    assessment: str
    plan: str

class VisitCreate(BaseModel):
    transcript: str
