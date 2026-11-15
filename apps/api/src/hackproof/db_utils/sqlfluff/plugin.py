from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules import BaseRule


@hookimpl
def get_rules() -> list[type[BaseRule]]:
    from hackproof.db_utils.sqlfluff.rules import Rule_Hackproof_CT01

    return [Rule_Hackproof_CT01]
