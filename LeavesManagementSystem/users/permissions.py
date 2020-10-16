from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from leaves.models import Leave


content_type = ContentType.objects.get_for_model(Leave)

VIEW_LEAVE_REQUESTS, created = Permission.objects.get_or_create(codename='view_leave_requests', name='Can View Appliers Leave Requests',
                                                                content_type=content_type)
REQUEST_LEAVE, created = Permission.objects.get_or_create(codename='request_leave', name='Can Request Leave To Its Approver',
                                                                content_type=content_type)
APPROVE_REJECT_LEAVE, created = Permission.objects.get_or_create(codename='approve_reject_leave',
                                                            name='Can Approve its Appliers Leaves', content_type=content_type)
VIEW_APPLIERS_LEAVES_HISTORY, created = Permission.objects.get_or_create(codename='view_appliers_leaves_history',
                                                            name='Can View Its appliers leaves history', content_type=content_type)
VIEW_ALL_LEAVES_HISTORY, created = Permission.objects.get_or_create(codename='view_all_leaves_history',
                                                            name='Can View All Leaves History', content_type=content_type)


def create_group_permissions(group_name, permissions):
    group, created = Group.objects.get_or_create(name=group_name)
    group.permissions.set(permissions)
    group.save()


def create_user_groups_permissions(apps, schema_editor):
    create_group_permissions('super', [VIEW_LEAVE_REQUESTS, APPROVE_REJECT_LEAVE, VIEW_APPLIERS_LEAVES_HISTORY, VIEW_ALL_LEAVES_HISTORY])
    create_group_permissions('approver', [VIEW_LEAVE_REQUESTS, REQUEST_LEAVE, APPROVE_REJECT_LEAVE, VIEW_APPLIERS_LEAVES_HISTORY])
    create_group_permissions('employee', [REQUEST_LEAVE])
