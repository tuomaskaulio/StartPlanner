from dataclasses import dataclass
@dataclass(slots=True)
class ClassInfo:
 id:str=""
 name:str=""
 course_name:str=""
 competitors:int=0
