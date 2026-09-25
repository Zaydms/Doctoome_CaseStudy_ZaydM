import duckdb

#overall questions related data
def question_performance(question_path):
    return duckdb.sql(f"""
        WITH last_question AS (
            SELECT session_id, MAX(question_number) AS last_reached
            FROM read_parquet('{question_path}')
            GROUP BY session_id
        )

        SELECT
            q.question_number,
            q.question_text,

            COUNT(*) AS reached,

            ROUND(
                100.0 * SUM(CASE WHEN q.answered THEN 1 ELSE 0 END)
                / COUNT(*), 2
            ) AS answer_rate,

            SUM(
                CASE
                    WHEN q.outcome_category IS NULL
                    AND q.question_number = l.last_reached
                    THEN 1 ELSE 0
                END
            ) AS dropouts,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN q.outcome_category IS NULL
                        AND q.question_number = l.last_reached
                        THEN 1 ELSE 0
                    END
                ) / COUNT(*), 2
            ) AS dropout_rate,

            ROUND(AVG(q.answer_time_seconds), 2) AS avg_response_seconds,
            MEDIAN(q.answer_time_seconds) AS median_response_seconds

        FROM read_parquet('{question_path}') q

        LEFT JOIN last_question l
            ON q.session_id = l.session_id

        GROUP BY q.question_number, q.question_text
        ORDER BY q.question_number
    """).df()

#les reponses pour chaque question de chaque categorie d'outcomes
def responses_by_outcome(question_path):
    return duckdb.sql(f"""
        SELECT
            question_number,
            answer_value,
            outcome_category,
            COUNT(*) AS responses,
            ROUND(
                100.0 * COUNT(*) /
                SUM(COUNT(*)) OVER (
                    PARTITION BY question_number, outcome_category
                ), 2
            ) AS percentage
        FROM read_parquet('{question_path}')
        WHERE answered = TRUE
          AND outcome_category IS NOT NULL
        GROUP BY question_number, answer_value, outcome_category
        ORDER BY outcome_category, question_number, percentage DESC
    """).df()

#number of answers with "prefer not to say" or "not sure"
def prefer_not_to_say(question_path):
    return duckdb.sql(f"""
        SELECT
            question_number,
            COUNT(*) AS total_responses,
            SUM(
                CASE WHEN LOWER(TRIM(answer_value))
                    IN ('prefer_not_to_say', 'not_sure')
                THEN 1 ELSE 0 END
            ) AS prefer_not_to_say_not_sure,

            ROUND(
                100.0 * SUM(
                    CASE WHEN LOWER(TRIM(answer_value))
                        IN ('prefer_not_to_say', 'not_sure')
                    THEN 1 ELSE 0 END
                ) / COUNT(*), 2
            ) AS percentage

        FROM read_parquet('{question_path}')
        WHERE answered = TRUE
        GROUP BY question_number
        ORDER BY question_number
    """).df()

#most frequent combination of answers before an abandon
def frequent_dropout_combinations(question_path):
    return duckdb.sql(f"""
        WITH abandoned AS (
            SELECT
                session_id,
                STRING_AGG(
                    'Q' || question_number || ': ' || answer_value,
                    ' | ' ORDER BY question_number
                ) AS answer_combination,
                COUNT(*) AS answered_questions,
                MAX(question_number) AS last_question
            FROM read_parquet('{question_path}')
            WHERE outcome_category IS NULL
              AND answered = TRUE
            GROUP BY session_id
        )

        SELECT
            answer_combination,
            answered_questions,
            last_question,
            COUNT(*) AS sessions,
            ROUND(
                100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2
            ) AS percentage
        FROM abandoned
        GROUP BY answer_combination, answered_questions, last_question
        ORDER BY sessions DESC
        LIMIT 20
    """).df()