from django.test import SimpleTestCase
from django_group_role.roles import Role
from example_project.roles import UserManagers, GroupManagers, BasicRole


class DefinitionsTestCase(SimpleTestCase):
    def test_role_wrong_group(self):
        with self.assertRaisesMessage(AssertionError, "Role name must not be empty"):

            class NoGroupRole(Role):
                pass

        with self.assertRaisesMessage(AssertionError, "Role name must not be empty"):

            class NoGroupRole(Role):
                name = ""

    def test_role_wrong_permissions(self):
        with self.assertRaisesMessage(
            AssertionError, "Role permissions must be a list a set or a tuple"
        ):

            class NoPermRole(Role):
                name = "test"
                permissions = "invalid"

        with self.assertRaisesMessage(
            AssertionError, "A Role must specify at least 1 permission"
        ):

            class NoPermRole(Role):
                name = "test"
                permissions = []

        with self.assertRaisesMessage(
            AssertionError, "Permissions must be represented with strings"
        ):

            class NoPermRole(Role):
                name = "test"
                permissions = ["perm", 1]

    def test_role_composition(self):
        self.assertCountEqual(
            UserManagers._permissions,
            ["auth.view_user", "auth.view_group", "auth.add_user", "auth.change_user"],
        )
        self.assertCountEqual(
            GroupManagers._permissions,
            [
                "auth.view_user",
                "auth.view_group",
                "auth.add_group",
                "auth.delete_group",
            ],
        )
