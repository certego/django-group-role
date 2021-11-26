from django.test import SimpleTestCase
from django_group_role import Role, registry
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
            AssertionError, "Role permissions must be a list, a set, a tuple or a dict"
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
            ValueError,
            "Permissions, should be defined in the format: 'app_label.codename' (is perm)",
        ):

            class NoPermRole(Role):
                name = "test"
                permissions = ["perm", 1]

    def test_role_composition(self):
        self.assertCountEqual(
            UserManagers._permissions,
            {
                "auth": {
                    "_codenames": {"view_user", "view_group", "add_user", "change_user"}
                }
            },
        )
        self.assertCountEqual(
            GroupManagers._permissions,
            {
                "auth": {
                    "_codenames": {
                        "view_user",
                        "view_group",
                        "add_group",
                        "delete_group",
                    }
                }
            },
        )

    def test_abstract_role(self):
        class AbstractRole(Role):
            abstract = True
            name = "abstract"
            permissions = ["auth.view_user"]

        self.assertNotIn("abstract", registry)
