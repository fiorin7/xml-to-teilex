import re
from typing import List

def has_more_cyrillic_than_latin(string):
    if string == None:
        return

    pattern = '[а-яА-Я]'
    cyrillic = re.findall(pattern, string)
    latin = [x for x in string if (x.isalpha() and x not in cyrillic)]
    return len(cyrillic) > len(latin)

def is_empty_string(text):
    return text.strip() == ''


class SafeList(list):
    def __getitem__(self, i):
        try:
            return super().__getitem__(i)
        except IndexError:
            return None

class SafeString(str):
    def __getitem__(self, i):
        try:
            return super().__getitem__(i)
        except IndexError:
            return None
    
    def strip(self):
        return SafeString(super().strip())
    
    def rstrip(self):
        return SafeString(super().rstrip())
    
    def lstrip(self):
        return SafeString(super().lstrip())
    
    def split(self, *args, **kwargs) -> List[str]:
        return SafeList(super().split(*args, **kwargs))
