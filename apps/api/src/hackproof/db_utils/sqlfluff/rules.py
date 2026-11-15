from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_Hackproof_CT01(BaseRule):
    """Enforce upper-case CREATE TYPE names."""

    name = "custom.create_type_upper"
    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"create_type_statement"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> LintResult | None:
        identifier = next(context.segment.recursive_crawl("data_type_identifier"), None)
        if identifier is None:
            return None

        raw = identifier.raw
        if raw == raw.upper():
            return None

        return LintResult(
            anchor=identifier,
            fixes=[LintFix.replace(identifier, [identifier.edit(raw.upper())])],
            description=f"CREATE TYPE names must be upper case: '{raw}' -> '{raw.upper()}'.",
        )
