from utils import Singleton

def get_members(cls):
    return set([att for att in dir(cls) if not att.startswith("_")])

def get_values(cls):
    temp = [getattr(cls, att) for att in dir(cls) if not att.startswith("_")]
    vals = set()
    for item in temp:
        if type(item) in (int,float,str):
            vals.add(item)
        elif type(item) in (set,list,tuple):
            for i in item:
                vals.add(i)
    return vals

def add_meta_data(cls):
    cls.Members = get_members(cls)
    cls.Values = get_values(cls)

class CompassEnum(Singleton):
    North = "north"
    South = "south"
    East = "east"
    West = "west"

class VerticalEnum(Singleton):
    Above = "above"
    Below = "below"

add_meta_data(CompassEnum)
add_meta_data(VerticalEnum)
