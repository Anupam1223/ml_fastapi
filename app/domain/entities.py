"""this is my domain module, i want to have entities for time series related data"""

from dataclasses import dataclass
from datetime import datetime

@dataclass
class TimeSeriesData:
    timestamp: datetime
    value: float

