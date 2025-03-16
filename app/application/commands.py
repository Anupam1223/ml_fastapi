from app.domain.entities import TimeSeriesData
from app.infrastructure.repositories import TimeSeriesRepository
from app.infrastructure.unit_of_work import UnitOfWork

class SaveTimeSeriesData:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, timestamp, value):
        data = TimeSeriesData(timestamp=timestamp, value=value)
        with self.uow as session:
            repo = TimeSeriesRepository(session)
            repo.add(data)
