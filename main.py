import fitz  # PyMuPDF
import os


def split_pdf_by_pages(input_pdf_path, split_pages, output_folder="output_chunks"):
    """
    Splits a PDF file into multiple PDF files based on specific page split points.

    Args:
        input_pdf_path (str): The absolute path to the input PDF file.
        split_pages (list[int]): List of 1-indexed page numbers where to split (e.g., [21, 77, 117]).
                                 Chunks will be: 1 to split_pages[0], split_pages[0]+1 to split_pages[1], etc., up to the end.
        output_folder (str): The folder where the split PDF files will be saved.
    """
    print(f"Attempting to read PDF: {input_pdf_path}")
    try:
        doc = fitz.open(input_pdf_path)
        total_pages = len(doc)
        print(f"Total pages in input PDF: {total_pages}")
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return

    if total_pages == 0:
        print("Input PDF has no pages. Exiting.")
        return

    # Validate split_pages
    split_pages = sorted(set(split_pages))  # Remove duplicates, sort ascending
    if split_pages and (split_pages[0] < 1 or split_pages[-1] >= total_pages):
        print("Warning: Invalid split points (must be 1 <= page < total_pages). Adjusting...")
        split_pages = [p for p in split_pages if 1 <= p < total_pages]
    if not split_pages:
        print("No valid split points. Exiting.")
        doc.close()
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    # Define chunk ranges: add 0 as start and total_pages as end
    boundaries = [0] + split_pages + [total_pages]
    for chunk_idx in range(len(boundaries) - 1):
        start_page = boundaries[chunk_idx]  # 0-indexed
        end_page = boundaries[chunk_idx + 1]  # Exclusive end (0-indexed)

        if start_page >= end_page:
            continue  # Skip empty chunks

        print(f"Processing chunk from page {start_page + 1} to {end_page}")
        new_doc = fitz.open()  # New empty PDF
        new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)  # Insert range (0-indexed)

        output_pdf_path = os.path.join(output_folder, f"chunk_{start_page + 1}_to_{end_page}.pdf")
        print(f"Attempting to write to: {output_pdf_path}")
        try:
            new_doc.save(output_pdf_path)
            new_doc.close()
            print(f"Successfully wrote {output_pdf_path}")
        except Exception as e:
            print(f"Error writing PDF file {output_pdf_path}: {e}")
            new_doc.close()
            doc.close()  # Clean up
            return

    doc.close()
    print("All chunks processed successfully!")


if __name__ == "__main__":
    input_pdf = "pdf_to_split.pdf"
    num_prefix_pages = 29 # number of pages before the first chapter of the book (intro, preface, etc.)
    my_split_pages = list(map(lambda x: x + num_prefix_pages, [3, 21, 77, 117, 163, 201, 231, 253, 303, 341, 363, 397, 431, 487, 519, 561, 593, 657, 695, 743, 775, 835, 879, 907]))
    split_pdf_by_pages(input_pdf, my_split_pages)