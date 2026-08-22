import fitz


class PDFParser:

    @staticmethod
    def extract_pages(pdf_bytes: bytes):

        document = fitz.open(stream=pdf_bytes, filetype="pdf")

        pages = []

        for index, page in enumerate(document):

            text = page.get_text("text").strip()

            pages.append(
                {
                    "page": index + 1,
                    "text": text,
                }
            )

        document.close()

        return pages