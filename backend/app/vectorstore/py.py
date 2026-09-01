from app.vectorstore.client import get_qdrant_client

client = get_qdrant_client()

result = client.scroll(
    collection_name="document_chunks",
    limit=100,
    with_payload=True,
)

points = result[0]

document_id = "8ca94487-7f24-462d-a60a-7f676c5f321e"

document_points = [
    point
    for point in points
    if point.payload.get("document_id") == document_id
]

print("Qdrant points:", len(document_points))

for point in document_points:
    print(
        point.id,
        point.payload
    )