from app.infrastructure.db import SessionLocal
from sqlalchemy.exc import SQLAlchemyError


class UnitOfWork:
    def __enter__(self):
        self.session = SessionLocal()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            try:
                self.session.commit()  # Commit changes if no exception
            except SQLAlchemyError:
                self.session.rollback()  # Rollback if commit fails
                raise
        else:
            self.session.rollback()  # Rollback if there is any exception
        self.session.close()  # Always close the session
