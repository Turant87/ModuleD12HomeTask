from django import template
from django.utils.safestring import mark_safe

register = template.Library()

BAD_WORDS = ["Плохое слово", "Очень плохое слово", "Кий"]

@register.filter(name='censor')
def censor(value):
    for word in BAD_WORDS:
        value = value.replace(word, "*censored*")
    return mark_safe(value)
