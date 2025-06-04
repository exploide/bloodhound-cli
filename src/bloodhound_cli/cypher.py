import re


def escape(param):
    """Escapes and formats a parameter for inclusion in a Cypher query."""

    if isinstance(param, str):
        return param.replace("\\", "\\\\") \
                    .replace('"', '\\"') \
                    .replace("'", "\\'") \
                    .replace("`", "``")

    if isinstance(param, bool):
        return str(param).lower()

    if isinstance(param, list):
        escaped_list = []
        for x in param:
            if isinstance(x, str):
                escaped_list.append(f'"{escape(x)}"')
            else:
                escaped_list.append(f'{escape(x)}')
        return f"[{', '.join(escaped_list)}]"

    raise TypeError("Unsupported parameter type for a Cypher query.")


def _validate_node_name(name):
    """Validates if a string is suitable as a Cypher node name."""

    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]*", name):
        raise ValueError("Given node name is not valid.")


def node(name=None, label=None):
    """Construct a node with optional name and optional label."""

    result = ""
    if name is not None:
        _validate_node_name(name)
        result += name
    if label is not None:
        result += f":`{escape(label)}`"
    return result


def where(node_name, comparison_operator="=", boolean_operator="AND", **kwargs):
    """Construct WHERE clauses comparing properties of node as specified in kwargs."""

    if comparison_operator not in ["=", "IN"]:
        raise ValueError("Unsupported comparison operator for WHERE.")
    if boolean_operator not in ["AND", "OR"]:
        raise ValueError("Unsupported boolean operator for WHERE.")
    _validate_node_name(node_name)

    clauses = []
    for key, value in kwargs.items():
        if value is not None:
            escaped_key = escape(key)
            escaped_value = escape(value)
            if isinstance(value, str):
                clauses.append(f'{node_name}.`{escaped_key}` {comparison_operator} "{escaped_value}"')
            else:
                clauses.append(f'{node_name}.`{escaped_key}` {comparison_operator} {escaped_value}')

    if clauses:
        return "WHERE " + f" {boolean_operator} ".join(clauses)
    return ""
