from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def dashboard_url(context):
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return reverse('home')
    user = request.user
    mapping = {
        'admin': 'dashboard_admin',
        'student': 'dashboard_student',
        'teacher': 'dashboard_teacher',
        'parent': 'dashboard_parent',
    }
    name = mapping.get(getattr(user, 'role', ''), 'home')
    try:
        return reverse(name)
    except Exception:
        return reverse('home')
