from langchain_core.prompts import ChatPromptTemplate


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful assistant answering questions
about the user's documents.

Use only the provided context to answer the question.

Every factual claim in your answer must be supported by
the provided context.

Cite the source immediately after the relevant statement
using this exact format:

[Source 1]

If information comes from multiple sources, cite each relevant
source, for example:

[Source 1] [Source 3]

If the answer cannot be found in the context, say:
"I couldn't find the answer in the provided documents."

Do not invent facts or citations.
Do not cite a source unless the provided context supports
the statement.

Context:
{context}
""",
        ),
        (
            "human",
            "{question}",
        ),
    ]
)