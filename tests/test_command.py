from io import StringIO
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase, override_settings
from guardian.shortcuts import assign_perm


class CommandTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group_maps = {
            "Users": ["auth.view_user", "auth.delete_user"],
            "User-Managers": ["auth.view_user", "auth.delete_user"],
            "Other": ["auth.view_user"],
        }
        for name, perms in group_maps.items():
            group = Group.objects.create(name=name)
            for perm in perms:
                assign_perm(perm, group)

    def test_apply_every_role(self):
        self.assertEqual(Group.objects.all().count(), 3)
        out = StringIO()
        call_command("populate_roles", stdout=out)
        self.assertEqual(
            out.getvalue().split("\n"),
            [
                'Setting permissions for role "Users"...',
                'Role "Users" setup completed!',
                'Setting permissions for role "User-Managers"...',
                'Role "User-Managers" setup completed!',
                'Setting permissions for role "Group-Managers"...',
                'Role "Group-Managers" setup completed!',
                'Setting permissions for role "Broken"...',
                'Unable to bound permission to "Broken" (Permission auth.non_existing_perm cannot be bound to role)',
                "",
            ],
        )
        self.assertEqual(Group.objects.all().count(), 5)
        group = Group.objects.get_by_natural_key("Users")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
                ("delete_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        group = Group.objects.get_by_natural_key("User-Managers")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
                ("delete_user", "auth", "user"),
                ("change_user", "auth", "user"),
                ("add_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        group = Group.objects.get_by_natural_key("Group-Managers")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
                ("add_group", "auth", "group"),
                ("delete_group", "auth", "group"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )

    def test_apply_every_role_clear(self):
        self.assertEqual(Group.objects.all().count(), 3)
        out = StringIO()
        call_command("populate_roles", clear=True, stdout=out)
        self.assertEqual(
            out.getvalue().split("\n"),
            [
                "Clear mode enabled, already bound permissions will be removed!",
                'Setting permissions for role "Users"...',
                'Role "Users" setup completed!',
                'Setting permissions for role "User-Managers"...',
                'Role "User-Managers" setup completed!',
                'Setting permissions for role "Group-Managers"...',
                'Role "Group-Managers" setup completed!',
                'Setting permissions for role "Broken"...',
                'Unable to bound permission to "Broken" (Permission auth.non_existing_perm cannot be bound to role)',
                "",
            ],
        )
        self.assertEqual(Group.objects.all().count(), 5)
        group = Group.objects.get_by_natural_key("Users")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        group = Group.objects.get_by_natural_key("User-Managers")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
                ("change_user", "auth", "user"),
                ("add_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        group = Group.objects.get_by_natural_key("Group-Managers")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
                ("add_group", "auth", "group"),
                ("delete_group", "auth", "group"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )

    def test_apply_single_role_clear(self):
        self.assertEqual(Group.objects.all().count(), 3)
        out = StringIO()
        call_command("populate_roles", "Users", clear=True, stdout=out)
        self.assertEqual(
            out.getvalue().split("\n"),
            [
                "Clear mode enabled, already bound permissions will be removed!",
                'Setting permissions for role "Users"...',
                'Role "Users" setup completed!',
                "",
            ],
        )
        self.assertEqual(Group.objects.all().count(), 3)
        group = Group.objects.get_by_natural_key("Users")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        # user managers group was not modified
        group = Group.objects.get_by_natural_key("User-Managers")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_user", "auth", "user"),
                ("delete_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        # group managers was not created at all
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get_by_natural_key("Group-Managers")
