import shutil
import glob
from backend.rag_pipeline import ingest_pdf

shutil.rmtree('faiss_index', ignore_errors=True)
print("Old FAISS index deleted.")

pdfs = glob.glob('data/*.pdf')
print(f"Found {len(pdfs)} PDFs to ingest...")

for pdf in pdfs:
    try:
        print(f"Ingesting: {pdf}")
        chunks = ingest_pdf(pdf)
        print(f"  -> {chunks} chunks")
    except Exception as e:
        print(f"  -> Skipped {pdf}: {e}")

print("\nDone! FAISS index rebuilt successfully!")
