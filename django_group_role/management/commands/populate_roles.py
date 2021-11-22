from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.conf import settings
from ...roles import registry, load_roles, BadRoleException


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            nargs="*",
            help="""Roles to setup""",
        )
        parser.add_argument(
            "-c",
            "--clear",
            dest="clear",
            action="store_true",
            help="""Clear role/group permissions before setting defined ones""",
        )

    def handle(self, *rolenames, **options):
        clear = options.get("clear", False)
        if clear:
            self.stdout.write(
                self.style.NOTICE(
                    "Clear mode enabled, already bound permissions will be removed!"
                )
            )
        # assure roles are loaded
        load_roles()
        for name, role in registry.items():
            if not rolenames or name in rolenames:
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
