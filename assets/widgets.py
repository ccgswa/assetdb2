from import_export import widgets
from datetime import date
import tablib


class AssetLocationWidget(widgets.CharWidget):

    def clean(self, value):
        if value is None or '' or 'None':
            return 'none'
        else:
            return value


class ExcelDateWidget(widgets.CharWidget):
    """
    Excel date widget.

        * ``datemode``
    """

    def __init__(self, datemode, *args, **kwargs):
        self.datemode = datemode
        super(ExcelDateWidget, self).__init__(*args, **kwargs)

    def render(self, value):
        if value is None:
            return None
        return tablib.compat.xlrd.xldate.xldate_from_date_tuple(
            value.timetuple()[:3], self.datemode)

    def clean(self, value):
        if not value:
            return None
        tup = tablib.compat.xlrd.xldate.xldate_as_tuple(value, self.datemode)
        return date(*tup[:3])