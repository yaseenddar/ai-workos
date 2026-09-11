from app.reranking.provider.cross_encoder import CrossEncoderReranker

reranker = CrossEncoderReranker()

documents = [
    "The developer has two years of professional experience.",
    "React is a JavaScript library for building user interfaces.",
    "SecurePay is a fraud-aware payment platform.",
]

ranked = reranker.rerank(
    query="How many years of experience does the developer have?",
    documents=documents,
)

print(ranked)