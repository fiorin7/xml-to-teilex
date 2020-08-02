from copy import deepcopy
from lxml import etree as et
import re
from unidecode import unidecode
import string
import matcher as m
import teifier_for_morphological_part as morph
import rearranger_of_wrong_input_tags as rt
import teifier_for_senses as sns
import node_creator as nc

class Entry:
    def __init__(self, contents=[]):
        self.raw_contents = contents
        self.contents = contents
        self.title_lemma = self.get_title_lemma()
        self.fix_input_morph_tags_and_raplace_wrong_ones()
        self.entry_node = nc.create_entry_parent_node(self.title_lemma)
        self.entry_type =  self.get_entry_type()
        self.encoded_parts = {
            'morph_part' : self.set_morph_part_xml(),
            'senses' : []
        }
        self.raw_senses = self.append_senses()
        sns.encode_senses(self)
        
        
    def get_title_lemma(self):
        '''
        Return the "dictionary form" of the lemma e.g. ago, homo, ego.
        Words with both deponent and non-deponent forms like arbitro(r) accept as lemma the deponent one.
        '''
        his = [x for x in self.contents if x.tag == get_ns('hi')]
        first_line = re.split(', | ', his[0].text)
        lemma = unidecode(first_line[0])
        lemma_stripped = lemma.replace('-', '').replace('(', '').replace(')', '')
        return lemma_stripped
    
    def get_entry_type(self):
        match = m.match_morph_structure(self.contents)
        # if match != 'UNKNOWN':
        #     return match
        # else:
        #     self.fix_input_morph_tags_and_raplace_wrong_ones()
        #     return m.match_morph_structure(self.contents)
        return match
    
    def fix_input_morph_tags_and_raplace_wrong_ones(self):
        fixed_contents = rt.fix_wrong_tags_in_morph_part(self.contents)
        if fixed_contents:
            self.contents = fixed_contents
        self.contents = rt.fix_separated_brackets(self.contents)

    
    def merge_entry_parent_and_contents(self, entry_parent_node, contents):
        '''Insert original contents in the entry node.'''
        merged_entry = entry_parent_node
        [entry_parent_node.append(hi) for hi in self.contents]
        return merged_entry   

    def set_morph_part_xml(self):
        if self.title_lemma == 'adolescens':
            breakpoint
        morph_part, tag_span_of_morph_info = morph.get_morph_info(self.entry_type, self.contents)
        for _ in range(tag_span_of_morph_info):
            # print(et.tostring(self.contents[0], encoding='utf8', pretty_print=True).decode('utf8'))
            self.contents.remove(self.contents[0])

        return morph_part

    def insert_encoded_parts_in_entry(self):
        for part in self.encoded_parts.values():
            if part:
                if type(part) in (tuple, list):
                    [self.entry_node.append(x) for x in part]
                else:
                    self.entry_node.append(part)
    
    
    def append_senses(self, res = []):
        if self.entry_type != 'UNKNOWN' and self.encoded_parts.get('morph_part') and self.contents:
            res = [x for x in self.contents if x.text]
            self.contents = None
            return res
        else:
            return morph.deal_with_unknown_entry(self)


def get_ns(tag):
    '''Prefix tag with TEI namespace.'''
    return r'{http://www.tei-c.org/ns/1.0}' + tag

def remove_ref_parent(body):
    '''Remove ref parent tag (which contains hyperlink).'''
    for p in body:
        for idx in range(len(p)):
            x = p[idx]
            if x.tag == get_ns('ref'):
                children = x.getchildren()
                p.remove(x)
                for i in range(len(children)):
                    p.insert(i+idx, children[i])

def remove_style_attrib(body):
    '''Remove the style attribute with it's values (font size and font family).'''
    for p in body:
        for el in p:
            if 'style' in el.attrib.keys():
                el.attrib.pop('style')

def merge_elements_with_same_attribs(body):
    '''
    Merge two xml nodes (the tags with their attributes and content)
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
    '''Call all functions which do the initial manipulation of the input xml'''
    remove_ref_parent(body)
    remove_style_attrib(body)
    merge_elements_with_same_attribs(body)

def invalid_para(p):
    '''Dismiss the p's which contain the one letter title of a section like A, B etc.'''
    his = [hi for hi in p]
    return len(his) == 1 and len(his[0].text) == 1
    # needs more checks

def get_p_contents(p):
    '''Return the children of p of interest (in 'hi' tags).'''
    return [x for x in p if x.tag == get_ns('hi')]
    # what do with nested hi in ref

def get_new_tree(template):
    '''Return deepcopy of template to insert new entry in.'''
    return deepcopy(template)

def get_new_body(new_tree):
    '''Return variable with the "found" body of the template.'''
    new_root = new_tree.getroot()
    new_body = new_root.find(f'.//{get_ns("body")}')
    return new_body


parser = et.XMLParser(remove_blank_text=True)

template = et.parse('template.xml', parser)
tree = et.parse('example/raw_input.xml', parser)
root = tree.getroot()
body = root.find(f'.//{get_ns("body")}')
general_fix_up_input(body)


counter = 0
counter_unmatched = 0
for p in body.iter(f'{get_ns("p")}'):
    if invalid_para(p):
        continue
    
    counter += 1
    new_tree = get_new_tree(template)
    new_body = get_new_body(new_tree)
    contents = get_p_contents(p)
    entry = Entry(contents)
    entry.insert_encoded_parts_in_entry()
    
    new_body.append(entry.entry_node)
    
    new_tree.write(open(f'example/example-output/{entry.title_lemma}.xml', 'wb'), encoding='utf8', xml_declaration=True, pretty_print=True)
    # print(et.tostring(body, encoding='utf8', pretty_print=True).decode('utf8'))
    if entry.entry_type == 'UNKNOWN':
        counter_unmatched += 1
        print(f'{entry.contents[0].text}|{entry.contents[1].text}')
print(counter_unmatched)