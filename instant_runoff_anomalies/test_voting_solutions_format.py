import pytest

from voting_solutions_format import (
    parse_candidate_mapping,
    parse_valid_ballot,
    parse_invalid_ballot,
)


@pytest.mark.parametrize(
    "line,id,name", [('.CANDIDATE C06, "Write-in"', "C06", "Write-in")]
)
def test_parse_candidate_mapping(line: str, id: str, name: str) -> None:
    assert parse_candidate_mapping(line) == (id, name)


@pytest.fixture
def candidate_mapping() -> dict[str, str]:
    return {"C01": "Kim Jong Un", "C02": "Dua Lipa", "C03": "Trip Tucker"}


@pytest.mark.parametrize(
    "line,identifier,ranking",
    [
        (
            "000001-00-0123, 1) C02,C01,C03",
            "000001-00-0123",
            ({"Dua Lipa"}, {"Kim Jong Un"}, {"Trip Tucker"}),
        ),
        (
            "000002-00-0456, 1) C03,C02",
            "000002-00-0456",
            ({"Trip Tucker"}, {"Dua Lipa"}),
        ),
        pytest.param(
            "000002-00-0456, 1) C03=C02",
            "000002-00-0456",
            ({"Dua Lipa", "Trip Tucker"},),
            id="two_equal",
        ),
        pytest.param(
            "000002-00-0456, 1) C01=C02,C03",
            "000002-00-0456",
            ({"Kim Jong Un", "Dua Lipa"}, {"Trip Tucker"}),
            id="equal_first",
        ),
        pytest.param(
            "000002-00-0456, 1) C03,C01=C02",
            "000002-00-0456",
            ({"Trip Tucker"}, {"Kim Jong Un", "Dua Lipa"}),
            id="equal_last",
        ),
        pytest.param(
            "000002-00-0456, 1) C01=C02=C03",
            "000002-00-0456",
            ({"Kim Jong Un", "Dua Lipa", "Trip Tucker"},),
            id="all_equal",
        ),
        pytest.param(
            "000003-00-0789, 1) C01",
            "000003-00-0789",
            ({"Kim Jong Un"},),
            id="bullet_vote",
        ),
    ],
)
def test_parse_valid_ballot(
    line: str, identifier: str, ranking: tuple[str, ...], candidate_mapping
) -> None:
    ballot = parse_valid_ballot(line, candidate_mapping)
    assert ballot.identifier == identifier
    assert ballot.ranking == ranking
    assert ballot.is_valid


@pytest.mark.parametrize(
    "line,id",
    [("000002-00-0456, 0) ", "000002-00-0456")],
)
def test_parse_invalid_ballot(line: str, id: str) -> None:
    ballot = parse_invalid_ballot(line)
    assert ballot.identifier == id
    assert not ballot.is_valid
