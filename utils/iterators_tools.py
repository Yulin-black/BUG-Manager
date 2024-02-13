from django.utils.safestring import mark_safe


class ChoicesButton:
    def __init__(self, name, choices_list, request):
        self.choices_list = choices_list
        self.request = request
        self.name = name

    def __iter__(self):
        for item in self.choices_list:
            key = str(item[0])
            value = item[1]

            request_copy = self.request.GET.copy()
            request_value = request_copy.getlist(self.name)
            request_copy._mutable = True

            if key in request_value:
                checkbox = "checked"
                request_value.remove(key)
            else:
                checkbox = ""
                request_value.append(key)

            request_copy.setlist(self.name, request_value)
            if 'page' in request_copy:
                request_copy.pop('page')

            url = self.request.path + f"?{request_copy.urlencode()}"

            html = f"<a class='cell' href='{url}'><input type='checkbox' {checkbox}/><label>{value}</label></a>"
            yield mark_safe(html)


class ForeignKeySelect:
    def __init__(self, name, fk_list, request):
        self.fk_list = fk_list
        self.request = request
        self.name = name

    def __iter__(self):
        request_copy = self.request.GET.copy()
        request_copy._mutable = True
        if 'page' in request_copy:
            request_copy.pop('page')
        if self.name in request_copy:
            request_copy.pop(self.name)

        yield mark_safe(
            f"<select class='selectpicker' data-live-search='true' multiple value='{request_copy.urlencode()}' name='{self.name}'>")
        for item in self.fk_list:
            key = str(item[0])
            value = item[1]
            request_value = self.request.GET.getlist(self.name)

            if key in request_value:
                checkbox = "selected"
                request_value.remove(key)
            else:
                checkbox = ""
                request_value.append(key)

            option = f"<option value='{key}' {checkbox}>{value}</option>"
            yield mark_safe(option)
        yield mark_safe("</select>")
