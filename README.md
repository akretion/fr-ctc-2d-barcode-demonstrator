# Proposal for 2D barcode for France's CTC

During the [JFE 2026](https://jfe.fnfe-mpe.org/) event on May 5-6th 2026, one of the main talks mentionned the idea of a 2D barcode to transmit the company's e-invoicing address to the cashier, but this was just an idea and there was no spec available for it. France's CTC reform is starting on September 1st 2026, so we should move forward rapidly on this. Here is a proposal to normalize a 2D barcode to easily transmit the e-invoicing address from the customer to the cashier, as well as a few other parameters that could be useful for the customer company that will receive the invoice.

## Data in 2D barcode

| EN16931 field            | EN16931 code | Required?   |
|:-------------------------|:-------------|:------------|
| Buyer electronic address | BT-49        | Required    |
| Buyer reference          | BT-10        | Optional    |
| Project reference        | BT-11        | Optional    |
| Contract reference       | BT-12        | Optional    |
| Purchase order reference | BT-13        | Optional    |

## Data encoding

Data encoding would be the same as the [2D barcode to connect to a WiFi network](https://github.com/zxing/zxing/wiki/Barcode-Contents#wi-fi-network-config-android-ios-11). The prefix would be **FRCTCINVOICEME** which stands for *FRance CTC INVOICE-ME* (*CTC* means *Continuous Transaction Controls*, which is a common name for e-invoicing reforms).

Exemple of 2D barcode content:

~~~~
FRCTCINVOICEME:BT-49:820123354_FRAIS;BT-11:JFE2026
~~~~

means:
* my electronic address (i.e. the identifier of my [directory](https://facturation.chorus-pro.gouv.fr/) line) is **820123354_FRAIS** (in this exemple : my SIREN is *820123354* and my suffix is *FRAIS*)
* project reference is **JFE2026**

Encoding rules:

* Order of fields doesn't matter
* Prefix **FRCTCINVOICEME** is followed by <mark> : </mark> (colon)
* Delimiter between fields is <mark> ; </mark> (semi-colon)
* Delimiter between field code and field value is <mark> : </mark> (colon)
* Special characters <mark> \ </mark>, <mark> ; </mark>, <mark> , </mark>, <mark> " </mark> and <mark> : </mark> must be escaped with a backslash (<mark> \ </mark>) as in MECARD encoding.

## Sample python code

This GitHub project provides 2 scripts:

* <mark>fr\_ctc\_barcode\_generate.py</mark> to generate a 2D barcode
* <mark>fr\_ctc\_barcode\_read.py</mark> to parse the string outputed by the barcode reader

To install the required dependencies, run:

~~~~
pip install -r requirements.txt
~~~~

To run the test suite, run:

~~~~
python -m unittest tests.py
~~~~

## Comments and change proposals

You can open an issue on this GitHub project to give your opinon on this proposal and propose changes.

## Motivations for technical choices

To make this proposal, I used my experience implementing different barcode and text-based protocols such as [GS1 barcodes](https://ref.gs1.org/standards/genspecs/), the [protocol between payment terminal and cashier software of the Association du Paiement](https://associationdupaiement.fr/protocoles/protocole-caisse/).

The main topic is how to separate the different blocks of data when the values have a variable length. GS1 barcode uses the [FNC1 character](https://www.gs1uk.org/knowledge-hub/barcodes/what-is-the-function-1-character), which is a barcode-only character which doesn't exist in the Unicode table ; at first, it seems a good idea to use a character that cannot be used in the data values, but it just moves the technical problem downstream to the text representation of the barcode outputed by the barcode reader, where the user must configure the text representation of FNC1 and this configuration process is different from a barcode manufacturer to another. In real-life, it's a big pain because the barcode reader need to have a specific configuration, which causes many problems when the barcode reader needs to be replaced.

Other protocols like the protocol between payment terminal and cashier software of the Association du Paiement, the length of each value is given before the value itself and field identifiers have a fixed-length. It is easy to implement in code, but the string is difficult to read for a human, which makes debugging less easy. And EN16931 field codes (<mark>BT-1</mark>, <mark>BT-10</mark>, <mark>BT-112</mark>) don't have a fixed length.

Another possibilité is to build a JSON such as <mark>{'BT-49': '820123354\_FRAIS', 'BT-11': 'JFE2026'}</mark> and then convert this JSON to a string with json.dumps(). The reading the barcode, a simple call to json.loads() will give back the data as a dictionnary. From a technical and software development point of view, this solution is perfect: the code to generate and parse the barcode is very simple. Only drawback: it is a bit more verbose than the proposed implementation i.e. it uses more characters.

The implementation proposed here has the following advantages:
* very easy to read by a human, which makes the standard very easy to understand and easy to debug
* no special configuration on barcode scanners
* already used for WiFi barcode: we don't re-invent the wheel!

Main drawback: parsing the string outputed by the 2D barcode scanner is a bit more complex than it seems because of the escaping mecanism. We will have to insist on the escaping mecanism, so that the implementation in cashier software handle it properly. Providing sample test barcodes that contain escaped characters would be a way to invite cashier software to implement it properly.

## Left to decide to finalize the standard

* Format of the 2D barcode: [QR Code](https://en.wikipedia.org/wiki/QR_code), [Datamatrix](https://en.wikipedia.org/wiki/Data_Matrix), [Aztec](https://en.wikipedia.org/wiki/Aztec_Code), ...
* Exact list of the optional EN16931 fields
* Prefix **FRCTCINVOICEME**
