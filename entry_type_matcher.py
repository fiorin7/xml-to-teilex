import re
from utils import SafeString

def is_adj_1_2_decl(content0s, content1s):
    return content1s.isdigit() and ',' not in content0s and content0s.endswith('us')

def is_adj_1_2_decl_three_forms_written_out(content0s):
    split_c0s = content0s.split(', ')
    return len(split_c0s) == 3 and split_c0s[-2].strip().endswith('a') and\
        split_c0s[-1].strip().endswith('um')

def is_adj_like_acer_aequalis(content0s):
    split_c0s = content0s.split(', ')
    return len(split_c0s) in (2, 3) and split_c0s[-2].strip().endswith('is') and\
        split_c0s[-1].strip().endswith(('e', 'е'))

def is_adv(content0s, content1s):
    return content1s == 'adv.' and len(re.split(', | ', content0s)) == 1

def is_one_form_verb(content0s, content1s):
    return content1s.isdigit() and content0s.endswith('o')

def is_deponent_verb(content0s, content1s):
    if len(content0s.split(', ')) == 1:
        return content1s.isdigit() and  content0s.endswith(('o(r)', 'or'))
    else:
        return content1s.isdigit() and content0s.split(', ')[1].strip().endswith('sum')

def is_special_verb(content0):
    first_word = content0.split(', ')[0].strip()
    return first_word.endswith(('-sum', '-fero', '-eo')) and '1.' not in content0

def is_simple_noun(content1s):
    return  content1s in ('m', 'f', 'n', 'mf')

def is_greek_noun(content1s):
    return  content1s in ('m (гр.)', 'f (гр.)', 'n (гр.)', 'mf (гр.)')

def is_noun(content1s):
    return any([is_simple_noun(content1s),
    is_greek_noun(content1s)])

# *********************

def is_verb_based_on_conj_number(content1s):
    return  content1s in ('2', '4')

def is_verb_based_on_conj_number_and_forms_count(content0s, content1s):
    return (content1s in ('1', '2', '3', '4')) and len(content0s.split(', ')) >= 2 and content0s.split(', ')[0].endswith(('o', 'm', 't', 'i'))

# ********************

def is_conjunct(content0s, content1s):
    return content1s in ('coniunct.', 'coniunct') and len(re.split(', | ', content0s)) == 1

def is_praep(content1s):
    if len(content1s.split(' ')) == 3:
        return content1s.split(' ')[0] == 'praep.' and content1s.split(' ')[1] == 'с' and len(content1s.split(' ')[2]) == 4

def is_multiple_form_verb(content0s, content1s):
    return any([is_verb_based_on_conj_number(content1s),
    is_verb_based_on_conj_number_and_forms_count(content0s, content1s)])
    

def match_entry_type(contents):
    content0 = SafeString(contents[0].text)
    content1 = SafeString(contents[1].text)
    content0s = content0.strip()
    content1s = content1.strip()

    entry_type = ''

    if is_adj_1_2_decl(content0s, content1s):
        entry_type = 'adj_1_2_decl'
    elif is_adj_like_acer_aequalis(content0s):
        entry_type = 'adj_like_acer_aequalis'
    elif is_adj_1_2_decl_three_forms_written_out(content0s):
        entry_type = 'adj_1_2_decl_three_forms_written_out'
    elif is_adv(content0s, content1s):
        entry_type = 'adv'
    elif is_one_form_verb(content0s, content1s):
        entry_type = 'one_form_verb'
    elif is_multiple_form_verb(content0s, content1s):
        entry_type = 'multiple_form_verb'
    elif is_deponent_verb(content0s, content1s):
        entry_type = 'deponent_verb'
    elif is_special_verb(content0):
        entry_type = 'special_verb'
    elif is_noun(content1s):
        entry_type = 'noun'
    elif is_conjunct(content0s, content1s):
        entry_type = 'conjunct'
    elif is_praep(content1s):
        entry_type = 'praep'

    elif content1s[:2] in ('1.', 'I.'):
        entry_type = 'unknown but clear senses start'

    else:
        entry_type = 'UNKNOWN'
    
    return entry_type
    




