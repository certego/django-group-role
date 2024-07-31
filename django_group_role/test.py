from django.test import override_settings
from .exceptions import BadRoleException
from .roles import load_roles, registry


class RoleEnabledTestMixin:
    force_role_reload = False
    clear_role_registry = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        rolenames = getattr(cls, "roles", None)
        if isinstance(rolenames, str):
            rolenames = [rolenames]
        roles_from = getattr(cls, "roles_from", None)
        if roles_from:
            # get roles from override
            # always force reload
            with override_settings(ROLES_MODULE=roles_from):
                load_roles(force=True, clear=cls.clear_role_registry)
        else:
            # load standard roles
            load_roles(force=cls.force_role_reload, clear=cls.clear_role_registry)

        # setup roles
        for name, role in registry.items():
            if not rolenames or name in rolenames:
                # istantiate role class
                role = role()
                try:
                    role.setup_permissions()
                except BadRoleException as e:
                    # if something wrong raise assertion
                    raise AssertionError(str(e))
