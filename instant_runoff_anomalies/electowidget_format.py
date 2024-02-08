"""
tools for dealing with Rob Lanphier's Electowidget format
specifically for the case of IRV elections
like the 2009 Burlington, Vermont mayoral election
https://electorama.com/electowidget/
https://electowiki.org/wiki/User:RobLa/Electowidget
"""

from collections import Counter
import json

from bs4 import BeautifulSoup

from rankings import IRVRankingWithPossibleEquality


def extract_ballot_counts_from_json_inside_html(
    webpage_html: str,
) -> Counter[IRVRankingWithPossibleEquality]:
    """
    https://electowiki.org/wiki/2009_Burlington,_Vermont_Mayoral_Election_data
    has a pre-formatted section with a JSON object that contains
    the counts of all rankings
    """
    soup = BeautifulSoup(webpage_html, "html.parser")
    preformatted_sections = soup.find_all("pre")
    assert len(preformatted_sections) == 1, "expect one preformatted section"
    election_data = json.loads("{" + preformatted_sections[0].string + "}")
    ballots = election_data["inline_ballots"]
    return Counter(
        {
            ranking_from_ratings(ballot_record["vote"]): ballot_record["qty"]
            for ballot_record in ballots
        }
    )


def ranking_from_ratings(ratings: dict[str, int]) -> IRVRankingWithPossibleEquality:
    """This format assigns bigger numbers to higher ranked candidates"""
    return tuple(
        frozenset(
            candidate for candidate in ratings if ratings[candidate] == this_rating
        )
        for this_rating in sorted(set(ratings.values()), reverse=True)
    )
