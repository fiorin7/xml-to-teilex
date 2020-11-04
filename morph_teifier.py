import node_factory as nf
from utils import SafeString
from debug import debug

def noun_xml(content0, content1):
    content0_split = content0.split(', ')
    form_lemma = nf.create_form_lemma_node(content0_split[0])
    pc = nf.create_pc_node(', ')
    form_inflected = nf.create_form_inflected_node(content0_split[1])
    gram_grp = nf.create_gram_grp(content1)

    return [form_lemma, pc, form_inflected, gram_grp]

def verb_xml(entry_type, content0, content1):
    result = []
    content0_split = content0.split(', ')
    form_lemma = nf.create_form_lemma_node(content0_split[0])
    result.append(form_lemma)

    if len(content0_split) > 1:
        for word in content0_split[1:]:
            pc = nf.create_pc_node(', ')
            form_inflected = nf.create_form_inflected_node(word)
            result.append(pc)
            result.append(form_inflected)
    
    if entry_type != 'special_verb':
        gram_grp = nf.create_gram_grp(content1, "iType")
        result.append(gram_grp)

    return result
    

def adj_1_2_decl_xml(content0, content1):
    form_lemma = nf.create_form_lemma_node(content0)
    gram_grp = nf.create_gram_grp(content1, "????")

    return [form_lemma, gram_grp]

def adj_multiple_forms_xml(content0):
    content0_split = content0.split(', ')
    result = []

    form_lemma = nf.create_form_lemma_node(content0_split[0])
    result.append(form_lemma)

    for word in content0_split[1:]:
        form_inflected = nf.create_form_inflected_node(word)
        pc = nf.create_pc_node(', ')
        result.append(pc)
        result.append(form_inflected)
    
    return result

def nom_and_gen_xml(content0, content1, content2, content3, content4):
    result = []
    tag_span = 0

    if content0.rstrip()[-1] == ',':
        form_lemma = nf.create_form_lemma_node(content0.rstrip()[:-1])
        usg_gen = nf.create_usg_node(content1)
        if content2.strip() == '-':
            form_inflected = nf.create_form_inflected_node('-' + content3)
            tag_span = 4
        else:
            form_inflected = nf.create_form_inflected_node(content2)
            tag_span = 3

    else:
        form_lemma = nf.create_form_lemma_node(content0)
        usg_gen = nf.create_usg_node(content2)
        if content3.strip() == '-':
            form_inflected = nf.create_form_inflected_node('-' + content4)
            tag_span = 5
        else:
            form_inflected = nf.create_form_inflected_node(content3)
            tag_span = 4
    
    pc = nf.create_pc_node(', ')

    result.extend([form_lemma, pc, *usg_gen, form_inflected])

    return result, tag_span


def adv_conjunct_xml(content0, content1):
    form_lemma = nf.create_form_lemma_node(content0)
    gram_grp = nf.create_gram_grp(content1, "????")
    return [form_lemma, gram_grp]




def get_morph_info(entry_type, contents):
    content0 = SafeString(contents[0].text)
    content1 = SafeString(contents[1].text)

    if len(contents) > 2:
        content2 = SafeString(contents[2].text)
    else:
        content2 = None
    
    if len(contents) > 3:
        content3 = SafeString(contents[3].text)
    else:
        content3 = None
    
    if len(contents) > 4:
        content4 = SafeString(contents[4].text)
    else:
        content4 = None

    res = None
    tag_span_of_morph_info = 0

    if entry_type == 'noun':
        res = noun_xml(content0, content1)
        tag_span_of_morph_info = 2

    elif entry_type in ('one_form_verb', 'multiple_form_verb', 'deponent_verb', 'special_verb'):
        res = verb_xml(entry_type, content0, content1)
        if entry_type == 'special_verb':
            tag_span_of_morph_info = 1
        else:
            tag_span_of_morph_info = 2

    elif entry_type == 'adj_1_2_decl':
        res = adj_1_2_decl_xml(content0, content1)
        tag_span_of_morph_info = 2

    elif entry_type in ('adj_like_acer_aequalis', 'adj_1_2_decl_three_forms_written_out'):
        res = adj_multiple_forms_xml(content0)
        tag_span_of_morph_info = 1
    
    elif entry_type == 'nom_and_gen':
        returned = nom_and_gen_xml(content0, content1, content2, content3, content4)
        res = returned[0]
        tag_span_of_morph_info = returned[1]
    
    elif entry_type in ('adv', 'conjunct'):
        res = adv_conjunct_xml(content0, content1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'praep':
        res = nf.create_praep_xml(content0, content1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'unknown but clear senses start':
        if debug():
            print(content0)
        pass
    
    elif entry_type == 'UNKNOWN':
        if debug():
            print(content0)
        pass

    return res, tag_span_of_morph_info
