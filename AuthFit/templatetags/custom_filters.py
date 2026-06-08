import json
from django import template

register = template.Library()

@register.filter
def safe_json(value):
    return json.dumps(value)