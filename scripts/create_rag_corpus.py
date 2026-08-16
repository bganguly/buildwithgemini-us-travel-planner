"""Script to create a Serverless Vertex AI RAG Corpus and index instructions.txt.

Project ID: 'qwiklabs-gcp-04-44a01d976633'
Location: 'us-central1'
"""

import sys
import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-04-44a01d976633"
LOCATION = "us-central1"
GCS_PATH = "gs://us-travel-planner-media-qwiklabs-04/rag/instructions.txt"

PARSING_PROMPT = (
    "Extract all travel guidelines, speed limits, operating hours, and travel restrictions described in this text. "
    "Output clean, self-contained rules."
)


def create_corpus():
    print(f"Initializing Vertex AI RAG in {LOCATION} for project {PROJECT_ID}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Switch region's RAG managed DB to serverless mode
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    try:
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg,
                rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
            )
        )
        print("Updated RAG Engine Config to Serverless mode.")
    except Exception as e:
        print("Note updating ragEngineConfig:", e)

    # 2. Create the corpus
    print("Creating serverless RAG corpus 'travel-instructions-corpus'...")
    corpus = rag.create_corpus(
        display_name="travel-instructions-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    corpus_name = corpus.name
    print(f"CREATED_CORPUS_NAME: {corpus_name}")

    # 3. Import + parse + chunk + embed
    print(f"Importing files from {GCS_PATH}...")
    resp = rag.import_files(
        corpus_name=corpus_name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-3.6-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print("Import response:", resp)
    print(f"Imported count: {getattr(resp, 'imported_rag_files_count', None)}")

    with open("rag_corpus_name.txt", "w") as f:
        f.write(corpus_name)
    print(f"Saved corpus name to rag_corpus_name.txt: {corpus_name}")


if __name__ == "__main__":
    create_corpus()
