import re
from typing import List, Optional

def has_more_cyrillic_than_latin(string):
    pattern = '[а-яА-Я]'
    cyrillic = re.findall(pattern, string)
    latin = [x for x in string if (x.isalpha() and x not in cyrillic)]
    return len(cyrillic) > len(latin)

def is_empty_string(text):
    return text.strip() == ''


class SafeList(list):
    def __getitem__(self, i):
        if i >= 0 and i < len(self):
            return super().__getitem__(i)
        else:
            return None

class SafeString(str):
    def __getitem__(self, i):
        if i >= 0 and i < len(self):
            return super().__getitem__(i)
        else:
            return None
    
    def strip(self):
        return SafeString(super().strip())
    
    def rstrip(self):
        return SafeString(super().rstrip())
    
    def lstrip(self):
        return SafeString(super().lstrip())
    
    # def split(self, sep: Optional[str] = ..., maxsplit: int = ...) -> List[str]:
    #     return SafeList(super().split())


# x = SafeString('b ')

# print('***'+x.strip()+'***')

# kek = 'kek'
# kek.split()