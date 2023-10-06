from django import VERSION
from django.contrib.auth.models import Group
from django.test import TestCase
from django_group_role.test import RoleEnabledTestMixin


class BaseTestingTestCase(RoleEnabledTestMixin, TestCase):
    if VERSION < (4, 2):
        def assertQuerySetEqual(self, *args, **kwargs):
            return super().assertQuerysetEqual(*args, **kwargs)

    clear_role_registry = True
    force_role_reload = True


class OnlySelectedTestCase(BaseTestingTestCase):
    roles = ["Users", "User-Managers"]

    def test_roles(self):
        self.assertQuerySetEqual(
            Group.objects.values_list("name", flat=True).order_by("name"),
            [
                "User-Managers",
                "Users",
            ],
            transform=str,
        )
        group = Group.objects.get_by_natural_key("Users")
        self.assertQuerySetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        group = Group.objects.get_by_natural_key("User-Managers")
        self.assertQuerySetEqual(
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


class OverrideFromRolesTestCase(BaseTestingTestCase):
    roles_from = "example_project.roles_secondary"

    def test_roles(self):
        self.assertQuerySetEqual(
            Group.objects.values_list("name", flat=True).order_by("name"),
            [
                "Base",
                "Groupers",
                "Managers",
            ],
            transform=str,
        )
        group = Group.objects.get_by_natural_key("Base")
        self.assertQuerySetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        group = Group.objects.get_by_natural_key("Managers")
        self.assertQuerySetEqual(
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
        group = Group.objects.get_by_natural_key("Groupers")
        self.assertQuerySetEqual(
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
