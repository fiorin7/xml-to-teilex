from lxml import etree as et
from copy import copy
from collections import deque
import re
from teifier_for_morphological_part import get_pc_node
from string import punctuation

def one_is_missing(raw_senses):
    one_spotted = False
    two_spotted = False

    for para in raw_senses:
        if '1.' in para.text:
            one_spotted = True
            break

    for para in raw_senses:
        if '2.' in para.text:
            two_spotted = True
            break
    
    return not one_spotted and two_spotted

def is_numbered_entry(raw_senses):
    for para in raw_senses:
        if '1.' in para.text:
            return True
    return False

def is_long_roman_numeral(initial):
    return (len(initial) > 2 and (initial[:3] in ('II.', 'IV.')) or (len(initial) > 3 and initial[:4] == 'III.'))

def is_subsense_number(initial):
    if len(initial) < 2:
        return False
    condition = initial[:2] == 'I.' or initial[:3] in ('II.', 'IV.') or initial[:4] == 'III.' or\
            (initial[0].isdigit() and initial[1] == '.') or\
                (initial[0].isalpha() and initial[1] == ')')
    return condition

def has_more_cyrillic_than_latin(string):
    pattern = '[а-яА-Я]'
    cyrillic = re.findall(pattern, string)
    latin = [x for x in string if (x.isalpha() and x not in cyrillic)]
    return len(cyrillic) > len(latin)

def create_sense_container_non_numbered(title_lemma):
    sense_container = et.Element("sense")
    sense_container.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{title_lemma}.1")
    return sense_container

def create_sense_container(title_lemma, sense_number=['1']):
    sense_container = et.Element("sense")
    xml_id_contents = title_lemma + '.' + ''.join(sense_number)
    sense_container.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{xml_id_contents}")

    return sense_container

def create_label(label_content):
    label = et.Element("lbl")
    label.text = label_content
    return label

def find_previous_numbers(numbers):
    collection = deque([numbers[-1]])

    for i in range(len(numbers)-1, -1, -1):
        num = numbers[i]
        if collection[0].islower():
            if num.isdigit():
                collection.appendleft(num)
                continue
        elif collection[0].isdigit():
            if num.isupper():
                collection.appendleft(num)
                continue
        elif collection[0].isupper():
            break
    
    return collection


def fix_cyrillic_letter(initial, title_lemma):
    if not is_long_roman_numeral(initial):
        if len(initial) > 1 and initial[1] == ')':
            replacements = {
                'а': 'a',
                'с': 'c',
                'е': 'e',
            }
            if initial[0] in replacements:
                initial = replacements[initial[0]] + ')'
    return initial
        

def fix_mixed_numbers(entry, initial):
    raw_senses = entry.raw_senses
    fixed = False
    if not is_long_roman_numeral(initial):
        space_in_front = False
        if len(initial) > 2:

            fixed = True

            if raw_senses[0].text[0] == ' ':
                space_in_front = True
            
            initial_node = copy(raw_senses[0])
            initial_node.text = ''
            if space_in_front:
                initial_node.text += ' '
            initial_node.text += initial[:2]

            non_initial_node = copy(raw_senses[0])

            non_initial_node.text = non_initial_node.text.replace(initial.strip()[:2], '')
            if space_in_front:
                non_initial_node.text = non_initial_node.text[1:]
            
            entry.raw_senses.pop(0)
            entry.raw_senses.insert(0, non_initial_node)
            entry.raw_senses.insert(0, initial_node)

    return(fixed)

def fix_dot_in_next_node(raw_senses):
    for i in range(len(raw_senses)):
        if raw_senses[i].text.strip().isdigit() and raw_senses[i+1].text[0] == '.':
            raw_senses[i].text += '.'
            raw_senses[i+1].text = raw_senses[i+1].text[1:]

def add_missing_one(entry, title_lemma):
    sense_container = create_sense_container(title_lemma)
    label = create_label('1.')
    sense_container.append(label)
    append_sense_container_and_label(entry, sense_container)

def create_usg_node(node_content):
    usg_node = et.Element("usg")
    usg_node.set('type', '???')
    usg_node.text = node_content
    return usg_node

def create_def_node(node_content):
    result = []
    for i in range(len(node_content.split(', '))):
        x = node_content.split(', ')[i]
        for y in range(len([z for z in x.split('; ') if z.strip() != ''])):
            def_node = et.Element("def")
            def_node.set('{http://www.w3.org/XML/1998/namespace}lang', 'bg')
            def_node.text = x.split('; ')[y]
            result.append(def_node)
            if y < len(x.split('; '))-1:
                result.append(get_pc_node('; '))
        if i < len(node_content.split(', '))-1:
            result.append(get_pc_node(', '))
    return result

def assemble_cit_nodes(cit_type, quote_content):
    if cit_type == 'translation':
        cit_node = et.Element("cit")
        cit_node.set('type', 'translation')
        cit_node.set('{http://www.w3.org/XML/1998/namespace}lang', 'bg')

    elif cit_type == 'example':
        cit_node = et.Element("cit")
        cit_node.set('type', 'example')

    quote_node = et.Element("quote")
    quote_node.text = quote_content

    cit_node.append(quote_node)

    return cit_node


def create_cit_nodes(node_content):
    result = []
    dash_in_the_end = False
    dot_in_the_end = False
    semi_colon_in_the_end = False

    if 'insignis ad deformitatem puer' in node_content:
        breakpoint
    if node_content.strip()[-1] == '–':
        if node_content[-1] == ' ':
            node_content = node_content[:-2]
            dash_node = get_pc_node('— ')
        else:
            dash_node = get_pc_node('—')
            node_content = node_content[:-1]
        dash_in_the_end = True
    
    if node_content.strip()[-1] == '.':
        if node_content[-1] == ' ':
            node_content = node_content[:-2]
            dot_node = get_pc_node('. ')
        else:
            dot_node = get_pc_node('.')
            node_content = node_content[:-1]
        dot_in_the_end = True
    
    if node_content.strip()[-1] == ';':
        if node_content[-1] == ' ':
            node_content = node_content[:-2]
            s_colon_node = get_pc_node('; ')
        else:
            s_colon_node = get_pc_node(';')
            node_content = node_content[:-1]
        semi_colon_in_the_end = True
        
    
    split_contents = node_content.split('; ')
    split_contents = [x for x in split_contents if x.strip() != '']

    for y in range(len(split_contents)):
        x = split_contents[y]

        for i in range(len(x.split(' '))):
            word = x.split(' ')[i]
            if word.strip() == '' and i != len(x.split(' '))-1:
                continue

            if has_more_cyrillic_than_latin(word) and not (len(word) == 1 and not has_more_cyrillic_than_latin(x.split(' ')[i+1])):
                if i > 0:
                    if not (x.split(' ')[0] == '' and i == 1):
                        cit_node = assemble_cit_nodes('example', ' '.join((x.split(' ')[:i])) + ' ')
                        result.append(cit_node)
                if x.split(' ')[0] == '' and i == 1:
                    cit_node = assemble_cit_nodes('translation', ' '.join(x.split(' ')))
                else:
                    cit_node = assemble_cit_nodes('translation', ' '.join(x.split(' ')[i:]))
                result.append(cit_node)
                break
            elif i == len(x.split(' ')) - 1:
                cit_node = assemble_cit_nodes('example', ' '.join((x.split(' '))))
                result.append(cit_node)
                break
            
        if y < (len(split_contents)-1):
            result.append(get_pc_node('; '))
            # print(x)
            # print('kek')
    
    
    if dot_in_the_end:
        result.append(dot_node)
    if semi_colon_in_the_end:
        result.append(s_colon_node)
    if dash_in_the_end:
        result.append(dash_node)
    
    return result


def create_subsense_number_node(title_lemma, numbers, initial):
    sense_container = create_sense_container(title_lemma, find_previous_numbers(numbers))
    label = create_label(initial)
    sense_container.append(label)
    return sense_container
            
def append_sense_container_and_label(entry, new_node):
    assigned = False
    for i in range(len(entry.encoded_parts['senses'])-1, -1, -1):
        node = entry.encoded_parts['senses'][i]
        if node.tag == 'sense':
            if node.attrib['{http://www.w3.org/XML/1998/namespace}id'][-1].isupper() and new_node.attrib['{http://www.w3.org/XML/1998/namespace}id'][-1].islower():
                children = node.getchildren()
                for i in range(len(children)-1, -1, -1):
                    child = children[i]
                    if child.tag == 'sense' and child.attrib['{http://www.w3.org/XML/1998/namespace}id'][-1].isdigit():
                        child.append(new_node)
                        assigned = True
                        last_sense_container = new_node
                        break
            if node.attrib['{http://www.w3.org/XML/1998/namespace}id'][-1].isdigit() and new_node.attrib['{http://www.w3.org/XML/1998/namespace}id'][-1].islower():
                entry.encoded_parts['senses'][i].append(new_node)
                assigned = True
                last_sense_container = new_node
                break
            if node.attrib['{http://www.w3.org/XML/1998/namespace}id'][-1].isupper() and new_node.attrib['{http://www.w3.org/XML/1998/namespace}id'][-1].isdigit():
                entry.encoded_parts['senses'][i].append(new_node)
                assigned = True
                last_sense_container = new_node
                break
    if not assigned:
        entry.encoded_parts['senses'].append(new_node)
    # [print(et.tostring(x, encoding='utf8', pretty_print=True).decode('utf8')) for x in entry.encoded_parts['senses']]
    # [print(x.text) for x in entry.encoded_parts['senses']]
    # entry.encoded_parts['senses'].append(new_node)

def encode_senses(entry):
    raw_senses = entry.raw_senses
    title_lemma = entry.title_lemma
    last_sense_container = None

    if raw_senses:
        fix_dot_in_next_node(raw_senses)
    numbers = []

    if raw_senses and one_is_missing(raw_senses):
        add_missing_one(entry, title_lemma)
        numbers.append('1')
    
    if raw_senses and not is_numbered_entry(raw_senses):
        entry.encoded_parts['senses'].append(create_sense_container_non_numbered(title_lemma))
        last_sense_container = entry.encoded_parts['senses'][0]
        numbers.append('1')


    while raw_senses:
        encoded = False
        initial = raw_senses[0].text.strip()
        initial = fix_cyrillic_letter(initial, title_lemma)

        # what do
        if is_subsense_number(initial):

            if fix_mixed_numbers(entry, initial):
                continue

            sense_number = initial[0]
            if sense_number == 'I':
                sense_number = initial[:-1]
            numbers.append(sense_number)
            last_sense_container = create_subsense_number_node(title_lemma, numbers, initial)
            append_sense_container_and_label(entry, last_sense_container)
            encoded = True
        
        else:
            content_node = [raw_senses[0]]

            if raw_senses[0].text.strip() in punctuation or raw_senses[0].text.strip() == '–':
                content_node = get_pc_node(raw_senses[0].text)

            elif raw_senses[0].get('rend') == "italic":
                content_node = [create_usg_node(raw_senses[0].text)]
            
            elif raw_senses[0].get('rend') == "bold" and has_more_cyrillic_than_latin(raw_senses[0].text):
                content_node = create_def_node(raw_senses[0].text)
            
            elif (not last_sense_container or len([x for x in last_sense_container.getchildren() if x.tag in ('cit', 'quote')]) == 0) and \
                has_more_cyrillic_than_latin(raw_senses[0].text.strip().split(' ')[0]):

                    dash_in_the_end = False
                    dot_in_the_end = False
                    semi_colon_in_the_end = False

                    node_content = raw_senses[0].text

                    if node_content.strip()[-1] == '–':
                        if node_content[-1] == ' ':
                            node_content = node_content[:-2]
                            dash_node = get_pc_node('— ')
                        else:
                            dash_node = get_pc_node('—')
                            node_content = node_content[:-1]
                        dash_in_the_end = True
                    
                    if node_content.strip()[-1] == '.':
                        if node_content[-1] == ' ':
                            node_content = node_content[:-2]
                            dot_node = get_pc_node('. ')
                        else:
                            dot_node = get_pc_node('.')
                            node_content = node_content[:-1]
                        dot_in_the_end = True
                    
                    if node_content.strip()[-1] == ';':
                        if node_content[-1] == ' ':
                            node_content = node_content[:-2]
                            s_colon_node = get_pc_node('; ')
                        else:
                            s_colon_node = get_pc_node(';')
                            node_content = node_content[:-1]
                        semi_colon_in_the_end = True
                    
                    content_node = []

                    found_latin = False

                    for i in range(len(node_content.split(' '))):
                        word = node_content.split(' ')[i]
                        if word.strip() == '':
                            continue
                        if has_more_cyrillic_than_latin(word) and not (len(word) == 1 and not has_more_cyrillic_than_latin(node_content.split(' ')[i+1])):
                            pass
                        else:
                            found_latin = True
                            break
                    if not found_latin:
                        def_node = create_def_node(node_content)
                        content_node.extend(def_node)
                        if dot_in_the_end:
                            content_node.append(dot_node)
                        if semi_colon_in_the_end:
                            content_node.append(s_colon_node)
                        if dash_in_the_end:
                            content_node.append(dash_node)
                    else:
                        def_node = create_def_node(' '.join(node_content.split(' ')[:i]) + ' ')
                        content_node.extend(def_node)
                        cit_node = create_cit_nodes(' '.join(node_content.split(' ')[i:]))
                        content_node.extend(cit_node)
                        if dot_in_the_end:
                            content_node.append(dot_node)
                        if semi_colon_in_the_end:
                            content_node.append(s_colon_node)
                        if dash_in_the_end:
                            content_node.append(dash_node)

            
            
            else:
                content_node = create_cit_nodes(raw_senses[0].text)

            if last_sense_container is not None:
                [last_sense_container.append(x) for x in content_node]
            else:
                [entry.encoded_parts['senses'].append(x) for x in content_node]

        raw_senses.pop(0)

    
    # print(range(len(entry.encoded_parts['senses'])-1, -1, -1))
    # [print(et.tostring(x, encoding='utf8', pretty_print=True).decode('utf8')) for x in entry.encoded_parts['senses']]
    [print(x.attrib) for x in entry.encoded_parts['senses']]



        
