from copy import deepcopy
from lxml import etree as et
import re
from unidecode import unidecode
import string
import matcher as m

def get_ns(tag):
    '''Prefixes tag with TEI namespace.'''
    return r'{http://www.tei-c.org/ns/1.0}' + tag

def remove_ref_parent(body):
    '''Removes ref parent tag (which contains hyperlink).'''
    for p in body:
        for idx in range(len(p)):
            x = p[idx]
            if x.tag == get_ns('ref'):
                children = x.getchildren()
                p.remove(x)
                for i in range(len(children)):
                    p.insert(i+idx, children[i])

def remove_style_attrib(body):
    '''Removes the style attribute with it's values (font size and font family).'''
    for p in body:
        for el in p:
            if 'style' in el.attrib.keys():
                el.attrib.pop('style')

def merge_elements_with_same_attribs(body):
    '''
    Merges two xml nodes (the tags with their attributes and content)
    if the have matching attributes and values.
    xml:space attribute isn't taken into account during the comparison and is retained after the merging
    '''
    for p in body:
        for idx in range(len(p)-1,-1,-1):
            curr_node = p[idx]
            if idx == len(p)-1:
                old_node = curr_node
                continue
            if curr_node.get('rend') == old_node.get('rend'):
                if curr_node.text[-1] != ' ' and old_node.text[0] not in string.punctuation:
                    curr_node.text += ' '
                curr_node.text += old_node.text
                if old_node.get('{http://www.w3.org/XML/1998/namespace}space') == 'preserve':
                    curr_node.attrib['{http://www.w3.org/XML/1998/namespace}space'] = 'preserve'
                p[idx] = curr_node
                p.remove(old_node)
            old_node = curr_node

def general_fix_up_input(body):
    '''This function calls all functions which do the initial manipulation of the input xml'''
    remove_ref_parent(body)
    remove_style_attrib(body)
    merge_elements_with_same_attribs(body)


def get_title_lemma(p):
    '''
    Returns the "dictionary form" of the lemma e.g. ago, homo, ego.
    Words with both deponent and non-deponent forms like arbitro(r) accept as lemma the deponent one.
    '''
    his = [x for x in p if x.tag == get_ns('hi')]
    first_line = re.split(', | ', his[0].text)
    lemma = unidecode(first_line[0])
    lemma_stripped = lemma.replace('-', '').replace('(', '').replace(')', '')
    return lemma_stripped

def invalid_para(p):
    '''Dismisses the p's which contain the one letter title of a section like A, B etc.'''
    his = [hi for hi in p]
    return len(his) == 1 and len(his[0].text) == 1
    # needs more checks

def get_p_contents(p):
    '''Returns the children of p of interest (in 'hi' tags).'''
    return [x for x in p if x.tag == get_ns('hi')]
    # what do with nested hi in ref

def get_new_tree(template):
    '''Returns deepcopy of template to insert new entry in.'''
    return deepcopy(template)

def get_new_body(new_tree):
    '''Returns variable with the "found" body of the template.'''
    new_root = new_tree.getroot()
    new_body = new_root.find(f'.//{get_ns("body")}')
    return new_body

def get_entry(lemma):
    '''Creates entry parent node with its attributes.'''
    entry = et.Element("entry")
    entry.set('sortKey', f"{lemma}")
    entry.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{lemma}")
    entry.set('{http://www.w3.org/XML/1998/namespace}lang', "la")
    return entry


def merge_para_and_template(entry, contents):
    '''Inserts entry in the template.'''
    [entry.append(hi) for hi in contents]


parser = et.XMLParser(remove_blank_text=True)

template = et.parse('template.xml', parser)
tree = et.parse('example/raw_input.xml', parser)
root = tree.getroot()
body = root.find(f'.//{get_ns("body")}')
general_fix_up_input(body)



counter = 0

for p in body.iter(f'{get_ns("p")}'):
    if invalid_para(p):
        continue
    
    counter += 1
    new_tree = get_new_tree(template)
    new_body = get_new_body(new_tree)
    title_lemma = get_title_lemma(p)
    
    entry = get_entry(title_lemma)
    new_body.append(entry)
    contents = get_p_contents(p)

    merge_para_and_template(entry, contents)


    new_tree.write(open(f'example/example-output/{title_lemma}.xml', 'wb'), encoding='utf8', xml_declaration=True, pretty_print=True)
    # print(et.tostring(body, encoding='utf8', pretty_print=True).decode('utf8'))



