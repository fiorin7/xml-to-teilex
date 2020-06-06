from copy import deepcopy
from lxml import etree as et

parser = et.XMLParser(remove_blank_text=True)

template = et.parse('template.xml', parser)
tree = et.parse('example/raw_input.xml', parser)
root = tree.getroot()


def get_ns(string):
    return r'{http://www.tei-c.org/ns/1.0}' + string

counter = 0
for p in root.iter(f'{get_ns("p")}'):
    counter += 1
    new_tree = deepcopy(template)
    new_root = new_tree.getroot()
    body = new_root.find(f'.//{get_ns("body")}')
    body.append(p)

    new_tree.write(open(f'example/example-output/{counter}.xml', 'wb'), encoding='utf8', xml_declaration=True, pretty_print=True)
    # print(et.tostring(body, encoding='utf8', pretty_print=True).decode('utf8'))


# tree.write(open('example/example-output.xml', 'wb'), encoding='utf8')

# print([elem.tag for elem in root.iter()])
# print(ET.tostring(root, encoding='utf8').decode('utf8'))