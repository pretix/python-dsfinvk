from datetime import datetime
from decimal import Decimal

import pytz
from dsfinvk.collection import Collection
from dsfinvk.models import Z_Waehrungen

c = Collection()
record = Z_Waehrungen()
record.Z_KASSE_ID = '0'
record.Z_ERSTELLUNG = datetime.now(pytz.timezone("Europe/Berlin"))
record.Z_NR = 1
record.ZAHLART_WAEH = "EUR"
record.ZAHLART_BETRAG_WAEH = Decimal("123.23")
c.add(record)

c.write("sample.zip")
