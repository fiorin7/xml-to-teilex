from lxml import etree as et
import re
from copy import copy

def has_more_cyrillic_than_latin(string):
    pattern = '[а-яА-Я]'
    cyrillic = re.findall(pattern, string)
    latin = [x for x in string if (x.isalpha() and x not in cyrillic)]
    return len(cyrillic) > len(latin)

def fix_extra_morph_brackets(entry):
        contents = entry.contents
        extra_morph = ''
        for i in range(len(contents)):
            x = contents[i]
            if ')' in x.text:
                if x.text.strip()[-1] == ')':
                    extra_morph += x.text
                    contents[i].text = ''
                    break
                else:
                    idx = x.text.index(')')
                    extra_morph += x.text[:idx+1]
                    contents[i].text = x.text[idx+1:]
                    break
            else:
                extra_morph += x.text
                contents[i].text = ''

        extra = et.Element("extraMorph")
        extra.text = extra_morph
        entry.encoded_parts['morph_part'].append(extra)
        entry.contents = [x for x in contents if x.text]

def unknown_entry_type_find_senses_start(entry):
    contents = entry.contents
    for i in range(len(contents)):
        if contents[i].text.strip()[:2] == '1.':
            if i > 0:
                entry.encoded_parts['morph_part'] = contents[:i]
                entry.entry_type = 'unknown but clear senses start'
                return contents[i:]
        elif contents[i].get('rend' ) == 'bold' and contents[i].text.strip()[-2:] == '1.':
            number_node = copy(contents[i])
            number_node.text = '1.'
            contents[i].text = contents[i].text.replace('1.', '')
            if contents[i].text[-1] == ' ':
                number_node.text += ' '
                contents[i].text = contents[i].text[:-1]

            entry.encoded_parts['morph_part'] = contents[:i+1]
            entry.entry_type = 'unknown but clear senses start'

            res = []
            res.append(number_node)
            res.extend(contents[i+1:])
            return res

        elif contents[i].get('rend' ) == 'bold' and contents[i].text[-1] == '1' and contents[i+1].text[0] == '.':
            number_node = copy(contents[i])
            number_node.text = '1.'
            contents[i].text = contents[i].text[:-1]
            contents[i+1].text = contents[i+1].text[1:]

            entry.encoded_parts['morph_part'] = contents[:i+1]
            entry.entry_type = 'unknown but clear senses start'

            res = []
            res.append(number_node)
            res.extend(contents[i+1:])
            return res

    for i in range(len(contents)):
        if has_more_cyrillic_than_latin(contents[i].text.strip().split(' ')[0]) and not contents[i].get('rend'):
            if i > 0:
                entry.encoded_parts['morph_part'] = contents[:i]
                entry.entry_type = 'unknown but clear senses start'
                return contents[i:]



def get_form_lemma_node(text):
    form_lemma = et.Element("form")
    form_lemma.set('type', 'lemma')
    
    orth_node = et.Element("orth")
    orth_node.text = text

    form_lemma.append(orth_node)
    return form_lemma

def get_form_inflected_node(text):
    form_inflected = et.Element("form")
    form_inflected.set('type', 'inflected')
    form_inflected.text = text
    return form_inflected

def get_pc_node(text):
    pc = et.Element("pc")
    pc.text = text
    return pc

def get_gram_grp(text, gram_type="pos"):
    gram_prnt = et.Element("gramGrp")
    gram_chld = et.Element("gram")
    gram_chld.set('type', f'{gram_type}')
    gram_chld.text = text
    gram_prnt.append(gram_chld)
    return gram_prnt


def noun_xml(contents0, contents1):
    contents0_split = contents0.split(', ')
    form_lemma = get_form_lemma_node(contents0_split[0])
    pc = get_pc_node(', ')
    form_inflected = get_form_inflected_node(contents0_split[1])
    gram_grp = get_gram_grp(contents1)

    return [form_lemma, pc, form_inflected, gram_grp]

def verb_xml(entry_type, contents0, contents1):
    result = []
    contents0_split = contents0.split(', ')
    form_lemma = get_form_lemma_node(contents0_split[0])
    result.append(form_lemma)

    if len(contents0_split) > 1:
        for word in contents0_split[1:]:
            pc = get_pc_node(', ')
            form_inflected = get_form_inflected_node(word)
            result.append(pc)
            result.append(form_inflected)
    
    if entry_type != 'special_verb':
        gram_grp = get_gram_grp(contents1, "iType")
        result.append(gram_grp)

    return result
    

def adj_1_2_decl_xml(contents0, contents1):
    form_lemma = get_form_lemma_node(contents0)
    pc = get_pc_node(', ')
    gram_grp = get_gram_grp(contents1, "????")

    return [form_lemma, pc, gram_grp]

def adj_multiple_forms_xml(contents0):
    contents0_split = contents0.split(', ')
    result = []

    form_lemma = get_form_lemma_node(contents0_split[0])
    result.append(form_lemma)

    for word in contents0_split[1:]:
        form_inflected = get_form_inflected_node(word)
        pc = get_pc_node(', ')
        result.append(pc)
        result.append(form_inflected)
    
    return result

def adv_conjunct_xml(contents0, contents1):
    form_lemma = get_form_lemma_node(contents0)
    gram_grp = get_gram_grp(contents1, "????")
    return [form_lemma, gram_grp]

def praep_xml(contents0, contents1):
    form_lemma = get_form_lemma_node(contents0)
    gram_grp = get_gram_grp('praep.', "pos")
    colloc_node = et.Element('gram')
    colloc_node.set('type', 'colloc')
    colloc_node.text = contents1.replace('praep.', '')
    gram_grp.append(colloc_node)
    return [form_lemma, gram_grp]


def get_morph_info(entry_type, contents):
    contents0 = contents[0].text
    contents1 = contents[1].text

    res = None
    tag_span_of_morph_info = 0

    if entry_type == 'noun':
        res = noun_xml(contents0, contents1)
        tag_span_of_morph_info = 2

    elif entry_type in ('one_form_verb', 'multiple_form_verb', 'deponent_verb', 'special_verb'):
        res = verb_xml(entry_type, contents0, contents1)
        if entry_type == 'special_verb':
            tag_span_of_morph_info = 1
        else:
            tag_span_of_morph_info = 2

    elif entry_type == 'adj_1_2_decl':
        res = adj_1_2_decl_xml(contents0, contents1)
        tag_span_of_morph_info = 2

    elif entry_type in ('adj_like_acer_aequalis', 'adj_1_2_decl_three_forms_written_out'):
        res = adj_multiple_forms_xml(contents0)
        tag_span_of_morph_info = 1
    
    elif entry_type in ('adv', 'conjunct'):
        res = adv_conjunct_xml(contents0, contents1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'praep':
        res = praep_xml(contents0, contents1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'unknown but clear senses start':
        res = get_form_lemma_node(contents0)
        tag_span_of_morph_info = 1

    return res, tag_span_of_morph_info
