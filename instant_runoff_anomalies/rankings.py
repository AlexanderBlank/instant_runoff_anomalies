"""definitions of types of candidate rankings"""

IRVRankingWithPossibleEquality = tuple[frozenset[str], ...]
"""
The first element is the first-ranked set of candidates,
second element is the set of candidates ranked after the first set
of candidates, etc.
This ballot format allows for a voter to specify equal preference
between multiple candidates.
In the future, i might replace this with a class that does some useful things.
"""
