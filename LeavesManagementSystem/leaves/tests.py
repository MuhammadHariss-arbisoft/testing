# from django.test import TestCase
# from django.contrib.auth.models import Permission, Group
# from django.contrib.contenttypes.models import ContentType
# from .models import Leave



# # def test_group_creation():
# #     test_group, created = Group.objects.get_or_create(name='TestGroup')
# #     print(created)
# #     p1 = Permission.objects.get(codename='delete_leave')
# #     p2 = Permission.objects.get(codename='view_leave')
# #     p = [p1, p2]
# #     print(type(p))
# #     test_group.permissions.add(*p)
# #     test_group.save()

# # def test_assign_group_to_user():
# #     user = User.objects.filter(username='zain').first()
# #     group = Group.objects.filter(name='TestGroup').first()
# #     group.user_set.add(user)
# #     group.save()
