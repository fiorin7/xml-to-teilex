import re

def is_adj_1_2_decl(contents):
    return contents[1].text.strip().isdigit() and ',' not in contents[0].text and contents[0].text[-2:].strip() == 'us'

def is_adv(contents):
    return contents[1].text.strip() == 'adv.' and len(re.split(', | ', contents[0].text.strip())) == 1

def is_one_form_verb(contents):
    return contents[1].text.strip().isdigit() and contents[0].text[-1].strip() == 'o'

def is_noun(contents):
    return  contents[1].text.strip() in ('m', 'f', 'n', 'mf')

# *********************

def is_verb_based_on_conj_number(contents):
    return  contents[1].text.strip() in ('2', '4')

def is_verb_based_on_conj_number_and_forms_count(contents):
    return contents[1].text.strip() in ('2', '3', '4') and len(contents[0].text.split(', ')) >= 2

# ********************

def is_conjunct(contents):
    return contents[1].text.strip() in ('coniunct.', 'coniunct') and len(re.split(', | ', contents[0].text.strip())) == 1

def is_praep(contents):
    return contents[1].text.strip().split()[0] == 'praep.' and contents[1].text.strip().split()[1] == 'с' and len(contents[1].text.strip().split()[2]) == 4

def is_multiple_form_verb(contents):
    is_verb_based_on_conj_number(contents)
    is_verb_based_on_conj_number_and_forms_count(contents)

def match_and_prefix_form_and_grammar_meta(contents):
    is_adj_1_2_decl(contents)
    is_adv(contents)
    is_one_form_verb(contents)
    is_multiple_form_verb(contents)
    is_noun(contents)
    is_conjunct(contents)
    is_praep(contents)



