##Script to detect inconsistent visitors based on their outcomes.
def find_inconsistent_visitors(outcomes):
    diagnosed = outcomes[outcomes["outcome_category"] == "declared_diagnosed"]
    later = outcomes[outcomes["outcome_category"].isin(
        ["possible_risk", "no_current_indication"]
    )]

    bad = diagnosed.merge(later, on="visitor_id", suffixes=("_before", "_after"))
    bad = bad[bad["completed_at_after"] > bad["completed_at_before"]]

    return bad["visitor_id"].unique()
##Script to remove inconsistent visitors and their associated sessions, events, answers, and outcomes.
def remove_inconsistent_visitors(visitors, sessions, events, answers, outcomes, bad_ids):
    bad_sessions = sessions.loc[sessions["visitor_id"].isin(bad_ids), "session_id"]

    visitors = visitors[~visitors["visitor_id"].isin(bad_ids)]
    sessions = sessions[~sessions["visitor_id"].isin(bad_ids)]
    events = events[~events["session_id"].isin(bad_sessions)]
    answers = answers[~answers["session_id"].isin(bad_sessions)]
    outcomes = outcomes[~outcomes["session_id"].isin(bad_sessions)]

    return visitors, sessions, events, answers, outcomes