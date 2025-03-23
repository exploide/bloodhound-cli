from click import ParamType
from click.shell_completion import CompletionItem

from bloodhound_cli.api.exceptions import ApiException
from bloodhound_cli.api.from_config import api


class AssetGroupTagType(ParamType):
    """ParamType for an asset group tag."""

    name = "asset_group_tag"

    def shell_complete(self, ctx, param, incomplete):
        try:
            asset_groups = [
                ag
                for ag in api.get_asset_groups()
                if ag["tag"].startswith(incomplete)
            ]
        except ApiException:
            return []
        return [
            CompletionItem(ag["tag"], help=ag["name"])
            for ag in sorted(asset_groups, key=lambda g: g["tag"])
        ]


class DomainType(ParamType):
    """ParamType for a domain name."""

    name = "domain"

    def shell_complete(self, ctx, param, incomplete):
        try:
            domains = [
                domain["name"]
                for domain in api.domains(collected=True)
                if domain["name"].lower().startswith(incomplete.lower())
            ]
        except ApiException:
            return []
        return [
            CompletionItem(domain)
            for domain in sorted(domains)
        ]


class GroupType(ParamType):
    """ParamType for a group name."""

    name = "group"

    def shell_complete(self, ctx, param, incomplete):
        try:
            groups = [
                group["label"]
                for group in api.groups()
                if group["label"].lower().startswith(incomplete.lower())
            ]
        except ApiException:
            return []
        return [
            CompletionItem(group)
            for group in sorted(groups)
        ]
