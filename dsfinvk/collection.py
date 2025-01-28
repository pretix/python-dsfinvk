import csv
import os
from collections import defaultdict
from io import StringIO
from tempfile import TemporaryFile, NamedTemporaryFile
from zipfile import ZipFile
from lxml import etree

from .table import Model


class Collection:
    def __init__(self):
        self.records = defaultdict(list)

    def add(self, record: Model):
        self.records[record._filename].append(record)

    def write(self, name, xml_path=None, dtd_path=None):
        with ZipFile(name, 'w') as zf:
            for k, l in self.records.items():
                b = StringIO()
                w = csv.DictWriter(b, fieldnames=[f.name for f in l[0]._fields], delimiter=";", lineterminator="\r\n")
                w.writeheader()
                for r in l:
                    if r._data:
                        w.writerow(r._data)
                b.seek(0)
                zf.writestr(k, b.read())

            if not xml_path:
                xml_path, dtd_path = self.generate_xml()
                zf.write(xml_path, 'index.xml')
                zf.write(dtd_path, os.path.basename(dtd_path))
                os.unlink(xml_path)
            else:
                zf.write(xml_path, 'index.xml')
                zf.write(dtd_path, os.path.basename(dtd_path))

    def find_asset(self, fn):
        dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets'))
        f = os.path.join(dir, fn)
        if os.path.exists(f):
            return f
        return None

    def generate_xml(self):
        xml_file = self.find_asset('index.xml')
        if not xml_file:
            raise RuntimeError('cannot find bundled index.xml')
        parser = etree.XMLParser(load_dtd=True, resolve_entities=False)
        tree = etree.parse(xml_file, parser)
        root = tree.getroot()

        for media in root.xpath(".//Media"):
            for table in media.xpath("Table"):
                url_element = table.find("URL")
                if url_element is not None and url_element.text not in self.records:
                    media.remove(table)

        dtd_uri = self.find_asset(tree.docinfo.system_url)
        if not os.path.exists(dtd_uri):
            raise RuntimeError('cannot find referenced DTD')

        with NamedTemporaryFile('wb+', delete=False) as new_xml_file:
            tree.write(new_xml_file, pretty_print=True, encoding="utf-8", xml_declaration=True,
                       doctype=tree.docinfo.doctype)
        with open(new_xml_file.name, 'r+') as f:
            # LXML ersetzt beim RecordDelimiter das Newline durch ein echtes Newline.
            # Das ist möglicherweise ein Problem. Daher ersetzen wir das danach in der Datei.
            content = f.read()
            f.seek(0)
            f.write(content.replace('<RecordDelimiter>&#13;\n</RecordDelimiter>',
                                    '<RecordDelimiter>&#13;&#10;</RecordDelimiter>'))
        return new_xml_file.name, dtd_uri
