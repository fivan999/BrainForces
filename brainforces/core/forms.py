import django.forms


class SearchForm(django.forms.Form):
    """форма для поиска"""

    query = django.forms.CharField()
    search_by = django.forms.ChoiceField(choices=[])
