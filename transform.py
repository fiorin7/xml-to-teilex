from copy import deepcopy
from lxml import etree as et

def get_ns(string):
    return r'{http://www.tei-c.org/ns/1.0}' + string

def get_title_lemma(tree):
    pass

def invalid_para(p):
    his = [hi for hi in p]
    return len(his) == 1 and len(his[0].text) == 1

def merge_para_and_template(template, p):
    new_tree = deepcopy(template)
    new_root = new_tree.getroot()
    new_body = new_root.find(f'.//{get_ns("body")}')
    new_body.append(p)
    return new_tree

parser = et.XMLParser(remove_blank_text=True)

template = et.parse('template.xml', parser)
tree = et.parse('example/raw_input.xml', parser)
root = tree.getroot()
body = root.find(f'.//{get_ns("body")}')



counter = 0

for p in body.iter(f'{get_ns("p")}'):
    if invalid_para(p):
        continue
    
    counter += 1
    
    new_tree = merge_para_and_template(template, p)

    new_tree.write(open(f'example/example-output/{counter}.xml', 'wb'), encoding='utf8', xml_declaration=True, pretty_print=True)
    # print(et.tostring(body, encoding='utf8', pretty_print=True).decode('utf8'))



