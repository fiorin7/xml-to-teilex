from lxml import etree as et
import re
from copy import copy
import node_factory as nf
from string import punctuation

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
                if x.text.strip().endswith(')'):
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

        entry.contents = [x for x in contents if x.text]
        return nf.create_extra_morph(extra_morph)

def deal_with_unknown_entry(entry):
    senses = unknown_entry_type_find_senses_start(entry)
    if senses:
        unknown_entry_partially_encode(entry)
        return senses

def unknown_entry_type_find_senses_start(entry):
    contents = entry.contents
    for i in range(len(contents)):
        if contents[i].text.strip().startswith('1.'):
            if i > 0:
                entry.encoded_parts['morph_part'] = contents[:i]
                entry.entry_type = 'unknown but clear senses start'
                return contents[i:]
        elif contents[i].get('rend' ) == 'bold' and contents[i].text.strip().endswith('1.'):
            number_node = copy(contents[i])
            number_node.text = '1.'
            if contents[i].text.endswith(' '):
                number_node.text += ' '
                contents[i].text = contents[i].text[:-1]
            contents[i].text = contents[i].text.replace('1.', '')

            entry.encoded_parts['morph_part'] = contents[:i+1]
            entry.entry_type = 'unknown but clear senses start'

            res = []
            res.append(number_node)
            res.extend(contents[i+1:])
            return res

        elif contents[i].get('rend' ) == 'bold' and contents[i].text.endswith('1') and contents[i+1].text.startswith('.'):
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

def unknown_entry_partially_encode(entry):
    old_morph_part = copy(entry.encoded_parts['morph_part'])
    entry.encoded_parts['morph_part'] = []

    counter = 0
    while old_morph_part:
        content_node = [old_morph_part[0]]
        if counter == 0:
            content_node = unknown_initial_xml(content_node[0].text)
        
        elif old_morph_part[0].text.strip().startswith('(') and old_morph_part[0].text.strip().endswith(')'):
            content_node = [nf.create_extra_morph(old_morph_part[0].text)]
            
        elif old_morph_part[0].text.strip() in punctuation or old_morph_part[0].text.strip() == '–':
                content_node = [nf.create_pc_node(old_morph_part[0].text)]

        elif old_morph_part[0].get('rend') == "italic":
            if old_morph_part[0].text.strip() in ('m', 'f', 'n'):
                content_node = [nf.create_gram_grp(old_morph_part[0].text)]

            elif len(entry.encoded_parts['morph_part']) == 1 and len(old_morph_part) >= 2 and old_morph_part[1].get('rend' ) == 'bold' and old_morph_part[0].text.strip() == 'и' and entry.encoded_parts['morph_part'][-1].tag == nf.get_ns('form'):
                content_node = []
                entry.encoded_parts['morph_part'][-1].append(old_morph_part[0])
                entry.encoded_parts['morph_part'][-1].append(nf.create_orth_node(old_morph_part[1].text))
                old_morph_part.pop(0)

            else:
                content_node = nf.create_usg_node(old_morph_part[0].text)
        
        elif old_morph_part[0].text.strip() in ('1', '2', '3', '4') and (len(old_morph_part) == 1 or old_morph_part[1].text.strip() != '.'):
            content_node = [nf.create_gram_grp(old_morph_part[0].text, 'iType')]
        
        [entry.encoded_parts['morph_part'].append(x) for x in content_node]
        old_morph_part.pop(0)
        counter += 1


def unknown_initial_xml(content0):
    res = []
    content0_split = [x for x in content0.split(', ') if x.strip() != '']
    for i in range(len(content0_split)):
        if i == 0:
            form_lemma = nf.create_form_lemma_node(content0_split[i])
            res.append(form_lemma)

            if len(content0_split) > 1:
                pc = nf.create_pc_node(', ')
                res.append(pc)
        elif i == len(content0_split)-1:
            form_inflected = nf.create_form_inflected_node(content0_split[i])
            res.append(form_inflected)
        else:
            form_inflected = nf.create_form_inflected_node(content0_split[i])
            pc = nf.create_pc_node(', ')
            res.append(form_inflected)
            res.append(pc)
    return res


def noun_xml(content0, content1):
    content0_split = content0.split(', ')
    form_lemma = nf.create_form_lemma_node(content0_split[0])
    pc = nf.create_pc_node(', ')
    form_inflected = nf.create_form_inflected_node(content0_split[1])
    gram_grp = nf.create_gram_grp(content1)

    return [form_lemma, pc, form_inflected, gram_grp]

def verb_xml(entry_type, content0, content1):
    result = []
    content0_split = content0.split(', ')
    form_lemma = nf.create_form_lemma_node(content0_split[0])
    result.append(form_lemma)

    if len(content0_split) > 1:
        for word in content0_split[1:]:
            pc = nf.create_pc_node(', ')
            form_inflected = nf.create_form_inflected_node(word)
            result.append(pc)
            result.append(form_inflected)
    
    if entry_type != 'special_verb':
        gram_grp = nf.create_gram_grp(content1, "iType")
        result.append(gram_grp)

    return result
    

def adj_1_2_decl_xml(content0, content1):
    form_lemma = nf.create_form_lemma_node(content0)
    gram_grp = nf.create_gram_grp(content1, "????")

    return [form_lemma, gram_grp]

def adj_multiple_forms_xml(content0):
    content0_split = content0.split(', ')
    result = []

    form_lemma = nf.create_form_lemma_node(content0_split[0])
    result.append(form_lemma)

    for word in content0_split[1:]:
        form_inflected = nf.create_form_inflected_node(word)
        pc = nf.create_pc_node(', ')
        result.append(pc)
        result.append(form_inflected)
    
    return result

def adv_conjunct_xml(content0, content1):
    form_lemma = nf.create_form_lemma_node(content0)
    gram_grp = nf.create_gram_grp(content1, "????")
    return [form_lemma, gram_grp]




def get_morph_info(entry_type, contents):
    content0 = contents[0].text
    content1 = contents[1].text

    res = None
    tag_span_of_morph_info = 0

    if entry_type == 'noun':
        res = noun_xml(content0, content1)
        tag_span_of_morph_info = 2

    elif entry_type in ('one_form_verb', 'multiple_form_verb', 'deponent_verb', 'special_verb'):
        res = verb_xml(entry_type, content0, content1)
        if entry_type == 'special_verb':
            tag_span_of_morph_info = 1
        else:
            tag_span_of_morph_info = 2

    elif entry_type == 'adj_1_2_decl':
        res = adj_1_2_decl_xml(content0, content1)
        tag_span_of_morph_info = 2

    elif entry_type in ('adj_like_acer_aequalis', 'adj_1_2_decl_three_forms_written_out'):
        res = adj_multiple_forms_xml(content0)
        tag_span_of_morph_info = 1
    
    elif entry_type in ('adv', 'conjunct'):
        res = adv_conjunct_xml(content0, content1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'praep':
        res = nf.create_praep_xml(content0, content1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'unknown but clear senses start':
        print(content0)
        pass
    
    elif entry_type == 'UNKNOWN':
        print(content0)
        pass

    return res, tag_span_of_morph_info
