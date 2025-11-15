from django import template

register = template.Library()


# ======================================================
#   دوال حسابية مساعدة للتقارير
# ======================================================

@register.filter
def div(value, arg):
    """قسمة رقمين مع تجنب القسمة على صفر"""
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0
        return value / arg
    except:
        return 0


@register.filter
def mul(value, arg):
    """ضرب رقمين"""
    try:
        return float(value) * float(arg)
    except:
        return 0


@register.filter
def percent(value, total):
    """
    إرجاع النسبة % كنص جاهز مثل: 84.5%
    """
    try:
        value = float(value)
        total = float(total)
        if total == 0:
            return "0%"
        return f"{(value / total) * 100:.1f}%"
    except:
        return "0%"


@register.filter
def percentage(value, total):
    """
    إرجاع النسبة كرقم فقط بدون علامة % للاستخدام الحسابي
    """
    try:
        value = float(value)
        total = float(total)
        if total == 0:
            return 0
        return round((value / total) * 100, 1)
    except:
        return 0


@register.filter
def format_num(value):
    """
    تنسيق الأرقام بفواصل مثال:
    1234567 → 1,234,567
    """
    try:
        return f"{int(value):,}"
    except:
        return value
