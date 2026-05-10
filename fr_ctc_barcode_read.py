#! /usr/bin/env python
# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# BSD Licence "revised"

import argparse
import sys
import json
from stdnum.fr.siren import validate as siren_validate

__author__ = "Alexis de Lattre <alexis.delattre@akretion.com>"
__date__ = "May 9th 2026"
__version__ = "0.1"


BARCODE_PREFIX = "FRCTC"
ALLOWED_BTs = {
    'BT-10': 'Buyer reference',
    'BT-11': 'Project reference',
    'BT-12': 'Contract reference',
    'BT-13': 'Purchase order reference',
    'BT-49': 'Buyer electronic address',
    }


def read_barcode(args):
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
    if not barcode_str.startswith(BARCODE_PREFIX):
        raise ValueError(f"Barcode must start with '{BARCODE_PREFIX}'")
    data_str = barcode_str[len(BARCODE_PREFIX):]
    try:
        raw_res = json.loads(data_str)
    except Exception as e:
        raise ValueError(f"Post-prefix barcode data {data_str} is not a valid json: {str(e)}")
    res = {}
    for key, value in raw_res.items():
        if key not in ALLOWED_BTs:
            key = f"BT-{key}"
        if key not in ALLOWED_BTs:
            raise ValueError(f"Skipping key {key} because it is not part of the allowed keys ({', '.join(ALLOWED_BTs)})")
        if not isinstance(value, str):
            raise ValueError(f'Skipping key {key} because its value ({value}) is not a string')
        val_stripped = value.strip()
        if not val_stripped:
            print(f'Skipping key {key} because its value ({value}) is empty')
            continue
        res[key] = val_stripped
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
    read_barcode(args)


def run():
    if __name__ == '__main__':
        main()


run()
