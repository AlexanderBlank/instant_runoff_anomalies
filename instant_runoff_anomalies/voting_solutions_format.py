"""
tools for dealing with data from Voting Solutions
votingsolutions.com
This is what was used for the 2009 Burlington, Vermont mayoral election
and i've so far only looked at that election.
"""

import dataclasses
import itertools
import operator
import re

from rankings import IRVRankingWithPossibleEquality


@dataclasses.dataclass(frozen=True)
class Ballot:
    identifier: str
    """corresponds to what looks like a ballot identifier in the file"""

    ranking: IRVRankingWithPossibleEquality
    """
    In the 2009 Burlington, Vermont mayoral election data,
    6 ballots contain an equal ranking of 2 candidates,
    and no ballots contain an equal ranking of more than 2 candidates.
    None of the equal rankings ended up affecting the election.
    I'm not sure what the rules are for how these ballots are treated.
    """

    is_valid: bool
    """
    It's not clear to me if all 4 of the invalid ballots
    in the 2009 Burlington, Vermont mayoral election data
    are considered invalid because they truly had an empty ranking
    or if the ballots were invalid in some other way
    and were therefore treated as empty.
    I doubt i'll be able to find raw enough data to find out
    and it seems the rule in this election was to exclude those 4 ballots.
    """


def extract_ballots_from_final_piles_report(report_text: str) -> list[Ballot]:
    """
    At least from the data i got from the archive of
    the 2009 Burlington, Vermont mayoral election data,
    this is the only file in the Reports folder
    that contains every ballot in the election.
    So this is the file we look at to get raw ballot data.
    """

    # File consists of sections separated by blank lines
    # Get rid of occurrences of multiple blank lines

    windows_line_ending = "\r\n"
    sections_including_comments = [
        [line for line in section.splitlines() if line and not line.isspace()]
        for section in report_text.split(windows_line_ending + windows_line_ending)
    ]

    # TODO tolerate case of zero invalid ballots if that's formatted differently
    assert sections_including_comments[-1][0] == "# INVALID BALLOTS"
    # This is a comment, which can't really be counted on
    # but there's not an actual section header indicating
    # the invalid ballots section.
    # I imagine that what really matters is the second column
    # being 0 instead of 1 or the ranking being empty.
    # I don't know what the 0 or 1 column means other than
    # that it's 1 for all valid ballots in the one file i've
    # looked at and 0 for all invalid ballots.
    # This is the only comment we look at. Ignore the rest.

    sections_stripped_of_comments = [
        [line for line in section if not line.startswith("#")]
        for section in sections_including_comments
    ]

    # Remove empty sections (e.g., that were entirely comments)
    sections = [section for section in sections_stripped_of_comments if section]

    candidate_sections = [
        section
        for section in sections
        if any(line.startswith(CANDIDATE_DEFINITION_PREFIX) for line in section)
    ]
    assert (
        len(candidate_sections) == 1
    ), "expected all candidate defintions in one section"

    candidate_names_from_id = dict(
        parse_candidate_mapping(line) for line in candidate_sections[0]
    )

    final_pile_sections = [
        section for section in sections if section[0].startswith(FINAL_PILE_PREFIX)
    ]

    assert len(final_pile_sections) >= 1

    non_final_pile_sections = [
        section for section in sections if not section[0].startswith(FINAL_PILE_PREFIX)
    ]

    assert not any(
        section
        for section in non_final_pile_sections
        if any(VALID_BALLOT_PREFIX_REGEX.match(line) for line in section)
    ), "unexpected valid ballot outside of the final pile section"

    assert not any(
        section
        for section in sections[:-1]
        if any(INVALID_BALLOT_PREFIX_REGEX.match(line) for line in section)
    ), "unexpected invalid ballot outside of the last section"

    results = list(
        itertools.chain(
            parse_valid_ballot(line, candidate_names_from_id)
            for section in final_pile_sections
            for line in section[1:]
        )
    ) + [parse_invalid_ballot(line) for line in sections[-1]]

    assert len(results) >= 1
    assert len({ballot.identifier for ballot in results}) == len(
        results
    ), "ids not unique"
    return sorted(results, key=operator.attrgetter("identifier"))


FINAL_PILE_PREFIX = ".FINAL-PILE "
CANDIDATE_DEFINITION_PREFIX = ".CANDIDATE "
VALID_BALLOT_PREFIX_REGEX = re.compile(r"^\d\d\d\d\d\d-\d\d-\d\d\d\d, 1\) ")
INVALID_BALLOT_PREFIX_REGEX = re.compile(r"^\d\d\d\d\d\d-\d\d-\d\d\d\d, 0\) ")


def parse_candidate_mapping(line: str) -> tuple[str, str]:
    assert line.startswith(CANDIDATE_DEFINITION_PREFIX)
    left, right = line[len(CANDIDATE_DEFINITION_PREFIX) :].split(", ", maxsplit=1)
    assert right.startswith('"') and right.endswith('"'), "expected quoted name"
    return left, right[1:-1]


def parse_valid_ballot(line: str, candidate_map: dict[str, str]) -> Ballot:
    match = VALID_BALLOT_PREFIX_REGEX.match(line)
    assert match

    ranking = tuple(
        frozenset(candidate_map[cand_id] for cand_id in cand_set_string.split("="))
        for cand_set_string in line[match.span()[1] :].split(",")
    )

    assert all(len(candidate_set) >= 1 for candidate_set in ranking)
    assert len(ranking) >= 1, f"no votes in {line=}"
    assert len(frozenset.union(*ranking)) == sum(
        len(candidate_set) for candidate_set in ranking
    ), f"duplicate vote in {line=}"

    return Ballot(
        identifier=line[: len("000000-00-0000")],
        ranking=ranking,
        is_valid=True,
    )


def parse_invalid_ballot(line: str) -> Ballot:
    match = INVALID_BALLOT_PREFIX_REGEX.match(line)
    assert match
    assert match.span()[1] == len(line), f"unexpected data for invalid ballot {line=}"
    return Ballot(
        identifier=line[: len("000000-00-0000")],
        ranking=tuple(),
        is_valid=False,
    )
