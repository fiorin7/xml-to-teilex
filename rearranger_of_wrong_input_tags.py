from utils import is_empty_string
from lxml import etree as et
from copy import copy
from utils import SafeString

def make_bold_hi_node(text):
    hi_node = et.Element("hi")
    hi_node.set('rend', 'bold')
    hi_node.text = text
    return hi_node

def make_normal_hi_node(text):
    hi_node = et.Element("hi")
    hi_node.text = text
    return hi_node

def make_italic_hi_node(text):
    hi_node = et.Element("hi")
    hi_node.set('rend', 'italic')
    hi_node.text = text
    return hi_node

def number_one_is_in_c0(content0):
    return content0.strip().endswith('1.')

def gram_number_is_in_c1(content0, content1):
    first_word_stripped = content0.split(', ')[0].strip()
    is_verb = first_word_stripped.endswith(('o', 'or', 'o(r)'))
    is_adj = len(content0.split(', ')) == 1 and content0.strip().endswith('us')
    return  (is_verb or is_adj) and len(content1.strip()) > 1 and content1.strip()[0].isdigit() and content1.strip()[1] != '.'


def fix_wrong_tags_in_morph_part(contents):
    content0_node = contents[0]
    content1_node = contents[1]
    content0 = SafeString(contents[0].text)
    content1 = SafeString(contents[1].text)

    result = []

    if number_one_is_in_c0(content0):
        number_node_text = '1.'
        if content0_node.text.endswith(' '):
            number_node_text += ' '
        content0_2_node = make_bold_hi_node(number_node_text)
        content0_node.text = content0_node.text.rstrip()[:-2]
        result.append(content0_node)
        result.append(content0_2_node)
        [result.append(x) for x in contents[1:]]
        # print('***************')
        # for x in result[:4]:
        #     print(et.tostring(x, encoding='utf8', pretty_print=True).decode('utf8'))
    

        return result
    
    elif gram_number_is_in_c1(content0, content1):
        result.append(content0_node)
        number = ''
        if content1.startswith(' '):
            number += ' '
        number += content1.lstrip()[0]
        content0_2_node = make_normal_hi_node(number)
        content1_node.text = content1_node.text.lstrip()[1:]
        result.append(content0_2_node)
        result.append(content1_node)
        [result.append(x) for x in contents[2:]]
        # print('***************')
        # for x in result[:4]:
        #     print(et.tostring(x, encoding='utf8', pretty_print=True).decode('utf8'))
        
        return result

def fix_separated_brackets(contents):
    if 'apto' in contents[0].text:
        breakpoint
    new_contents = []
    old_contents = copy(contents)
    opening_brackets_idx = None
    opening_brackets_content = ''
    italic = False
    error = False
    i = 0
    while contents:
        if '(' in contents[i].text and opening_brackets_idx:
            error = True
            break


        if '(' in contents[i].text and not ')' in contents[i].text:
            opening_brackets_idx = i
            idx_in_text = contents[i].text.index('(')
            if (idx_in_text == 1 and contents[i].text[0] == ' ') or idx_in_text == 0:
                opening_brackets_content = contents[i].text
                if contents[i].get('rend') == 'italic':
                    italic = True
            else:
                opening_brackets_content = contents[i].text[idx_in_text:]
                contents[i].text = contents[i].text.replace(opening_brackets_content, '')
                if contents[i].get('rend') == 'italic':
                    italic = True
                new_contents.append(contents[i])
        
        elif ')' in contents[i].text and opening_brackets_idx is not None:
            idx_in_text = contents[i].text.index(')')
            current_content = ''
            if contents[i].text.endswith((') ', ')')):
                opening_brackets_content += contents[i].text

                if italic:
                    new_contents.append(make_italic_hi_node(opening_brackets_content))
                else:
                    new_contents.append(make_normal_hi_node(opening_brackets_content))

                opening_brackets_idx = None
                opening_brackets_content = ''
                italic = False
            else:
                current_content = contents[i].text[:idx_in_text+1]
                opening_brackets_content += current_content
                contents[i].text = contents[i].text.replace(current_content, '')
                
                if italic:
                    new_contents.append(make_italic_hi_node(opening_brackets_content))
                else:
                    new_contents.append(make_normal_hi_node(opening_brackets_content))

                new_contents.append(contents[i])
                opening_brackets_idx = None
                opening_brackets_content = ''
                italic = False
        
        elif opening_brackets_idx is not None:
            opening_brackets_content += contents[i].text
            if contents[i].get('rend') == 'italic':
                italic = True
        
        else:
            new_contents.append(contents[i])

        contents.pop(0)
        

    if error:
        new_contents = old_contents
    
    return new_contents

def fix_displaced_punct(contents):
    for i in range(len(contents)):
        if not is_empty_string(contents[i].text) and contents[i].text.strip()[0] in r'!%),.:;?]|}' and i > 0 and len(contents[i].text.strip()) >= 2:
            if contents[i].text[0] == ' ':
                contents[i-1].text += ' ' + contents[i].text.strip()[0]
                contents[i].text = contents[i].text[2:]
            else:
                contents[i-1].text += contents[i].text.strip()[0]
                contents[i].text = contents[i].text[1:]
    return contents

