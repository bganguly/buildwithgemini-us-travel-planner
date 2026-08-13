"""Retrieval tools for querying Vertex AI RAG Corpus (instructions.txt).

Corpus Resource: 'projects/313999655048/locations/us-central1/ragCorpora/3991359150222213120'
"""

import vertexai
from vertexai.preview import rag

PROJECT_ID = "qwiklabs-gcp-04-44a01d976633"
LOCATION = "us-central1"
CORPUS_NAME = "projects/313999655048/locations/us-central1/ragCorpora/3991359150222213120"


def consult_travel_instructions(query: str) -> str:
    """Consult the travel instructions and rules corpus (speed limits, travel hours, rules).

    Args:
        query: Question or query regarding travel instructions, speed limits, allowed hours, or restrictions.

    Returns:
        Matched passages from the travel instructions corpus document.
    """
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
    except Exception as e:
        return f"Retrieval failed: {e}"

    contexts = getattr(resp.contexts, "contexts", [])
    passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
    return "\n\n---\n\n".join(passages) or "No relevant passage found."
