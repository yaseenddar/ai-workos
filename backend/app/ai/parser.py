import fitz  # PyMuPDF


class PDFParser:

    def parse(self, pdf_bytes: bytes) -> list[dict]:
        """
        Returns one dictionary per page.
        """

        document = fitz.open(stream=pdf_bytes, filetype="pdf")

        pages = []

        try:
            for page_number, page in enumerate(document, start=1):
                pages.append(
                    {
                        "page_number": page_number,
                        "text": page.get_text("text").strip(),
                    }
                )

            return pages

        finally:
            document.close()