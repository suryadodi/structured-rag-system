
import sqlite3
import hashlib

class DocumentRegistry:
    
    def __init__(self,db_path:str = "document_registry.db"):
        self.db_path = db_path
        self._create_table()
#The Foundation Builder
    def _create_table(self):
        connectwith= sqlite3.connect(self.db_path)
        cursor = connectwith.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS processed_files(
        file_hash TEXT PRIMARY KEY,filename TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        connectwith.commit()
        connectwith.close()

# The Hash Generator
    def generate_hash(self,filepath:str):
        sha256_hash = hashlib.sha256()
        with open(filepath,"rb") as file:
            for byte_block in iter(lambda:file.read(4096),b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
# The Checker
    def is_processed(self,file_hash:str):
        connectwith = sqlite3.connect(self.db_path)
        cursor = connectwith.cursor()
        cursor.execute("SELECT 1 FROM processed_files WHERE file_hash=?",(file_hash,))
        result = cursor.fetchone()
        connectwith.close()

        return result is not None

# The Writer
    def mark_processed(self,file_hash:str, filename:str):
        connectwith = sqlite3.connect(self.db_path)
        cursor= connectwith.cursor()
        cursor.execute("INSERT OR REPLACE INTO processed_files(file_hash, filename) VALUES(?,?)",(file_hash,filename))
        connectwith.commit()
        connectwith.close()
    

        