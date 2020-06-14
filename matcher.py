import re

def is_adj_1_2_decl(content0s, content1s):
    return content1s.isdigit() and ',' not in content0s and content0s[-2:] == 'us'

def is_adj_1_2_decl_three_forms_written_out(content0s):
    split_c0s = content0s.split(', ')
    return len(split_c0s) == 3 and split_c0s[-2].strip()[-1] == 'a' and\
        split_c0s[-1].strip()[-2:] == 'um'

def is_adj_like_acer_aequalis(content0s):
    split_c0s = content0s.split(', ')
    return len(split_c0s) in (2, 3) and split_c0s[-2].strip()[-2:] == 'is' and\
        split_c0s[-1].strip()[-1] in ('e', 'е')

def is_adv(content0s, content1s):
    return content1s == 'adv.' and len(re.split(', | ', content0s)) == 1

def is_one_form_verb(content0s, content1s):
    return content1s.isdigit() and content0s[-1] == 'o'

def is_deponent_verb(content0s, content1s):
    return content1s.isdigit() and (content0s[-1] == 'o' or \
        (content0s.split(', ')[0].strip()[-2:] == 'or' and content0s.split(', ')[1].strip()[-3:] == 'sum') or\
            content0s[-4:] == 'o(r)' or content0s[-2:] == 'or')

def is_special_verb(content0):
    first_word = content0.split(', ')[0].strip()
    return first_word[-4:] == '-sum' or first_word[-5:] == '-fero' or first_word[-3:] == '-eo'

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
    return (content1s in ('2', '3', '4')) and len(content0s.split(', ')) >= 2

# ********************

def is_conjunct(content0s, content1s):
    return content1s in ('coniunct.', 'coniunct') and len(re.split(', | ', content0s)) == 1

def is_praep(content1s):
    return content1s.split()[0] == 'praep.' and content1s.split()[1] == 'с' and len(content1s.split()[2]) == 4

def is_multiple_form_verb(content0s, content1s):
    return any([is_verb_based_on_conj_number(content1s),
    is_verb_based_on_conj_number_and_forms_count(content0s, content1s)])
    

def match_and_prefix_form_and_grammar_meta(contents):
    content0 = contents[0].text
    content1 = contents[1].text
    content0s = contents[0].text.strip()
    content1s = contents[1].text.strip()
    
    return any([
    is_adj_1_2_decl(content0s, content1s),
    is_adj_like_acer_aequalis(content0s),
    is_adj_1_2_decl_three_forms_written_out(content0s),
    is_adv(content0s, content1s),
    is_one_form_verb(content0s, content1s),
    is_multiple_form_verb(content0s, content1s),
    is_deponent_verb(content0s, content1s),
    is_special_verb(content0),
    is_noun(content1s),
    is_conjunct(content0s, content1s),
    is_praep(content1s)])





