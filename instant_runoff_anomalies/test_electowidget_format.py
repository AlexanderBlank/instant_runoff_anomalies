import pytest

from electowidget_format import (
    ranking_from_ratings,
    IRVRankingWithPossibleEquality,
)


@pytest.mark.parametrize(
    "ratings,ranking",
    [
        ({}, tuple()),
        ({"a": 3}, ({"a"},)),
        ({"a": 0, "b": 1}, ({"b"}, {"a"})),
        ({"a": 5, "b": 4}, ({"a"}, {"b"})),
        ({"a": 5, "b": 5}, ({"a", "b"},)),
        ({"a": 5, "b": 5, "c": 3}, ({"a", "b"}, {"c"})),
        ({"a": 5, "b": 5, "c": 8}, ({"c"}, {"a", "b"})),
        ({"a": 5, "b": 5, "c": 8, "d": 5}, ({"c"}, {"a", "b", "d"})),
    ],
)
def test_ranking_from_ratings(
    ratings: dict[str, int], ranking: IRVRankingWithPossibleEquality
) -> None:
    assert ranking_from_ratings(ratings) == ranking
