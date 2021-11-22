from django.contrib.auth.models import Group
from django.test import TestCase
from guardian.shortcuts import assign_perm
from example_project.roles import BasicRole


class DatabaseSetupTestCase(TestCase):
    def test_create_role_group_if_not_exists(self):
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get_by_natural_key("Users")

        role = BasicRole()
        self.assertIsInstance(role.group, Group)
        group = Group.objects.get_by_natural_key("Users")
        self.assertEqual(group, role.group)

    def test_get_existing_role_group(self):
        group = Group.objects.create(name="Users")
        role = BasicRole()
        self.assertIsInstance(role.group, Group)
        self.assertEqual(group, role.group)

    def test_group_permissions_assignment(self):
        Group.objects.create(name="Users")
        role = BasicRole()
        self.assertFalse(role.group.permissions.all().exists())
        assign_perm("auth.delete_user", role.group)
        role.setup_permissions()
        self.assertQuerysetEqual(
            role.group.permissions.values_list("codename", flat=True),
            ["view_user", "view_group", "delete_user"],
            ordered=False,
        )

    def test_group_permissions_assignment_with_reset(self):
        Group.objects.create(name="Users")
        role = BasicRole()
        self.assertFalse(role.group.permissions.all().exists())
        assign_perm("auth.delete_user", role.group)
        role.setup_permissions(True)
        self.assertQuerysetEqual(
            role.group.permissions.values_list("codename", flat=True),
            [
                "view_user",
                "view_group",
            ],
            ordered=False,
        )
