def user_groups(request):
    if request.user.is_authenticated:
        groups = list(request.user.groups.values_list("name", flat=True))
    else:
        groups = []

    return {
        "groups": groups
    }
