from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimeSeriesData:
    timestamp: datetime
    value: float

@dataclass
class Anomaly:
    timestamp: datetime
    value: float
    is_anomaly: bool