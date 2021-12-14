from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.conf import settings
from ...roles import registry, load_roles, BadRoleException


def _fuzzy_search(rolenames):
    fuzzy_rolenames = [
        name.lower().replace("-", " ").replace("_", " ") for name in rolenames
    ]

    def search(name):
        return (
            not rolenames
            or name in rolenames
            or name.lower().replace("-", " ").replace("_", " ") in fuzzy_rolenames
        )

    return search


def _standard_search(rolenames):
    def search(name):
        return not rolenames or name in rolenames

    return search


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("args", nargs="*", help="""Roles to setup""")
        parser.add_argument(
            "-c",
            "--clear",
            dest="clear",
            action="store_true",
            help="""Clear role/group permissions before setting defined ones""",
        )
        parser.add_argument(
            "-F",
            "--fuzzy",
            dest="fuzzy",
            action="store_true",
            help="""Enable role/group fuzzy equality (spaces, dash, underscore and case are ignored)""",
        )

    def handle(self, *rolenames, **options):
        clear = options.get("clear", False)
        fuzzy = options.get("fuzzy", False)
        if clear:
            self.stdout.write(
                self.style.NOTICE(
                    "Clear mode enabled, already bound permissions will be removed!"
                )
            )
        if fuzzy:
            check_name = _fuzzy_search(rolenames)
        else:
            check_name = _standard_search(rolenames)
        # assure roles are loaded
        load_roles()
        for name, role in registry.items():
            if check_name(name):
                self.stdout.write(f'Setting permissions for role "{name}"...')
                # istantiate role class
                role = role()
                try:
                    role.setup_permissions(clear)
                except BadRoleException as ex:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Unable to bound permission to "{name}" ({ex})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Role "{name}" setup completed!')
                    )
