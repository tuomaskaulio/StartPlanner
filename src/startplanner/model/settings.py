from dataclasses import dataclass
@dataclass(slots=True)
class Settings:
 first_start:str="18:00"
 same_course_interval:int=2
 first_control_limit:int=1
 class_gap:int=2
