from fastapi import APIRouter, Depends
from app.application.commands import SaveTimeSeriesData
from app.application.queries import GetTimeSeriesData
from app.infrastructure.unit_of_work import UnitOfWork
from pydantic import BaseModel
from datetime import datetime
from typing import List

router = APIRouter()

class TimeSeriesInput(BaseModel):
    timestamp: datetime
    value: float

class BulkTimeSeriesInput(BaseModel):
    data: List[TimeSeriesInput]

@router.post("/upload-data")
def upload_data(payload: BulkTimeSeriesInput):
    use_case = SaveTimeSeriesData(UnitOfWork())
    for item in payload.data:
        use_case.execute(item.timestamp, item.value)
    return {"message": "Data uploaded successfully"}

@router.get("/get-data")
def get_data():
    use_case = GetTimeSeriesData(UnitOfWork())
    data = use_case.execute()
    return [{"timestamp": entry.timestamp, "value": entry.value} for entry in data]
