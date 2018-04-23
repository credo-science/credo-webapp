class CredoAPIException(Exception):
    pass


class ValidationException(CredoAPIException):
    pass


class RegistrationException(CredoAPIException):
    pass


class LoginException(CredoAPIException):
    pass
