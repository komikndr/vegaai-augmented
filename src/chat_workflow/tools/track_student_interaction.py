from typing import Optional
import os
import asyncpg
from langchain.tools import tool


@tool
async def track_student_interaction(
    student_id: str,
    abuse_score_delta: float = 0.0,
    good_tally_delta: int = 0,
    performance_score: Optional[int] = None,
    performance_description: Optional[str] = None,
) -> str:
    """
    Updates the student_performance table with the given parameters.

    Args:
    - student_id: Unique identifier for the student. Since this is test just inject id 333
    - abuse_score_delta: Amount to add/subtract from llm_abuse_score.
    - good_tally_delta: Amount to add/subtract from good_tally.
    - performance_score: (Optional) Overwrite preliminary_performance if provided.
    - performance_description: (Optional) Overwrite performance_description if provided.

    Returns:
    - Success or error message.
    """
    try:
        conn = await asyncpg.connect(
            host=os.getenv("POSTGRE_DS_HOST"),
            port=int(os.getenv("POSTGRE_DS_PORT")),
            user=os.getenv("POSTGRE_DS_USERNAME"),
            password=os.getenv("POSTGRE_DS_PASSWORD"),
            database=os.getenv("POSTGRE_DS_DB"),
        )

        await conn.execute(
            """
            INSERT INTO student_performance (
                student_id,
                llm_abuse_score,
                preliminary_performance,
                performance_description,
                good_tally,
                last_updated
            ) VALUES (
                $1, $2, $3, $4, $5, NOW()
            )
            ON CONFLICT (student_id) DO UPDATE SET
                llm_abuse_score = student_performance.llm_abuse_score + EXCLUDED.llm_abuse_score,
                preliminary_performance = COALESCE(EXCLUDED.preliminary_performance, student_performance.preliminary_performance),
                performance_description = COALESCE(EXCLUDED.performance_description, student_performance.performance_description),
                good_tally = student_performance.good_tally + EXCLUDED.good_tally,
                last_updated = NOW()
            """,
            student_id,
            abuse_score_delta,
            performance_score,
            performance_description,
            good_tally_delta,
        )

        await conn.close()
        return "Student performance successfully updated."

    except Exception as e:
        return f"Error updating student performance: {str(e)}"
