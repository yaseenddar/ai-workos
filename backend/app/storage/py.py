from .minio import MinioStorage

storage = MinioStorage()
data = storage.download_file(
    "23aee910-ddf8-41ac-a25d-cfed61658639/documents/58c46a13-0a82-4235-95c1-ee8969e771fb.pdf"
)
print(len(data))