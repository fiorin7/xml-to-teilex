from lxml import etree as et
from copy import copy
from collections import deque
import re

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
    sense_container.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{title_lemma}")
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
        


# def create_sense_container(title_lemma, sense_number='1'):
#     if one_is_missing(raw_senses):
#         sense_container = assemble_sense_container(title_lemma)
    
#     else:
#         sense_container = assemble_sense_container(title_lemma)

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
    if raw_senses[0].text.strip().isdigit() and raw_senses[1].text[0] == '.':
        raw_senses[0].text += '.'
        raw_senses[1].text = raw_senses[1].text[1:]

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

def create_subsense_number_node(title_lemma, numbers, initial):
    sense_container = create_sense_container(title_lemma, find_previous_numbers(numbers))
    label = create_label(initial)
    sense_container.append(label)
    return sense_container


# def add_subsense_number_node(title_lemma, numbers, initial, entry):
#     append_sense_container_and_label(entry, sense_container)

def append_contents():
    pass
            
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
    if raw_senses:
        fix_dot_in_next_node(raw_senses)
    numbers = []

    if raw_senses and one_is_missing(raw_senses):
        add_missing_one(entry, title_lemma)
        numbers.append('1')
    
    if raw_senses and not is_numbered_entry(raw_senses):
        entry.encoded_parts['senses'].append(create_sense_container_non_numbered(title_lemma))

    last_sense_container = None

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
            content_node = raw_senses[0]

            if raw_senses[0].get('rend') == "italic":
                content_node = create_usg_node(raw_senses[0].text)
            
            # if not encoded:
            #     entry.encoded_parts['senses'].append(raw_senses[0])

            if last_sense_container:
                last_sense_container.append(content_node)
                print('kek')
            else:
                entry.encoded_parts['senses'].append(content_node)
            # encoded = True

        raw_senses.pop(0)

    
    # print(range(len(entry.encoded_parts['senses'])-1, -1, -1))
    # [print(et.tostring(x, encoding='utf8', pretty_print=True).decode('utf8')) for x in entry.encoded_parts['senses']]
    [print(x.attrib) for x in entry.encoded_parts['senses']]



        