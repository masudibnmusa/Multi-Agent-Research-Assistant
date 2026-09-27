TASK_DECOMPOSITION_PROMPT = """You are a research planning assistant.

Break the following research question into at most {max_sub_questions} specific,
independently searchable sub-questions.

Question: {query}

Respond ONLY with JSON in this exact shape:
{{"sub_questions": ["...", "..."]}}
"""

SUMMARIZE_PROMPT = """Summarize the key points relevant to this sub-question, using
only the information in the provided sources. Write concise bullet points.
Do not include information not present in the sources.

Sub-question: {sub_question}

Sources:
{sources}
"""

FACTCHECK_PROMPT = """Determine whether the following claim is supported by the
provided sources.

Claim: {claim}

Sources:
{sources}

Respond with exactly one word: "supported", "contradicted", or "unsupported".
"""