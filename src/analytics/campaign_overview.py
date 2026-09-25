import duckdb

#Listing a complete campaign overview
def get_campaign_overview(session_path):
    return duckdb.sql(f"""
        SELECT
            COUNT(DISTINCT visitor_id) AS unique_visitors,
            COUNT(DISTINCT session_id) AS total_sessions,

            SUM(
                CASE WHEN started THEN 1 ELSE 0 END
            ) AS started_questionnaires,

            SUM(
                CASE WHEN completed THEN 1 ELSE 0 END
            ) AS completed_questionnaires,

            ROUND(
                100.0 *
                SUM(CASE WHEN completed THEN 1 ELSE 0 END)
                /
                NULLIF(
                    SUM(CASE WHEN started THEN 1 ELSE 0 END),
                    0
                ),
                2
            ) AS completion_rate,

            COUNT(
                DISTINCT CASE
                    WHEN is_returning_visitor THEN visitor_id
                END
            ) AS returning_visitors

        FROM read_parquet('{session_path}')
    """).df()

#Outcome distribution
def get_outcome_distribution(session_path):
    return duckdb.sql(f"""
        SELECT
            outcome_category,
            COUNT(*) AS total,

            ROUND(
                100.0 * COUNT(*)
                / SUM(COUNT(*)) OVER (),
                2
            ) AS percentage

        FROM read_parquet('{session_path}')

        WHERE outcome_category IS NOT NULL

        GROUP BY outcome_category
        ORDER BY total DESC
    """).df()

#Rate at which visitors start sessions
def get_visitor_start_rate(session_path):
    return duckdb.sql(f"""
        SELECT
            COUNT(DISTINCT CASE WHEN started THEN visitor_id END) AS visitors_started,
            ROUND(
                100.0 * COUNT(DISTINCT CASE WHEN started THEN visitor_id END)
                / COUNT(DISTINCT visitor_id), 2
            ) AS visitor_start_rate
        FROM read_parquet('{session_path}')
    """).df()
