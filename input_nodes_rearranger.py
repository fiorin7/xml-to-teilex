from lxml import etree as et
from copy import copy
from utils import is_empty_string, SafeString
from node_factory import get_ns, create_bold_hi_node, create_normal_hi_node, create_italic_hi_node


def fix_morph_numbers(contents):

    def number_one_is_in_c0(content0):
        return len(content0.strip()) > 2 and content0.strip().endswith('1.')
    
    def number_one_and_a_are_in_c0(content0):
        return content0.strip().endswith('1. a)')


    def gram_number_is_in_c1(content0, content1):
        first_word_stripped = content0.split(', ')[0].strip()
        is_verb = first_word_stripped.endswith(('o', 'or', 'o(r)')) and content1.strip().startswith(('1', '2', '3', '4'))
        is_adj = len(content0.split(', ')) == 1 and content0.strip().endswith('us') and content1.strip().startswith('3')
        return  (is_verb or is_adj) and len(content1.strip()) > 1  and content1.strip()[1] != '.'

    content0_node = contents[0]
    content1_node = contents[1]
    content0 = SafeString(contents[0].text)
    content1 = SafeString(contents[1].text)

    result = []

    if number_one_is_in_c0(content0):
        number_node_text = '1.'
        if content0_node.text.endswith(' '):
            number_node_text += ' '
        content0_2_node = create_bold_hi_node(number_node_text)
        content0_node.text = content0_node.text.rstrip()[:-2]
        result.append(content0_node)
        result.append(content0_2_node)
        [result.append(x) for x in contents[1:]]

        return result
    
    elif number_one_and_a_are_in_c0(content0):
        number_node_text = '1. '
        a_node_text = 'a)'
        if content0_node.text.endswith(' '):
            a_node_text += ' '
        content0_2_node = create_bold_hi_node(number_node_text)
        content0_3_node = create_bold_hi_node(a_node_text)
        content0_node.text = content0_node.text.rstrip()[:-5]

        result.extend([content0_node, content0_2_node, content0_3_node])
        [result.append(x) for x in contents[1:]]

        return result

    
    elif gram_number_is_in_c1(content0, content1):
        result.append(content0_node)
        number = ''
        if content1.startswith(' '):
            number += ' '
        number += content1.lstrip()[0]
        content0_2_node = create_normal_hi_node(number)
        content1_node.text = content1_node.text.lstrip()[1:]
        result.append(content0_2_node)
        result.append(content1_node)
        [result.append(x) for x in contents[2:]]
        
        return result


def fix_separated_brackets(contents):

    def two_opening_brackets_in_a_row():
        return '(' in contents[i].text and opening_brackets_idx
    
    def found_opening_bracket_no_closing_bracket_in_node():
        return '(' in contents[i].text and not ')' in contents[i].text
    
    def opening_bracket_in_beginning_of_node():
        return (idx_in_text == 1 and contents[i].text[0] == ' ') or idx_in_text == 0
    
    def found_closing_bracket_matching_opening_bracket_in_node():
        return ')' in contents[i].text and opening_brackets_idx is not None
    
    def closing_bracket_in_end_of_node():
        return contents[i].text.endswith((') ', ')')) and idx_in_text in (len(contents[i].text)-1, len(contents[i].text)-2)
    
    def theres_an_opening_bracket_but_no_closing_bracket_yet():
        return opening_brackets_idx is not None
    

    new_contents = []
    old_contents = copy(contents)
    opening_brackets_idx = None
    opening_brackets_content = ''
    italic = False
    error = False
    i = 0


    while contents:
        if two_opening_brackets_in_a_row():
            error = True
            break


        if found_opening_bracket_no_closing_bracket_in_node():
            opening_brackets_idx = i
            idx_in_text = contents[i].text.index('(')
            if opening_bracket_in_beginning_of_node():
                opening_brackets_content = contents[i].text
                if contents[i].get('rend') == 'italic':
                    italic = True
            else:
                opening_brackets_content = contents[i].text[idx_in_text:]
                contents[i].text = contents[i].text.replace(opening_brackets_content, '')
                if contents[i].get('rend') == 'italic':
                    italic = True
                new_contents.append(contents[i])
        
        elif found_closing_bracket_matching_opening_bracket_in_node():
            idx_in_text = contents[i].text.index(')')
            current_content = ''
            extra_text_to_append = False

            if closing_bracket_in_end_of_node():
                opening_brackets_content += contents[i].text
            else:
                current_content = contents[i].text[:idx_in_text+1]
                opening_brackets_content += current_content
                contents[i].text = contents[i].text.replace(current_content, '')
                extra_text_to_append = True
                
            if italic:
                new_contents.append(create_italic_hi_node(opening_brackets_content))
            else:
                new_contents.append(create_normal_hi_node(opening_brackets_content))

            if extra_text_to_append:
                new_contents.append(contents[i])

            opening_brackets_idx = None
            opening_brackets_content = ''
            italic = False
        
        elif theres_an_opening_bracket_but_no_closing_bracket_yet():
            opening_brackets_content += contents[i].text
            if contents[i].get('rend') == 'italic':
                italic = True
        
        else:
            new_contents.append(contents[i])

        contents.pop(0)
        

    if error:
        new_contents = old_contents
    
    return new_contents


def fix_misplaced_punct(contents):
    for i in range(len(contents)):
        if not is_empty_string(contents[i].text) and contents[i].text.strip()[0] in r'!%),.:;?]|}' and i > 0 and len(contents[i].text.strip()) >= 2:
            if contents[i].text[0] == ' ':
                contents[i-1].text += ' ' + contents[i].text.strip()[0]
                contents[i].text = contents[i].text[2:]
            else:
                contents[i-1].text += contents[i].text.strip()[0]
                contents[i].text = contents[i].text[1:]
    return contents

