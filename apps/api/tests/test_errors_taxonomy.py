from stellar_sdk import xdr

from hackproof.errors import get_soroban_errors


def test_every_parser_result_code_has_entry():
    """Acceptance criteria:
    Every result code the parser can emit has an entry, enforced by a test.
    """
    errors = get_soroban_errors()
    codes_in_yaml = {e.code for e in errors}

    # All invoke host function failure codes
    invoke_codes = {
        item.name.removeprefix("INVOKE_HOST_FUNCTION_")
        for item in xdr.InvokeHostFunctionResultCode
        if item != xdr.InvokeHostFunctionResultCode.INVOKE_HOST_FUNCTION_SUCCESS
    }

    # Codes seen in HackMeridian 2026 as mentioned in issue spec
    known_meridian_codes = {
        "TRAPPED",
        "INSUFFICIENT_REFUNDABLE_FEE",
        "RESOURCE_LIMIT_EXCEEDED",
        "ENTRY_ARCHIVED",
    }

    assert known_meridian_codes.issubset(codes_in_yaml)
    assert invoke_codes.issubset(codes_in_yaml)


def test_errors_fields_and_documentation():
    errors = get_soroban_errors()
    assert len(errors) > 0

    for err in errors:
        assert err.code.isupper(), f"Error code {err.code} should be uppercase"
        assert len(err.category) > 0
        assert len(err.plain_english) > 10
        assert len(err.common_cause) > 10
        assert len(err.fix) > 10
        assert err.docs_url.startswith("https://")
