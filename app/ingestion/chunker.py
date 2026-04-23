import uuid
from app.utils.logger import get_structured_logger
from app.config.settings import app_settings

logger = get_structured_logger(__name__)

class TextChunker:
    def __init__(self):
        self.chunk_size = app_settings.CHUNK_SIZE
        self.chunk_overlap= app_settings.CHUNK_OVERLAP
    
    def chunk_text(self, text: str):
        chunks = []
        current_chunk = ""
        paragraphs = text.split("\n\n")
        
        for textpara in paragraphs:
            textpara = textpara.strip()
            if not textpara:
                continue
            
            if len(current_chunk) + len(textpara) + 2 <= self.chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + textpara
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = current_chunk[-self.chunk_overlap:] + "\n\n" + textpara
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def chunk_documents(self, doc_data: dict, filename: str):
        all_chunks = []
        if doc_data.get("text"):
            text_pieces = self.chunk_text(doc_data["text"])
            for piece in text_pieces:
                chunk_id = str(uuid.uuid4())
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "content": piece,
                    "metadata": {
                        "source": filename,
                        "type": "paragraph",
                        "chunk_id": chunk_id,
                        "content": piece[:20000]
                    }
                })
        
        # Adding Table and images
        for table in doc_data.get("tables", []):
            chunk_id = str(uuid.uuid4())
            all_chunks.append({
                "chunk_id": chunk_id,
                "content": table["content"],
                "metadata": {
                    "source": filename,
                    "page": table["metadata"].get("page"),
                    "type": "table",
                    "chunk_id": chunk_id,
                    "content": table["content"][:20000]
                }
            })
            
        for image in doc_data.get("images", []):
            chunk_id = str(uuid.uuid4())
            all_chunks.append({
                "chunk_id": chunk_id,
                "content": image["content"],
                "metadata": {
                    "source": filename,
                    "page": image["metadata"].get("page"),
                    "type": "image",
                    "chunk_id": chunk_id,
                    "content": image["content"][:20000]
                }
            })
        return all_chunks
