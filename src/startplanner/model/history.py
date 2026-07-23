from dataclasses import dataclass
from datetime import datetime
@dataclass(slots=True)
class HistoryEvent:
 timestamp:datetime
 message:str
