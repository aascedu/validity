from typing import Any

from django import template
from django.db.models import Model
from django.http.request import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from utilities.templatetags.builtins.filters import linkify, placeholder


register = template.Library()


@register.filter
def colored_choice(obj: Model, field: str) -> str:
    if not (raw_value := getattr(obj, field)):
        return raw_value
    value = getattr(obj, f"get_{field}_display")
    color = getattr(obj, f"get_{field}_color")
    return mark_safe(f'<span class="badge text-bg-{color()}">{value()}</span>')


@register.filter
def linkify_list(obj_list: list[Model], attr: str | None = None) -> str:
    result = ", ".join(linkify(obj, attr) for obj in obj_list)
    return placeholder("") if not result else mark_safe(result)


@register.filter
def checkmark(value: Any) -> str:
    value = bool(value)
    attr_map = {False: "mdi-close-thick text-danger", True: "mdi-check-bold text-success"}
    attr = attr_map[value]
    return mark_safe(f'<i class="mdi {attr}" title="{value}"></i>')


@register.filter
def data_source(model) -> str:
    return _("Data Source") if model.data_source else _("DB")


@register.filter
def colorful_percentage(percent: float) -> str:
    levels = {75: "yellow", 50: "orange", 25: "danger"}
    badge_color = "success"
    for level, color in levels.items():
        if level <= percent:
            break
        badge_color = color
    percent = round(percent, 1)
    return format_html('<span class="badge rounded-pill text-bg-{}">{}%</span>', badge_color, percent)


@register.simple_tag
def url_with_query_params(request: HttpRequest, **params):
    params = {k: [v] if not isinstance(v, list) else v for k, v in params.items()}
    query_params = request.GET.copy()
    query_params |= params
    return f"{request.path}?{query_params.urlencode()}"


@register.simple_tag
def urljoin(*parts: str) -> str:
    if len(parts) <= 1:
        return "".join(parts)
    middle_parts = "/".join((part.strip("/") for part in parts[1:-1]))
    url_parts = [parts[0].rstrip("/"), parts[-1].lstrip("/")]
    if middle_parts:
        url_parts.insert(1, middle_parts)
    return "/".join(url_parts)


@register.simple_tag
def report_stats(obj, severity):
    count = getattr(obj, f"{severity}_count")
    if count == 0:
        return "—"
    passed = getattr(obj, f"{severity}_passed")
    percentage = getattr(obj, f"{severity}_percentage")
    return mark_safe(f"{passed}/{count} ") + colorful_percentage(percentage)


@register.filter
def filler(value, fill_with="—"):
    """
    Like placeholder, but with arbitrary fill_with value
    """
    return value if value else mark_safe(fill_with)
