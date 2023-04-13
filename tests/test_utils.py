from django.test import SimpleTestCase
from django_group_role.utils import map_permissions


class UtilsSimpleTestCase(SimpleTestCase):
    def test_map_permissions_list_wrong_code(self):
        with self.assertRaisesMessage(
            ValueError,
            "Permissions, should be defined in the format: 'app_label.codename' (but is view_user)",
        ):
            map_permissions(["view_user"])

    def test_map_permissions_list(self):
        perm_map = map_permissions(
            ["auth.view_user", "auth.view_group", "myapp.view_mymodel"]
        )
        self.assertEqual(
            perm_map,
            {
                "auth": {"_codenames": {"view_user", "view_group"}},
                "myapp": {"_codenames": {"view_mymodel"}},
            },
        )

    def test_map_permissions_dict(self):
        perm_map = map_permissions(
            {
                "auth.user": ["view_user", "change_user"],
                "auth": {"group": ["view_group"]},
                "myapp.mymodel": ["view_mymodel", "change_mymodel"],
            }
        )
        self.assertEqual(
            perm_map,
            {
                "auth": {"user": {"view_user", "change_user"}, "group": {"view_group"}},
                "myapp": {
                    "mymodel": {"view_mymodel", "change_mymodel"},
                },
            },
        )

    def test_map_permissions_dict_plus_list(self):
        perm_map = map_permissions(
            {
                "auth.user": ["view_user", "change_user"],
                "auth": {"group": ["view_group"]},
                "myapp.mymodel": ["view_mymodel", "change_mymodel"],
            },
            ["auth.view_user", "myapp.delete_mymodel", "otherapp.view_element"],
        )
        self.assertEqual(
            perm_map,
            {
                "auth": {
                    "_codenames": {"view_user"},
                    "user": {"view_user", "change_user"},
                    "group": {"view_group"},
                },
                "myapp": {
                    "_codenames": {"delete_mymodel"},
                    "mymodel": {"view_mymodel", "change_mymodel"},
                },
                "otherapp": {
                    "_codenames": {"view_element"},
                },
            },
        )

    def test_map_permissions_list_plus_dict(self):
        perm_map = map_permissions(
            ["auth.view_user", "myapp.delete_mymodel", "otherapp.view_element"],
            {
                "auth.user": ["view_user", "change_user"],
                "auth": {"group": ["view_group"]},
                "myapp.mymodel": ["view_mymodel", "change_mymodel"],
            },
        )
        self.assertEqual(
            perm_map,
            {
                "auth": {
                    "_codenames": {"view_user"},
                    "user": {"view_user", "change_user"},
                    "group": {"view_group"},
                },
                "myapp": {
                    "_codenames": {"delete_mymodel"},
                    "mymodel": {"view_mymodel", "change_mymodel"},
                },
                "otherapp": {
                    "_codenames": {"view_element"},
                },
            },
        )

    def test_map_permissions_dict_plus_dict(self):
        perm_map = map_permissions(
            {
                "auth": {"user": ["view_user"]},
                "myapp": {"mymodel": ["delete_mymodel"]},
                "otherapp.element": ["view_element"],
            },
            {
                "auth.user": ["view_user", "change_user"],
                "auth": {"group": ["view_group"]},
                "myapp.mymodel": ["view_mymodel", "change_mymodel"],
            },
        )
        self.assertEqual(
            perm_map,
            {
                "auth": {
                    "user": {"view_user", "change_user"},
                    "group": {"view_group"},
                },
                "myapp": {
                    "mymodel": {"view_mymodel", "change_mymodel", "delete_mymodel"},
                },
                "otherapp": {
                    "element": {"view_element"},
                },
            },
        )
