import duckdb

#campaign performance
def performance_by(session_path, dimension):
    return duckdb.sql(f"""
        SELECT
            {dimension},
            COUNT(*) AS sessions,
            SUM(CASE WHEN started THEN 1 ELSE 0 END) AS started,
            SUM(CASE WHEN completed THEN 1 ELSE 0 END) AS completed,

            ROUND(
                100.0 * SUM(CASE WHEN completed THEN 1 ELSE 0 END)
                / NULLIF(SUM(CASE WHEN started THEN 1 ELSE 0 END), 0), 2
            ) AS completion_rate,

            ROUND(
                100.0 * SUM(CASE WHEN started AND NOT completed THEN 1 ELSE 0 END)
                / NULLIF(SUM(CASE WHEN started THEN 1 ELSE 0 END), 0), 2
            ) AS dropout_rate

        FROM read_parquet('{session_path}')
        GROUP BY {dimension}
        ORDER BY sessions DESC
    """).df()

#outcomes by campaigns
def outcomes_by(session_path, dimension):
    return duckdb.sql(f"""
        SELECT
            {dimension},
            outcome_category,
            COUNT(*) AS total,

            ROUND(
                100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (PARTITION BY {dimension}), 2
            ) AS percentage

        FROM read_parquet('{session_path}')
        WHERE outcome_category IS NOT NULL

        GROUP BY {dimension}, outcome_category
        ORDER BY {dimension}, total DESC
    """).df()

#age by campaign
def age_by_campaign(session_path):
    return duckdb.sql(f"""
        SELECT
            campaign_name,
            ROUND(AVG(age), 1) AS average_age,
            MEDIAN(age) AS median_age,
            COUNT(*) AS sessions
        FROM read_parquet('{session_path}')
        WHERE age IS NOT NULL
        GROUP BY campaign_name
        ORDER BY median_age DESC
    """).df()

#classifying sources by devices used
def device_by_source(session_path):
    return duckdb.sql(f"""
        SELECT
            device_type,
            acquisition_source,
            COUNT(*) AS sessions,

            ROUND(
                100.0 * SUM(CASE WHEN completed THEN 1 ELSE 0 END) /
                NULLIF(SUM(CASE WHEN started THEN 1 ELSE 0 END), 0), 2
            ) AS completion_rate

        FROM read_parquet('{session_path}')
        GROUP BY device_type, acquisition_source
        ORDER BY acquisition_source, sessions DESC
    """).df()

#outcomes by devices used
def outcomes_by_device(session_path):
    return duckdb.sql(f"""
        SELECT
            device_type,
            outcome_category,
            COUNT(*) AS total,
            ROUND(
                100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (PARTITION BY device_type), 2
            ) AS percentage
        FROM read_parquet('{session_path}')
        WHERE outcome_category IS NOT NULL
        GROUP BY device_type, outcome_category
        ORDER BY device_type, percentage DESC
    """).df()

#evolution of outcomes by time
def monthly_outcome_evolution(session_path):
    return duckdb.sql(f"""
        SELECT
            STRFTIME(session_started_at, '%Y-%m') AS month,
            outcome_category,
            COUNT(*) AS total,
            ROUND(
                100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (
                    PARTITION BY STRFTIME(session_started_at, '%Y-%m')
                ), 2
            ) AS percentage
        FROM read_parquet('{session_path}')
        WHERE outcome_category IS NOT NULL
        GROUP BY month, outcome_category
        ORDER BY month, outcome_category
    """).df()

#number of sessions per month
def monthly_session_evolution(session_path):
    return duckdb.sql(f"""
        SELECT
            STRFTIME(session_started_at, '%Y-%m') AS month,
            COUNT(*) AS sessions,
            COUNT(DISTINCT visitor_id) AS unique_visitors
        FROM read_parquet('{session_path}')
        GROUP BY month
        ORDER BY month
    """).df()