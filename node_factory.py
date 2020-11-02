from lxml import etree as et
from utils import is_empty_string

# ############ RELATED #########################
def get_ns(tag):
    '''Prefix tag with TEI namespace.'''
    return r'{http://www.tei-c.org/ns/1.0}' + tag

# ################# MAIN #######################
def create_entry_parent_node(lemma):
    '''Create entry parent node with its attributes.'''
    entry_node = et.Element(get_ns("entry"))
    entry_node.set('sortKey', f"{lemma}")
    entry_node.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{lemma}")
    entry_node.set('{http://www.w3.org/XML/1998/namespace}lang', "la")
    return entry_node

# ############  INPUT STYLE NODES ################
def create_bold_hi_node(text):
    hi_node = et.Element(get_ns("hi"))
    hi_node.set('rend', 'bold')
    hi_node.text = text
    return hi_node

def create_normal_hi_node(text):
    hi_node = et.Element(get_ns("hi"))
    hi_node.text = text
    return hi_node

def create_italic_hi_node(text):
    hi_node = et.Element(get_ns("hi"))
    hi_node.set('rend', 'italic')
    hi_node.text = text
    return hi_node

# ############### MOSTLY MORPH ##################
def create_extra_morph(extra_morph):
    extra = et.Element(get_ns("extraMorph"))
    extra.text = extra_morph
    return extra

def create_form_lemma_node(text):
    form_lemma = et.Element(get_ns("form"))
    form_lemma.set('type', 'lemma')
    

    form_lemma.append(create_orth_node(text))
    return form_lemma

def create_orth_node(text):
    orth_node = et.Element(get_ns("orth"))
    orth_node.text = text
    return orth_node

def create_form_inflected_node(text):
    form_inflected = et.Element(get_ns("form"))
    form_inflected.set('type', 'inflected')
    form_inflected.text = text
    return form_inflected

def create_pc_node(text):
    pc = et.Element(get_ns("pc"))
    pc.text = text
    return pc

def create_gram_grp(text, gram_type="pos"):
    gram_prnt = et.Element(get_ns("gramGrp"))
    gram_chld = et.Element(get_ns("gram"))
    gram_chld.set('type', f'{gram_type}')
    gram_chld.text = text
    gram_prnt.append(gram_chld)
    return gram_prnt

def create_praep_xml(content0, content1):
    form_lemma = create_form_lemma_node(content0)
    gram_grp = create_gram_grp('praep.', "pos")
    colloc_node = et.Element(get_ns('gram'))
    colloc_node.set('type', 'colloc')
    colloc_node.text = content1.replace('praep.', '')
    gram_grp.append(colloc_node)
    return [form_lemma, gram_grp]


# ############### MOSTLY SENSE ##################

def create_sense_container_non_numbered(title_lemma):
    sense_container = et.Element(get_ns("sense"))
    sense_container.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{title_lemma}.1")
    return sense_container

def create_sense_container(title_lemma, sense_number=['1']):
    sense_container = et.Element(get_ns("sense"))
    xml_id_contents = title_lemma + '.' + ''.join(sense_number)
    sense_container.set('{http://www.w3.org/XML/1998/namespace}id', f"LBR.{xml_id_contents}")

    return sense_container

def create_label(label_content):
    label = et.Element(get_ns("lbl"))
    label.text = label_content
    return label

def create_usg_node(node_content):
    res = []
    pc_text = None

    if node_content.strip().endswith(':'):
        idx_pc = node_content.index(':')
        pc_text = node_content[idx_pc:]
        node_content = node_content[:idx_pc]

    usg_node = et.Element(get_ns("usg"))
    usg_node.set('type', '???')
    usg_node.text = node_content
    res.append(usg_node)

    if pc_text:
        pc_node = create_pc_node(pc_text)
        res.append(pc_node)
        
    return res

def create_def_node(node_content):
    result = []
    for i in range(len(node_content.split(', '))):
        x = node_content.split(', ')[i]
        for y in range(len([z for z in x.split('; ') if not is_empty_string(z)])):
            def_node = et.Element(get_ns("def"))
            def_node.set('{http://www.w3.org/XML/1998/namespace}lang', 'bg')
            def_node.text = x.split('; ')[y]
            result.append(def_node)
            if y < len(x.split('; '))-1:
                result.append(create_pc_node('; '))
        if i < len(node_content.split(', '))-1:
            result.append(create_pc_node(', '))
    return result

def assemble_cit_nodes(cit_type, quote_content):
    if cit_type == 'translation':
        cit_node = et.Element(get_ns("cit"))
        cit_node.set('type', 'translation')
        cit_node.set('{http://www.w3.org/XML/1998/namespace}lang', 'bg')

    elif cit_type == 'example':
        cit_node = et.Element(get_ns("cit"))
        cit_node.set('type', 'example')

    quote_node = et.Element(get_ns("quote"))
    quote_node.text = quote_content

    cit_node.append(quote_node)

    return cit_node