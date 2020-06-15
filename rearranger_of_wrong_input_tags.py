from lxml import etree as et

def make_bold_hi_node(text):
    hi_node = et.Element("hi")
    hi_node.set('rend', 'bold')
    hi_node.text = text
    return hi_node

def make_normal_hi_node(text):
    hi_node = et.Element("hi")
    hi_node.text = text
    return hi_node

def number_one_is_in_c0(content0):
    return content0.strip()[-2:] == '1.'

def gram_number_is_in_c1(content0, content1):
    first_word_stripped = content0.split(', ')[0].strip()
    is_verb = first_word_stripped[-1] == 'o' or first_word_stripped[-2:] == 'or' or first_word_stripped[-4:] == 'o(r)'
    is_adj = len(content0.split(', ')) == 1 and content0.strip()[-2:] == 'us'
    return  (is_verb or is_adj) and content1.strip()[0].isdigit() and content1.strip()[1] != '.'


def fix_wrong_tags_in_morph_part(contents):
    content0_node = contents[0]
    content1_node = contents[1]
    content0 = contents[0].text
    content1 = contents[1].text

    result = []

    if number_one_is_in_c0(content0):
        content0_node.text = content0_node.text.rstrip()[:-2]
        content0_2_node = make_bold_hi_node('1.')
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
        if content1[0] == ' ':
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
    
