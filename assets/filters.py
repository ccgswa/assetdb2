from django.contrib import admin
from django.contrib.admin.filters import FieldListFilter
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import datetime
from datetime import date


class YearPurchasedListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('purchase date')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'purchase_date'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        date_list = [('Today', 'Today'),
                     ('Past 7 days', 'Past 7 days'),
                     ('This month', 'This month'),
                     ('This year', 'This year')]

        current_year = date.today().year
        years = set([str(year) for year in range(current_year-1, current_year-10, -1)])
        # year_list = [(str(year), str(year)) for year in years]
        years_desc = sorted(years, key=int, reverse=True)

        for year in years_desc:
            date_list.append((str(year), str(year)))

        date_list.append(('older', 'older'))

        return date_list

    # def choices(self, cl):  # Override this method to prevent the default "All".
    # Evaluates display text as query string. Not suitable for use!
        # from django.utils.encoding import force_text
    #     for lookup, title in self.lookup_choices:
    #         yield {
    #             'selected': False,
    #             'query_string': cl.get_query_string({
    #                 self.parameter_name: lookup,
    #             }, []),
    #             'display': title,
    #         }

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        next_year = today.replace(year=today.year + 1, month=1, day=1)

        # this_year = date.today().year

        # Filter the query set based on purchase year selected

        if self.value() == 'Any date':
            return queryset

        elif self.value() == 'Today':
            return queryset.filter(purchase_date__gte=today,
                                   purchase_date__lte=tomorrow)

        elif self.value() == 'Past 7 days':
            return queryset.filter(purchase_date__gte=today - datetime.timedelta(days=7),
                                   purchase_date__lte=tomorrow)

        elif self.value() == 'This month':
            return queryset.filter(purchase_date__gte=today.replace(day=1),
                                   purchase_date__lte=next_month)

        elif self.value() == 'This year':
            return queryset.filter(purchase_date__gte=today.replace(month=1, day=1),
                                   purchase_date__lte=next_year)

        elif self.value() == 'older':
            return queryset.filter(purchase_date__lte=today.replace(year=today.year-10, month=12, day=31))

        elif self.value():
            year = int(self.value())
            return queryset.filter(purchase_date__gte=date(year, 1, 1),
                                   purchase_date__lte=date(year, 12, 31))
        else:
            return queryset


# TODO Django won't let me use a filter in list_filter that inherits directly from FieldListFilter! T_T
# Rewritten DateFieldListFilter - DO NOT USE
class PurchaseYearListFilter(FieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        field_path = 'purchase_date'
        self.field_generic = '%s__' % field_path
        self.date_params = {k: v for k, v in params.items()
                            if k.startswith(self.field_generic)}

        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        next_year = today.replace(year=today.year + 1, month=1, day=1)

        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_until = '%s__lt' % field_path
        self.links = (
            (_('Any date'), {}),
            (_('Today'), {
                self.lookup_kwarg_since: str(today),
                self.lookup_kwarg_until: str(tomorrow),
            }),
            (_('Past 7 days'), {
                self.lookup_kwarg_since: str(today - datetime.timedelta(days=7)),
                self.lookup_kwarg_until: str(tomorrow),
            }),
            (_('This month'), {
                self.lookup_kwarg_since: str(today.replace(day=1)),
                self.lookup_kwarg_until: str(next_month),
            }),
            (_('This year'), {
                self.lookup_kwarg_since: str(today.replace(month=1, day=1)),
                self.lookup_kwarg_until: str(next_year),
            }),
        )

        this_year = today.year
        years = set([str(year) for year in range(this_year-1, this_year-10, -1)])
        # year_list = [(str(year), str(year)) for year in years]
        years_desc = sorted(years, key=int, reverse=True)

        for year in years_desc:
            year_link = (_(year), {
                self.lookup_kwarg_since: str(today.replace(year=year, month=1, day=1)),
                self.lookup_kwarg_until: str(today.replace(year=year+1, month=12, day=31)),
                })
            self.links += (year_link, )

        older_link = (_('older'), {
            self.lookup_kwarg_since: str(today.replace(year=1000, month=1, day=1)),
            self.lookup_kwarg_until: str(today.replace(year=this_year+11, month=1, day=1)),
            })

        self.links += (older_link, )

        super(PurchaseYearListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

    def expected_parameters(self):
        return [self.lookup_kwarg_since, self.lookup_kwarg_until]

    def choices(self, cl):
        for title, param_dict in self.links:
            yield {
                'selected': self.date_params == param_dict,
                'query_string': cl.get_query_string(
                    param_dict, [self.field_generic]),
                'display': title,
            }