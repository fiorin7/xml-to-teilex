import re

def is_adj_1_2_decl(content0, content1):
    return content1.strip().isdigit() and ',' not in content0 and content0[-2:].strip() == 'us'

def is_adv(content0, content1):
    return content1.strip() == 'adv.' and len(re.split(', | ', content0.strip())) == 1

def is_one_form_verb(content0, content1):
    return content1.strip().isdigit() and content0[-1].strip() == 'o'

def is_deponent_verb(content0, content1):
    return content1.strip().isdigit() and content0[-1].strip() == 'o' or \
        content0[-4:].strip() == 'o(r)' or content0[-2:].strip() == 'or' \
            or (content0.split(', ')[0][-2:].strip() == 'or' and content0.split(', ')[1][-3:].strip() == 'sum')

def is_simple_noun(content0, content1):
    return  content1.strip() in ('m', 'f', 'n', 'mf')

def is_greek_noun(content0, content1):
    return  content1.strip() in ('m (гр.)', 'f (гр.)', 'n (гр.)', 'mf (гр.)')

def is_noun(content0, content1):
    return any([is_simple_noun(content0, content1),
    is_greek_noun(content0, content1)])

# *********************

def is_verb_based_on_conj_number(content0, content1):
    return  content1.strip() in ('2', '4')

def is_verb_based_on_conj_number_and_forms_count(content0, content1):
    return (content1.strip() in ('2', '3', '4')) and len(content0.split(', ')) >= 2

# ********************

def is_conjunct(content0, content1):
    return content1.strip() in ('coniunct.', 'coniunct') and len(re.split(', | ', content0.strip())) == 1

def is_praep(content0, content1):
    return content1.strip().split()[0] == 'praep.' and content1.strip().split()[1] == 'с' and len(content1.strip().split()[2]) == 4

def is_multiple_form_verb(content0, content1):
    return any([is_verb_based_on_conj_number(content0, content1),
    is_verb_based_on_conj_number_and_forms_count(content0, content1)])
    

def match_and_prefix_form_and_grammar_meta(contents):
    content0 = contents[0].text
    content1 = contents[1].text
    return any([
    is_adj_1_2_decl(content0, content1),
    is_adv(content0, content1),
    is_one_form_verb(content0, content1),
    is_multiple_form_verb(content0, content1),
    is_noun(content0, content1),
    is_conjunct(content0, content1),
    is_praep(content0, content1)])





