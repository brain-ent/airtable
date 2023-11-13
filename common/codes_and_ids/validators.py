import logging
import os
import re
from dataclasses import dataclass
from typing import List

from common.codes_and_ids.constants import IRECO_TAG_SEP, IRECO_WORD_SEP, MAX_IRECO_PARTS, IRECO_PART_MIN_LEN, IRECO_PART_MAX_LEN, \
    MIN_IRECO_PARTS, ALPHA_CODE_MIN_LEN, ALPHA_CODE_MAX_LEN, ALPHA_CODE_SEP, DIR_NAME_SEP
from common.codes_and_ids.tags import ImageTag
from common.codes_and_ids.utils import get_subcode_from_ireco_code


@dataclass
class CodeStatus:
    valid: bool
    info: str


def check_ireco_code(ireco_code: str) -> CodeStatus:
    """
    Checks alphabetic IRECO code
    E.g. MELLON.NICE.SLICED
    Note: It does not check tags like
          MELLON.NICE.SLICED#PACKAGE
    """
    if IRECO_TAG_SEP in ireco_code:
        return CodeStatus(
            valid=False,
            info='Do not use tags/package types in IDs'
        )
    for space in (' ', '\t', '\n', '\r'):
        if space in ireco_code:
            return CodeStatus(
                valid=False,
                info='You cannot use spaces in ID'
            )
    parts = ireco_code.split(IRECO_WORD_SEP)
    if not parts[0].isalpha():
        return CodeStatus(
            valid=False,
            info=f'The first word must be alphabetic only, '
                 f'not `{parts[0]}`'
        )
    if len(parts) < MIN_IRECO_PARTS:
        return CodeStatus(
            valid=False,
            info=f'Too few words. '
                 f'Please use at least {MIN_IRECO_PARTS}'
        )
    if len(parts) > MAX_IRECO_PARTS:
        return CodeStatus(
            valid=False,
            info=f'Too many words. '
                 f'Please use no more than {MAX_IRECO_PARTS}'
        )
    for word in parts:
        if not (word.isupper() or word.isdigit()):
            return CodeStatus(
                valid=False,
                info=f'Each part must be ALPHABETIC or digits, '
                     f'not `{word}`'
            )
        if len(word) < IRECO_PART_MIN_LEN:
            return CodeStatus(
                valid=False,
                info=f'Part `{word}` is too short. '
                     f'Use at least {IRECO_PART_MIN_LEN} chars.'
            )
        if len(word) > IRECO_PART_MAX_LEN:
            return CodeStatus(
                valid=False,
                info=f'Part `{word}` is too long. '
                     f'Use no more than {IRECO_PART_MAX_LEN} chars.'
            )
    return CodeStatus(
        valid=True,
        info='Ok'
    )


def check_ireco_code_and_tags(ireco_code_and_tags: str) -> CodeStatus:
    parts = ireco_code_and_tags.split(IRECO_TAG_SEP)
    ireco_code = parts.pop(0)
    ireco_code_status = check_ireco_code(ireco_code)
    if not ireco_code_status.valid:
        return ireco_code_status
    for tag in parts:
        try:
            ImageTag(tag)
        except ValueError:
            return CodeStatus(
                valid=False,
                info=f'Invalid tag: `{tag}`'
            )
    return CodeStatus(
        valid=True,
        info='Ok'
    )


def check_alpha_code(alpha_code: str) -> CodeStatus:
    """
    Check Alpha code
    (internal store's code)
    E.g.: 5300, 8560,
    """
    if not alpha_code.isdigit():
        return CodeStatus(
            valid=False,
            info=f'Alpha code must be a number, '
                 f'not `{alpha_code}`'
        )
    if len(alpha_code) < ALPHA_CODE_MIN_LEN or \
            len(alpha_code) > ALPHA_CODE_MAX_LEN:
        return CodeStatus(
            valid=False,
            info=f'Alpha code length must be '
                 f'{ALPHA_CODE_MIN_LEN} - {ALPHA_CODE_MAX_LEN}'
        )
    return CodeStatus(
        valid=True,
        info='Ok'
    )


def check_cs_alpha_codes(alpha_codes: str) -> CodeStatus:
    """
    Check multiple Alpha codes separated with ALPHA_CODE_SEP
    """
    # cs - Comma Separated
    codes = alpha_codes.split(ALPHA_CODE_SEP)
    codes = [c.strip() for c in codes]
    for c in codes:
        status = check_alpha_code(c)
        if not status.valid:
            return status
    return CodeStatus(
        valid=True,
        info='Ok'
    )


def is_class_dir(dir_path: str) -> bool:
    # MELON.HONEYDEW.SLICED#NET_2022.10.28_20.45.31.477652
    r = r'^[A-Z0-9.#]*_\d{4}\.\d{2}\.\d{2}_\d{2}\.\d{2}\.\d{2}\.\d{1,6}'
    if not (
            os.path.isdir(dir_path)
            or os.path.isdir(os.path.realpath(dir_path))
    ):
        logging.debug(
            f'It is not a directory or a link to a directory: {dir_path}'
        )
        return False
    dir_name: str = os.path.basename(dir_path)
    dir_name = dir_name.replace(
        # Allow double DIR_NAME_SEP for more readability
        f'{DIR_NAME_SEP}{DIR_NAME_SEP}',f'{DIR_NAME_SEP}'
    )
    if not re.match(r, dir_name):
        logging.debug(f'{dir_name} does not match re')
        return False
    dir_name_parts = dir_name.split(DIR_NAME_SEP)
    code_status = check_ireco_code_and_tags(dir_name_parts[0])
    if not code_status.valid:
        logging.debug(
            f'Bad IRECO code: {dir_path}. '
            f'{code_status.info}'
        )
    return code_status.valid
