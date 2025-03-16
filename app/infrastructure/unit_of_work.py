from app.infrastructure.db import SessionLocal


class UnitOfWork:
    def __enter__(self):
        self.session = SessionLocal()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()
