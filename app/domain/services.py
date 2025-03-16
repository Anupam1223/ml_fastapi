class TimeSeriesService:
    @staticmethod
    def validate_data(value: float):
        if value < 0:
            raise ValueError("Value must be non-negative")
