from enum import IntEnum


class RID(IntEnum):
    """Well-known RID constants."""

    GUEST = 501
    DOMAIN_ADMINS = 512
    DOMAIN_USERS = 513
    DOMAIN_COMPUTERS = 515
    DOMAIN_CONTROLLERS = 516
    PROTECTED_USERS = 525
