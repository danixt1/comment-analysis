from pydantic import BaseModel
from enum import Enum

class BEHAVIOR(Enum):
    positive = "positive"
    negative = "negative"
    neutral  = "neutral"
    question = "question"
class CommentData(BaseModel):
    spam:bool
    behavior:BEHAVIOR
    problems:list[str]
class CommentsAnalyzeResults(BaseModel):
    results:list[CommentData]