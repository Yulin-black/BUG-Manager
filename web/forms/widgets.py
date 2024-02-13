from django.forms import RadioSelect, Select


class ColorRadioSelect(RadioSelect):
    template_name = "widgets/color_radio/radio.html"
    option_template_name = "widgets/color_radio/radio_option.html"


class ColorPrioritySelect(Select):
    template_name = "widgets/color_select/select.html"
    option_template_name = "widgets/color_select/select_option.html"
