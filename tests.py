# Copyright 2026 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# BSD Licence "revised"
# To run the tests:
# python -m unittest tests.py

import unittest
from fr_ctc_barcode_read import parse_barcode
from fr_ctc_barcode_generate import prepare_barcode_str


class TestBarcode(unittest.TestCase):

    def test_simple_generate(self):
        easy_data_dict = {
            'BT-49': '448819680',
            'BT-11': 'JFE2026',
            }
        barcode_str = "FRCTCINVOICEME:BT-49:448819680;BT-11:JFE2026"
        self.assertEqual(prepare_barcode_str(easy_data_dict), barcode_str)

    def test_generate_no_empty_value(self):
        data_dict = {
            'BT-49': '448819680',
            'BT-11': ' JFE2026  ',
            'BT-12': ' ',
            'BT-13': None,
            'BT-99': 'UnallowedBT',
            }
        barcode_str = "FRCTCINVOICEME:BT-49:448819680;BT-11:JFE2026"
        self.assertEqual(prepare_barcode_str(data_dict), barcode_str)

    def test_refuse_gen(self):
        data_dicts = [
            {'BT-49': '448819681', 'BT-11': 'JFE2026'},  # invalid SIREN
            {'BT-11': 'JFE2026'},  # missing BT-49
            {'BT-49': ' ', 'BT-11': 'JFE2026'},  # empty BT-49
            {'BT-49': None, 'BT-11': 'JFE2026'},  # BT-49 is None
            ]
        for data_dict in data_dicts:
            with self.assertRaises(ValueError):
                prepare_barcode_str(data_dict)

    def test_simple_read(self):
        res = {
            'BT-49': '792377731',
            'BT-12': 'AK1242',
            'BT-13': 'PO42',
            }
        barcode_str = "FRCTCINVOICEME:BT-49:792377731;BT-12:AK1242;BT-13:PO42"
        self.assertEqual(parse_barcode(barcode_str), res)
        barcode_str += ';'
        self.assertEqual(parse_barcode(barcode_str), res)

    def test_empty_read(self):
        res = {
            'BT-49': '792377731',
            'BT-13': 'PO42',
            }
        barcode_str = "FRCTCINVOICEME:BT-49:792377731;BT-12:;BT-13:PO42"
        self.assertEqual(parse_barcode(barcode_str), res)

    def test_read_invalid_barcodes(self):
        invalid_barcodes = [
            "FRCTCINVOICEME:BT-12:AK1242;BT-13:PO42",  # missing BT-49
            "FRCTCINVOICEME:BT-49: ;BT-12:AK1242;BT-12:PO42",  # empty BT-49
            "RCTCINVOICEME:BT-49:792377731;BT-12:AK1242;BT-13:PO42",  # bad prefix
            "FRCTCINVOICEME::BT-49:792377731;BT-12:AK1242;BT-13:PO42",  # bad prefix
            "FRCTCINVOICEME:BT-49:792377731;BT-42:AK1242;BT-13:PO42",  # BT-42 unallowed
            "FRCTCINVOICEME:BT-49:792377731;BT-12:AK1242;BT-12:PO42",  # BT-12 present twice
            "FRCTCINVOICEME:",  # empty
            ]
        for invalid_barcode in invalid_barcodes:
            with self.assertRaises(ValueError):
                parse_barcode(invalid_barcode)

    def test_escape_and_unicode(self):
        in_res = {
            'BT-49': '792377731_FRAIS',
            'BT-10': 'POU"E"T',
            'BT-11': '''ET:NON;'Oui';Yes;''',
            'BT-12': 'escape\\me\\aussi\\\\',
            'BT-13': 'le\\pire ,é😄mè:',
            }
        barcode_str = prepare_barcode_str(in_res)
        out_res = parse_barcode(barcode_str)
        self.assertEqual(in_res, out_res)


if __name__ == '__main__':
    unittest.main()
