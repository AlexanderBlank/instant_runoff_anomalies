from collections import Counter
from io import BytesIO
from pathlib import Path
import sys
import tomllib
from zipfile import ZipFile

import requests

SCRIPT_DIR = Path(__file__).parent
sys.path.append(str(SCRIPT_DIR.parent.resolve()))

from electowidget_format import (
    extract_ballot_counts_from_json_inside_html,
)
from voting_solutions_format import (
    extract_ballots_from_final_piles_report,
)


def main() -> int:
    with open(SCRIPT_DIR / "data_sources.toml", "rb") as data_sources_file:
        data_sources = tomllib.load(data_sources_file)

    raw_ballots_response = requests.get(data_sources["raw_ballots"]["web_url"])

    with ZipFile(BytesIO(raw_ballots_response.content), "r").open(
        "Reports/2009 Burlington Mayor Final Piles Report.txt"
    ) as final_piles_file:
        report_text = final_piles_file.read().decode("utf-8")
        counts_from_valid_raw_ballots = Counter(
            ballot.ranking
            for ballot in extract_ballots_from_final_piles_report(report_text)
            if ballot.is_valid
        )

    electowiki_text = requests.get(data_sources["electowiki"]["web_url"]).text

    unconverted_counts_from_electowiki = extract_ballot_counts_from_json_inside_html(
        electowiki_text
    )

    name_mapping = {
        "Kiss": "Bob Kiss",
        "Montroll": "Andy Montroll",
        "Simpson": "James Simpson",
        "Smith": "Dan Smith",
        "Wright": "Kurt Wright",
        "Write-in": "Write-in",
    }

    counts_from_electowiki = Counter(
        {
            tuple(
                frozenset(name_mapping[name] for name in candidate_set)
                for candidate_set in ranking
            ): count
            for ranking, count in unconverted_counts_from_electowiki.items()
        }
    )

    assert counts_from_valid_raw_ballots == counts_from_electowiki

    return 0


if __name__ == "__main__":
    sys.exit(main())
