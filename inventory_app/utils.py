from django.contrib.auth.models import Group

def is_employee(user):
    """صلاحيات الموظف — يعمل الجرد ويرفعه للمشرف"""
    return user.groups.filter(name="employees").exists()

def is_supervisor(user):
    """صلاحيات المشرف — يراجع الجرد ويقبل أو يرفض"""
    return user.groups.filter(name="supervisors").exists()

def is_admin(user):
    """صلاحيات المدير — أعلى صلاحية"""
    return user.is_superuser or user.groups.filter(name="admins").exists()
