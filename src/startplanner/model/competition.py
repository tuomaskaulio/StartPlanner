from dataclasses import dataclass,field
from datetime import datetime
from .classinfo import ClassInfo
from .course import Course
from .competitor import Competitor
from .history import HistoryEvent
from .settings import Settings
@dataclass
class Competition:
 name:str=""
 classes:dict[str,ClassInfo]=field(default_factory=dict)
 courses:dict[str,Course]=field(default_factory=dict)
 competitors:list[Competitor]=field(default_factory=list)
 history:list[HistoryEvent]=field(default_factory=list)
 settings:Settings=field(default_factory=Settings)
 def add_history(self,msg:str): self.history.append(HistoryEvent(datetime.now(),msg))
