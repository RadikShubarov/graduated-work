from django import template
from ..models import Host

register = template.Library()


@register.simple_tag()
def get_hosts():
    return Host.objects.all()


