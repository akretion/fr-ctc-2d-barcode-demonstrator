#! /usr/bin/env python
# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# BSD Licence "revised"

import argparse
import sys
from stdnum.fr.siren import validate as siren_validate

__author__ = "Alexis de Lattre <alexis.delattre@akretion.com>"
__date__ = "May 9th 2026"
__version__ = "0.1"


BARCODE_PREFIX = "FRCTCINVOICEME"
TO_ESCAPE_CHARS = ["\\", ":", ";", ",", '"']
ESCAPE_CHAR = "\\"
BLOCK_SEP_CHAR = ";"
KEY_VALUE_SEP_CHAR = ":"
PREFIX_SEP_CHAR = ":"
ALLOWED_BTs = {
    'BT-10': 'Buyer reference',
    'BT-11': 'Project reference',
    'BT-12': 'Contract reference',
    'BT-13': 'Purchase order reference',
    'BT-49': 'Buyer electronic address',
    }


def gen_barcode(args):
    barcode_str = args.barcode_str and args.barcode_str[0]
    if not barcode_str:
        barcode_str = input("Enter barcode string: ")
    barcode_str = barcode_str.strip()
    if not barcode_str:
        print("You must enter a barcode string. Exiting.")
        sys.exit(1)
    print(f"Barcode string: {barcode_str}")
    res = parse_barcode(barcode_str)
    print('This barcode string is valid. Result:')
    for bt, value in res.items():
        print(f"{ALLOWED_BTs[bt]} ({bt}): {value}")
    siren = res['BT-49'][:9]
    try:
        siren_validate(siren)
    except Exception as e:
        print(f"WARNING: Buyer electronic address (BT-49) doesn't start with a valid SIREN ({siren}). Error: {str(e)}")


def parse_barcode(barcode_str):
    prefix = f"{BARCODE_PREFIX}{PREFIX_SEP_CHAR}"
    if not barcode_str.startswith(prefix):
        raise ValueError(f"Barcode must start with '{prefix}'")
    data_str = barcode_str[len(prefix):]
    res = {}
    while data_str:
        block_match = False
        for bt in ALLOWED_BTs.keys():
            bt_sep = f"{bt}{KEY_VALUE_SEP_CHAR}"
            if data_str.startswith(bt_sep):
                block_match = True
                if bt in res:
                    raise ValueError(f"{bt} is present twice!")
                data_str = data_str[len(bt_sep):]
                # now we read value
                value = ''
                next_is_escaped = False
                for char in list(data_str):
                    if char == BLOCK_SEP_CHAR and not next_is_escaped:
                        data_str = data_str[1:]
                        break
                    if char == ESCAPE_CHAR and not next_is_escaped:
                        next_is_escaped = True
                    else:
                        next_is_escaped = False
                        value += char
                    data_str = data_str[1:]
                if not value:
                    print(f"WARNING: {bt} has no value. Ignored.")
                    break
                res[bt] = value
                break
        if not block_match:
            raise ValueError(f"Remaining string '{data_str}' doesn't start with an allowed BT ({', '.join(ALLOWED_BTs.keys())})")
    if "BT-49" not in res:
        raise ValueError("BT-49 is not present, although it is required.")
    return res


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    usage = "fr_ctc_barcode_read.py <barcode_string>"
    epilog = f"Author: {__author__} - Version: {__version__}"
    description = "Parse the string outputed by the barcode reader when reading a 2D barcode for France CTC."
    parser = argparse.ArgumentParser(
        usage=usage, epilog=epilog, description=description)
    parser.add_argument(
        "barcode_str", nargs='*',
        help="String corresponding to the output of the 2D barcode reader.")
    args = parser.parse_args()
    gen_barcode(args)


def run():
    if __name__ == '__main__':
        main()


run()
