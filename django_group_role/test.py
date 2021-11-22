from django.test import override_settings
from .roles import load_roles, registry, BadRoleException


class RoleEnabledTestMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        rolenames = getattr(cls, "roles", None)
        if isinstance(rolenames, str):
            rolenames = [rolenames]
        roles_from = getattr(cls, "roles_from", None)
        if roles_from:
            # get roles from override
            with override_settings(ROLES_MODULE=roles_from):
                load_roles()
        else:
            # load standard roles
            load_roles()

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
