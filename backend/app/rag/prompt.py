from langchain_core.prompts import ChatPromptTemplate


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful assistant answering questions
about the user's documents.

Use only the provided context to answer the question.

If the answer cannot be found in the context, say:
"I couldn't find the answer in the provided documents."

Do not invent facts or use outside knowledge.

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