#! /usr/bin/env python
# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# BSD Licence "revised"

import argparse
import segno
import os
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
    output_file = args.barcode_file and args.barcode_file[0]
    if not output_file:
        output_file = input("Enter barcode output file: ")
        output_file = output_file.strip()
    if not output_file:
        print("You must enter a barcode output file. Exiting.")
        sys.exit(1)
    if not args.overwrite and os.path.exists(output_file):
        print(f"File {output_file} already exists. Use option --overwrite if you want to overwrite it. Exiting.")
        sys.exit(1)
    bt49 = args.bt49
    if not args.bt49:
        bt49 = input("Enter the buyer electronic address (BT-49): ")
        bt49 = bt49.strip()
    if not bt49:
        print("Buyer electronic address is required. Exiting.")
        sys.exit(1)
    data_dict = {'BT-49': bt49}
    if args.bt10:
        data_dict['BT-10'] = args.bt10
    if args.bt11:
        data_dict['BT-11'] = args.bt11
    if args.bt12:
        data_dict['BT-12'] = args.bt12
    if args.bt13:
        data_dict['BT-13'] = args.bt13
    scale_str = args.scale
    try:
        scale = int(scale_str)
    except Exception:
        print("Argument --scale (or -s) must be an integer. Exiting.")
        sys.exit(1)
    if scale <= 0:
        print("Argument --scale (or -s) must be a positive integer. Exiting.")
        sys.exit(1)
    barcode_str = prepare_barcode_str(data_dict)
    print(f"Barcode string: {barcode_str}")
    qrcode = segno.make_qr(barcode_str)
    qrcode.save(output_file, scale=scale)
    print(f'Barcode file {output_file} successfully generated')


def prepare_barcode_str(data_dict):
    data_dict_stripped = {key: val.strip() for key, val in data_dict.items() if val and val.strip() and isinstance(val, str) and key in ALLOWED_BTs}
    for key, value in data_dict_stripped.items():
        print(f"{ALLOWED_BTs[key]} ({key}): {value}")
    if 'BT-49' not in data_dict_stripped:
        raise ValueError('Missing BT-49')
    bt49 = data_dict_stripped['BT-49']
    siren = bt49[:9]
    try:
        siren_validate(siren)
    except Exception as e:
        raise ValueError(f"For France's CTC, the buyer electronic address starts with the SIREN of the company (9 digits). But the 9 first caracters of the buyer electronic address ({siren}) is not a valid SIREN: {str(e)}")
    data_dict_escaped = {key: mecard_format(val.strip()) for key, val in data_dict_stripped.items()}
    barcode_end = BLOCK_SEP_CHAR.join([f"{key}{KEY_VALUE_SEP_CHAR}{val_esc}" for key, val_esc in data_dict_escaped.items()])
    barcode_str = f"{BARCODE_PREFIX}{PREFIX_SEP_CHAR}{barcode_end}"
    return barcode_str


def mecard_format(value):
    for char in TO_ESCAPE_CHARS:
        value = value.replace(char, ESCAPE_CHAR + char)
    return value


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    usage = "fr_ctc_barcode_generate.py <barcode_filename>"
    epilog = f"Author: {__author__} - Version: {__version__}"
    description = "Generate 2D barcode for France's CTC."
    parser = argparse.ArgumentParser(
        usage=usage, epilog=epilog, description=description)
    parser.add_argument(
        '-b', '--bt10', dest="bt10", help="Buyer reference (BT10).")
    parser.add_argument(
        '-p', '--bt11', dest="bt11", help="Project reference (BT11).")
    parser.add_argument(
        '-c', '--bt12', dest="bt12", help="Contract reference (BT12).")
    parser.add_argument(
        '-po', '--bt13', dest="bt13", help="Purchase order reference (BT13).")
    parser.add_argument(
        '-d', '--bt49', dest="bt49", help="Buyer electronic address (BT49). Required.")
    parser.add_argument(
        '-s', '--scale', dest="scale", default=5,
        help="Scale of the barcode. Must be a positive integer. Default value: 5.")
    parser.add_argument(
        '-w', '--overwrite', dest="overwrite", action='store_true',
        help="Overwrite output barcode file if it already exists.")
    parser.add_argument(
        "barcode_file", nargs='*',
        help="Output barcode filename. It must have a valid extension: .png, .svg, .pdf or .eps.")
    args = parser.parse_args()
    gen_barcode(args)


def run():
    if __name__ == '__main__':
        main()


run()
