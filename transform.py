from copy import deepcopy
from lxml import etree as et
import re
from unidecode import unidecode

def get_ns(string):
    return r'{http://www.tei-c.org/ns/1.0}' + string

def remove_ref_parent(body):
    # this is for cases when one of the people working on the docx copied something
    # from an external source (like Perseus) and retained its hyperlink
    for p in body:
        for idx in range(len(p)):
            x = p[idx]
            if x.tag == get_ns('ref'):
                children = x.getchildren()
                p.remove(x)
                for i in range(len(children)):
                    p.insert(i+idx, children[i])

def remove_style_attrib(body):
    # this is for cases when one of the people working on the docx copied something
    # from an external source (like Perseus) and retained its original font size and family
    for p in body:
        for el in p:
            if 'style' in el.attrib.keys():
                el.attrib.pop('style')

def get_title_lemma(p):
    his = [x for x in p if x.tag == get_ns('hi')]
    first_line = re.split(', | ', his[0].text)
    lemma = unidecode(first_line[0])
    lemma_stripped = lemma.replace('-', '').replace('(', '').replace(')', '')
    # words with both deponent and non-deponent forms like arbitro(r) accept as lemma the deponent one
    return lemma_stripped

def invalid_para(p):
    his = [hi for hi in p]
    return len(his) == 1 and len(his[0].text) == 1
    # needs more checks

def get_p_contents(p):
    return [x for x in p if x.tag == get_ns('hi')]
    # what do with nested hi in ref

def get_new_tree(template):
    return deepcopy(template)

def get_new_body(new_tree):
    new_root = new_tree.getroot()
    new_body = new_root.find(f'.//{get_ns("body")}')
    return new_body

def get_entry(lemma):
    entry = et.Element("entry")
    entry.set('sortKey', f"{lemma}")
    entry.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{lemma}")
    entry.set('{http://www.w3.org/XML/1998/namespace}lang', "la")
    return entry


def merge_para_and_template(entry, contents):
    [entry.append(hi) for hi in contents]


parser = et.XMLParser(remove_blank_text=True)

template = et.parse('template.xml', parser)
tree = et.parse('example/raw_input.xml', parser)
root = tree.getroot()
body = root.find(f'.//{get_ns("body")}')
remove_ref_parent(body)
remove_style_attrib(body)



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



