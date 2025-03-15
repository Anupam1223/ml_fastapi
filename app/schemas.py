from pydantic import BaseModel
from typing import List


class InputData(BaseModel):
    features: List[float]
