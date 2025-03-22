from click import ParamType
from click.shell_completion import CompletionItem

from bloodhound_cli.api.exceptions import ApiException
from bloodhound_cli.api.from_config import api


class DomainType(ParamType):
    """ParamType for a domain name."""

    name = "domain"

    def shell_complete(self, ctx, param, incomplete):
        try:
            domains = sorted(d["name"] for d in api.domains(collected=True))
        except ApiException:
            return []
        return [
            CompletionItem(domain)
            for domain in domains if domain.lower().startswith(incomplete.lower())
        ]


class GroupType(ParamType):
    """ParamType for a group name."""

    name = "group"

    def shell_complete(self, ctx, param, incomplete):
        try:
            groups = sorted(g["label"] for g in api.groups())
        except ApiException:
            return []
        return [
            CompletionItem(group)
            for group in groups if group.lower().startswith(incomplete.lower())
        ]
