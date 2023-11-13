from typing import Optional, List, Tuple

from common.codes_and_ids.constants import ALPHA_CODE_SEP, IRECO_TAG_SEP, IRECO_WORD_SEP
from common.codes_and_ids.subcodes import IRECOSubCode
from common.codes_and_ids.tags import ImageTag


def string_to_tag(string: str) -> Optional[ImageTag]:
    """Find a tag by its name"""
    for possible_tag in ImageTag:
        possible_tag: ImageTag
        if possible_tag.value == string:
            return possible_tag
    return None


def alpha_codes_to_cs_str(alpha_codes: List[str]) -> str:
    sep = f'{ALPHA_CODE_SEP} '
    return sep.join(alpha_codes)


def alpha_codes_to_list(alpha_codes: str) -> List[str]:
    codes = alpha_codes.split(ALPHA_CODE_SEP)
    return [c.strip() for c in codes]


def get_subcode_from_ireco_code(
        ireco_code: str
) -> Optional[IRECOSubCode]:
    code = ireco_code.split(IRECO_TAG_SEP)[0]
    subcode = code.split(IRECO_WORD_SEP)[-1]
    try:
        return IRECOSubCode(subcode)
    except ValueError:
        return None


def split_ireco_code_and_subcode(
        ireco_code: str
) -> Tuple[str, Optional[IRECOSubCode]]:
    ireco_code = ireco_code.split(IRECO_TAG_SEP)[0]
    ireco_code_parts = ireco_code.split(IRECO_WORD_SEP)
    try:
        ireco_subcode = IRECOSubCode(ireco_code_parts[-1])
        ireco_code_parts.pop(-1)
    except ValueError:
        ireco_subcode = None
    ireco_code = IRECO_WORD_SEP.join(ireco_code_parts)
    return ireco_code, ireco_subcode


def split_ireco_code_and_tags_as_str(
        ireco_code: str
) -> Tuple[str, Optional[str]]:
    parts = ireco_code.split(IRECO_TAG_SEP)
    if len(parts) == 1:
        return parts[0], None
    code = parts.pop(0)
    tags = IRECO_TAG_SEP.join(parts)
    return code, tags
