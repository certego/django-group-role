from copy import deepcopy
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from django_group_role.roles import Role, registry, load_roles


class ConfigurationTestCase(SimpleTestCase):
    # need to keep registry clear in these tests
    def setUp(self):
        self._registry = deepcopy(registry)
        registry.clear()

    def tearDown(self):
        registry.clear()
        registry.update(self._registry)

    @override_settings(ROLES_MODULE=None)
    def test_configuration_errors(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "ROLES_MODULE settings is required to correctly load roles!",
        ):
            load_roles()

    @override_settings(ROLES_MODULE="nowhere.nothing")
    def test_configuration_module_not_found(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "No module nowhere.nothing from which import roles found!",
        ):
            load_roles()

    @override_settings(ROLES_MODULE="example_project.roles_secondary")
    def test_loading(self):
        load_roles()
        self.assertCountEqual(
            registry.keys(),
            [
                "Base",
                "Managers",
                "Groupers",
            ],
        )
