from app.domain.entities import TimeSeriesData
from app.infrastructure.db import Base
from sqlalchemy import Column, Integer, Float, DateTime
import datetime

class TimeSeriesModel(Base):
    __tablename__ = "timeseries_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    value = Column(Float, nullable=False)

class TimeSeriesRepository:
    def __init__(self, session):
        self.session = session

    def add(self, data: TimeSeriesData):
        db_entry = TimeSeriesModel(timestamp=data.timestamp, value=data.value)
        self.session.add(db_entry)

    def get_all(self):
        return self.session.query(TimeSeriesModel).order_by(TimeSeriesModel.timestamp).all()
