from dataclasses import dataclass
@dataclass(slots=True)
class Competitor:
 first_name:str=""
 last_name:str=""
 club:str=""
 class_name:str=""
