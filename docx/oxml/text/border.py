from ..xmlchemy import (
    BaseOxmlElement, OneOrMore, OptionalAttribute, RequiredAttribute,
    ZeroOrOne
)
from docx.oxml.simpletypes import (ST_BorderValue, ST_EighthsOfPointMeasure, ST_PtsMeasure,
                                   ST_HexColor, XsdBoolean)

class CT_BorderSide(BaseOxmlElement):
    """
    Class representing children of ``<w:pBdr>`` elements.
    """
    val = RequiredAttribute("w:val",ST_BorderValue)
    sz = RequiredAttribute("w:sz",ST_EighthsOfPointMeasure)
    space = RequiredAttribute("w:space",ST_PtsMeasure)
    color = RequiredAttribute("w:color",ST_HexColor)
    shadow = OptionalAttribute("w:shadow",XsdBoolean)
    

class CT_PBdr(BaseOxmlElement):
    """ 
    ``<w:pBdr>`` element, containing paragraph border information.
    """
    _tag_seq = ('w:top', 'w:left', 'w:bottom', 'w:right')
    top = ZeroOrOne('w:top', successors=_tag_seq[1:])
    left = ZeroOrOne('w:left', successors=_tag_seq[2:])
    bottom = ZeroOrOne('w:bottom', successors=_tag_seq[3:])
    right = ZeroOrOne('w:right', successors=_tag_seq[4:])
    del _tag_seq
    
