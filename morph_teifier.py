import node_factory as nf
from utils import SafeString

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

def adv_conjunct_xml(content0, content1):
    form_lemma = nf.create_form_lemma_node(content0)
    gram_grp = nf.create_gram_grp(content1, "????")
    return [form_lemma, gram_grp]




def get_morph_info(entry_type, contents):
    content0 = SafeString(contents[0].text)
    content1 = SafeString(contents[1].text)

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
    
    elif entry_type in ('adv', 'conjunct'):
        res = adv_conjunct_xml(content0, content1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'praep':
        res = nf.create_praep_xml(content0, content1)
        tag_span_of_morph_info = 2
    
    elif entry_type == 'unknown but clear senses start':
        print(content0)
        pass
    
    elif entry_type == 'UNKNOWN':
        print(content0)
        pass

    return res, tag_span_of_morph_info
