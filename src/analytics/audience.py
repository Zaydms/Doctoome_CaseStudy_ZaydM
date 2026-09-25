import duckdb

#classifying outcomes by age groups
def outcome_by_age(session_path):
    return duckdb.sql(f"""
        SELECT
            CASE
                WHEN age < 25 THEN '16-24'
                WHEN age < 35 THEN '25-34'
                WHEN age < 45 THEN '35-44'
                WHEN age < 55 THEN '45-54'
                WHEN age < 65 THEN '55-64'
                ELSE '65+'
            END AS age_group,
            outcome_category,
            COUNT(*) AS total,
            ROUND(100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (PARTITION BY age_group), 2) AS percentage
        FROM read_parquet('{session_path}')
        WHERE outcome_category IS NOT NULL AND age IS NOT NULL
        GROUP BY age_group, outcome_category
        ORDER BY age_group, total DESC
    """).df()

#classifying outcomes by genders
def outcome_by_gender(session_path):
    return duckdb.sql(f"""
        SELECT gender, outcome_category, COUNT(*) AS total,
            ROUND(100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (PARTITION BY gender), 2) AS percentage
        FROM read_parquet('{session_path}')
        WHERE outcome_category IS NOT NULL
        GROUP BY gender, outcome_category
        ORDER BY gender, total DESC
    """).df()

#classifying outcomes by regions
def outcome_by_region(session_path):
    return duckdb.sql(f"""
        SELECT region, outcome_category, COUNT(*) AS total,
            ROUND(100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (PARTITION BY region), 2) AS percentage
        FROM read_parquet('{session_path}')
        WHERE outcome_category IS NOT NULL
        GROUP BY region, outcome_category
        ORDER BY region, total DESC
    """).df()

#cassifying outcomes by averages and medians
def age_by_outcome(session_path):
    return duckdb.sql(f"""
        SELECT outcome_category,
            ROUND(AVG(age), 1) AS average_age,
            MEDIAN(age) AS median_age
        FROM read_parquet('{session_path}')
        WHERE outcome_category IS NOT NULL AND age IS NOT NULL
        GROUP BY outcome_category
    """).df()

#classifying the number of missing demographics in the visitors data
def missing_demographics(visitor_path):
    return duckdb.sql(f"""
        SELECT
            SUM(age IS NULL)::INT AS missing_age,
            SUM(gender = 'not provided')::INT AS missing_gender,
            SUM(region = 'not provided')::INT AS missing_region
        FROM read_parquet('{visitor_path}')
    """).df()

#classifying regions by ages
def median_age_by_region(session_path):
    return duckdb.sql(f"""
        SELECT
            region,
            MEDIAN(age) AS median_age
        FROM read_parquet('{session_path}')
        WHERE age IS NOT NULL
        GROUP BY region
        ORDER BY median_age DESC
    """).df()

#classifying the number of visitors by age groups
def visitors_by_age_group(visitor_path):
    return duckdb.sql(f"""
        SELECT age_group, COUNT(*) AS visitors
        FROM read_parquet('{visitor_path}')
        WHERE age_group <> 'not provided'
        GROUP BY age_group
        ORDER BY visitors DESC
    """).df()

#classifying the number of completed sessions by age groups
def completed_sessions_by_age(visitor_path):
    return duckdb.sql(f"""
        SELECT
            age_group,
            COUNT(*) AS visitors,
            SUM(completed_sessions) AS completed_sessions,
            ROUND(AVG(completed_sessions), 2) AS avg_completed_per_visitor
        FROM read_parquet('{visitor_path}')
        WHERE age_group <> 'not provided'
        GROUP BY age_group
        ORDER BY avg_completed_per_visitor DESC
    """).df()

#classifying the regions by gender percentages
def gender_by_region(visitor_path):
    return duckdb.sql(f"""
        SELECT
            region,
            gender,
            COUNT(*) AS visitors,
            ROUND(
                100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (PARTITION BY region), 2
            ) AS percentage
        FROM read_parquet('{visitor_path}')
        GROUP BY region, gender
        ORDER BY region, visitors DESC
    """).df()

#classifying outcomes by age and start time
def outcomes_by_age_and_time(session_path):
    return duckdb.sql(f"""
        WITH data AS (
            SELECT
                CASE
                    WHEN age < 25 THEN '16-24'
                    WHEN age < 35 THEN '25-34'
                    WHEN age < 45 THEN '35-44'
                    WHEN age < 55 THEN '45-54'
                    WHEN age < 65 THEN '55-64'
                    ELSE '65+'
                END AS age_group,

                CASE
                    WHEN HOUR(session_started_at) >= 5 AND HOUR(session_started_at) < 10 THEN 'Morning'
                    WHEN HOUR(session_started_at) >= 10 AND HOUR(session_started_at) < 16 THEN 'Day'
                    WHEN HOUR(session_started_at) >= 16 AND HOUR(session_started_at) < 22 THEN 'Afternoon'
                    WHEN HOUR(session_started_at) >= 22 THEN 'Night'
                    ELSE 'Late Night'
                END AS session_period,

                outcome_category

            FROM read_parquet('{session_path}')
            WHERE age IS NOT NULL
              AND outcome_category IS NOT NULL
        )

        SELECT
            age_group,
            session_period,
            outcome_category,
            COUNT(*) AS total_sessions,

            ROUND(
                100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (
                    PARTITION BY age_group, session_period
                ), 2
            ) AS percentage

        FROM data
        GROUP BY age_group, session_period, outcome_category
        ORDER BY age_group, session_period, percentage DESC
    """).df()