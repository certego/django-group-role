from copy import deepcopy
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django_group_role.roles import Role, registry, load_roles
from django_group_role.test import RoleEnabledTestMixin


class BaseTestingTestCase(RoleEnabledTestMixin, TestCase):
    # need to keep registry clear in these tests
    @classmethod
    def setUpClass(cls):
        cls._registry = deepcopy(registry)
        registry.clear()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        registry.clear()
        registry.update(cls._registry)


class OnlySelectedTestCase(BaseTestingTestCase):
    roles = ["Users", "User-Managers"]

    def test_roles(self):
        self.assertQuerysetEqual(
            Group.objects.values_list("name", flat=True).order_by("name"),
            [
                "User-Managers",
                "Users",
            ],
        )
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


class OverrideFromRolesTestCase(BaseTestingTestCase):
    roles_from = "example_project.roles_secondary"

    def test_roles(self):
        self.assertQuerysetEqual(
            Group.objects.values_list("name", flat=True).order_by("name"),
            [
                "Base",
                "Groupers",
                "Managers",
            ],
        )
        group = Group.objects.get_by_natural_key("Base")
        self.assertQuerysetEqual(
            group.permissions.all(),
            [
                ("view_group", "auth", "group"),
                ("view_user", "auth", "user"),
            ],
            transform=lambda p: p.natural_key(),
            ordered=False,
        )
        group = Group.objects.get_by_natural_key("Managers")
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
        group = Group.objects.get_by_natural_key("Groupers")
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
