from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

class HasOpenpolisIdListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Has OP ID')
    parameter_name = 'has_op_id'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('yes')),
            ('no', _('no')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'yes':
            return queryset.filter(openpolis_id__isnull=False).exclude(openpolis_id='')
        if self.value() == 'no':
            return queryset.filter(Q(openpolis_id__isnull=True) | Q(openpolis_id=''))



class HasBirthDateListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Has Birth Date')
    parameter_name = 'has_birth_date'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('yes')),
            ('no', _('no')),
            )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'yes':
            return queryset.filter(data_nascita__isnull=False)
        if self.value() == 'no':
            return queryset.filter(data_nascita__isnull=True)




class HasBirthLocationListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Has Birth Location')
    parameter_name = 'has_birth_location'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('yes')),
            ('no', _('no')),
            )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'yes':
            return queryset.filter(luogo_nascita__isnull=False).exclude(luogo_nascita='')
        if self.value() == 'no':
            return queryset.filter(Q(luogo_nascita__isnull=True) | Q(luogo_nascita=''))

