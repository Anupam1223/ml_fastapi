from app.infrastructure.repositories import TimeSeriesRepository
from app.infrastructure.unit_of_work import UnitOfWork


class GetTimeSeriesData:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self):
        with self.uow as session:
            repo = TimeSeriesRepository(session)
            return repo.get_all()
