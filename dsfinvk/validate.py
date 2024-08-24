import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from io import StringIO


class ValidationException(Exception):
    pass


def validate_files(filemap):
    errors = []
    if 'index.xml' not in filemap:
        errors.append('No index.xml found')
        return errors

    tree = ET.parse(filemap['index.xml'])
    root = tree.getroot()

    if root.find("./Version").text != '1.0':
        errors.append('index.xml version is not 1.0')
        return errors

    for media in root.findall("./Media"):
        for table in media.findall("./Table"):
            url = table.find("./URL").text

            if url not in filemap:
                errors.append('File "{}" not found.'.format(url))
                continue

            if not table.findall("./UTF8"):
                errors.append('{}: Validator does only support UTF8.'.format(url))
                continue

            try:
                if hasattr(filemap[url], 'read'):
                    validate_table(filemap[url], table)
                else:
                    with open(filemap[url], encoding='utf-8') as f:
                        validate_table(f, table)
            except ValidationException as e:
                errors.append('{}: {}'.format(url, str(e)))
    return errors


def validate_table(f, table):
    dec_symb = table.find("./DecimalSymbol").text
    digit_group_symb = table.find("./DigitGroupingSymbol").text
    if not table.findall("./Range"):
        range_start = 1
    else:
        range_start = int(table.find("./Range").find("./From").text)
    record_delim = table.find("./VariableLength/RecordDelimiter").text
    column_delim = table.find("./VariableLength/ColumnDelimiter").text
    text_encaps = table.find("./VariableLength/TextEncapsulator").text

    regex_part_integer = r'-?([0-9]+|[0-9]{1,3}(%s[0-9]{3})*)' % digit_group_symb

    if range_start != 2:
        raise ValidationException("Range is != [2, End], this is not technically invalid but prevents "
                                  "column header validation.")

    if table.findall("./FixedLength"):
        raise ValidationException("Fixed length validation is currently not supported.")

    if table.findall("./VariableLength/VariablePrimaryKey"):
        raise ValidationException("Primary key validation is currently not supported.")

    csvreader = csv.reader(
        f,
        delimiter=column_delim,
        quotechar=text_encaps,
        quoting=csv.QUOTE_MINIMAL
    )
    coldefs = table.findall("./VariableLength/VariableColumn")
    for i, row in enumerate(csvreader):
        ncol_csv = len(row)
        if ncol_csv != len(coldefs):
            raise ValidationException("Line {}: Row has {} fields but index.xml defines {} fields.".format(
                i + 1, ncol_csv, len(coldefs)
            ))
        if i == 0:
            for j, c in enumerate(coldefs):
                if c.find("./Name").text != row[j]:
                    raise ValidationException("Expected column {} to be {}, but headline is {}.".format(
                        j + 1, c.find("./Name").text, row[j]
                    ))
        else:
            for j, c in enumerate(coldefs):
                if c.findall("./Numeric"):
                    regex = regex_part_integer
                    dec_places = 0
                    if c.findall("./Numeric/Accuracy"):
                        dec_places = int(c.find("./Numeric/Accuracy").text)
                        regex += r"[%s]{1}[0-9]{%s}" % (dec_symb, dec_places)
                    if row[j] == "":
                        # It's unclear if empty strings are allowed in numeric fields
                        continue
                    if not re.match("^" + regex + "$", row[j]):
                        print("^" + regex + "$", row[j])
                        print(
                            "Line {}: Value {} in column {} is not a valid decimal with {} places".format(
                                i + 1,
                                row[j],
                                j + 1,
                                dec_places
                            )
                        )
                elif c.findall("./AlphaNumeric"):
                    if c.findall("./MaxLength"):
                        ml = int(c.find("./MaxLength").text)
                        if len(row[j]) > ml:
                            print(
                                "Line {}: Value {} in column {} is not allowed to have more than {} " \
                                "characters".format(
                                    i + 1,
                                    repr(row[j]),
                                    j + 1,
                                    ml
                                )
                            )
                elif c.findall("./Date"):
                    raise ValidationException("Date validation currently not supported")
                else:
                    raise ValidationException("Unsupported data type for column {}".format(j=j + 1))


def validate_dir(dirname):
    fmap = {}
    for f in os.listdir(dirname):
        fmap[f] = os.path.join(dirname, f)
    return validate_files(fmap)


def validate_zip(archive):
    with zipfile.ZipFile(archive, "r") as zf:
        fmap = {}
        for f in zf.namelist():
            with zf.open(f) as fp:
                fmap[f] = StringIO(fp.read().decode("utf-8"))
        return validate_files(fmap)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Call me with a directory name as the first argument.")
        sys.exit(1)
    errs = validate_dir(sys.argv[1])
    if errs:
        print("Validation failed. Errors:")
        for e in errs:
            print("-", e)
        sys.exit(1)
