class BadRoleException(Exception):
    def __init__(self, message, permission):
        self.permission = permission
        super().__init__(message)
