from dataclasses import dataclass
@dataclass(slots=True)
class Course:
 id:str=""
 name:str=""
 length_km:float=0.0
 climb_m:int=0
 first_control:str=""
