from lxml import etree as et

def get_form_lemma_node(text):
    form_lemma = et.Element("form")
    form_lemma.set('type', 'lemma')
    form_lemma.text = text
    return form_lemma

def get_form_inflected_node(text):
    form_inflected = et.Element("form")
    form_inflected.set('type', 'inflected')
    form_inflected.text = text
    return form_inflected

def get_pc_node(text):
    pc = et.Element("pc")
    pc.text = text
    return pc

def get_gram_grp(text, gram_type="pos"):
    gram_prnt = et.Element("gramGrp")
    gram_chld = et.Element("gram")
    gram_chld.set('type', f'{gram_type}')
    gram_chld.text = text
    gram_prnt.append(gram_chld)
    return gram_prnt


def noun_xml(contents0, contents1):
    contents0_split = contents0.split(', ')
    form_lemma = get_form_lemma_node(contents0_split[0])
    pc = get_pc_node(', ')
    form_inflected = get_form_inflected_node(contents0_split[1])
    gram_grp = get_gram_grp(contents1)

    return form_lemma, pc, form_inflected, gram_grp

def verb_xml(entry_type, contents0, contents1):
    result = []
    contents0_split = contents0.split(', ')
    form_lemma = get_form_lemma_node(contents0_split[0])
    result.append(form_lemma)

    if len(contents0_split) > 1:
        for word in contents0_split[1:]:
            pc = get_pc_node(', ')
            form_inflected = get_form_inflected_node(word)
            result.append(pc)
            result.append(form_inflected)
    
    if entry_type != 'special_verb':
        gram_grp = get_gram_grp(contents1, "iType")
        result.append(gram_grp)

    return result
    

def adj_1_2_decl_xml(contents0, contents1):
    form_lemma = get_form_lemma_node(contents0)
    pc = get_pc_node(', ')
    gram_grp = get_gram_grp(contents1, "????")

    return form_lemma, pc, gram_grp

def adj_multiple_forms_xml(contents0):
    contents0_split = contents0.split(', ')
    result = []

    form_lemma = get_form_lemma_node(contents0_split[0])
    result.append(form_lemma)

    for word in contents0_split[1:]:
        form_inflected = get_form_inflected_node(word)
        pc = get_pc_node(', ')
        result.append(pc)
        result.append(form_inflected)
    
    return result

def adv_praep_conjunct_xml(contents0, contents1):
    form_lemma = get_form_lemma_node(contents0)
    gram_grp = get_gram_grp(contents1, "????")
    return form_lemma, gram_grp


def get_morph_info(entry_type, contents):
    contents0 = contents[0].text
    contents1 = contents[1].text

    res = None
    tag_span_of_morph_info = 0

    if entry_type == 'noun':
        res = noun_xml(contents0, contents1)
        tag_span_of_morph_info = 2

    elif entry_type in ('one_form_verb', 'multiple_form_verb', 'deponent_verb', 'special_verb'):
        res = verb_xml(entry_type, contents0, contents1)
        if entry_type == 'special_verb':
            tag_span_of_morph_info = 1

    elif entry_type == 'adj_1_2_decl':
        res = adj_1_2_decl_xml(contents0, contents1)
        tag_span_of_morph_info = 2

    elif entry_type in ('adj_like_acer_aequalis', 'adj_1_2_decl_three_forms_written_out'):
        res = adj_multiple_forms_xml(contents0)
        tag_span_of_morph_info = 1
    
    elif entry_type in ('adv', 'praep', 'conjunct'):
        res = adv_praep_conjunct_xml(contents0, contents1)
        tag_span_of_morph_info = 2

    return res, tag_span_of_morph_info
