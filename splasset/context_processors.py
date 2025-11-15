from django.contrib.auth.models import Group
from inventory_app.models import InventorySession


def user_groups(request):
    if request.user.is_authenticated:
        groups = list(request.user.groups.values_list("name", flat=True))
    else:
        groups = []
    return {"user_groups": groups}


def pending_sessions(request):
    if request.user.is_authenticated:
        count = InventorySession.objects.filter(status="supervisor_under_review").count()
    else:
        count = 0
    return {"pending_count": count}