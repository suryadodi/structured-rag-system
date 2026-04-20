
import sqlite3

class DocumentRegistry:
    
    def __init__(self,db_path:str = "document_registry.db"):
        self.db_path = db_path
        self._create_table()
#The Foundation Builder
    def _create_table(self):
        connectwith= sqlite3.connect(self.db_path)
        cursor = connectwith.cursor()
        cursor.execute(""" CREATE TABLE IF NOT EXISTS processed_files(
        filename TEXT PRIMARY KEY,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        connectwith.commit()
        connectwith.close()
# The Checker
    def is_processed(self,filename:str):
        connectwith = sqlite3.connect(self.db_path)
        cursor = connectwith.cursor()
        cursor.execute("SELECT 1 FROM processed_files WHERE filename=?",(filename,))
        result = cursor.fetchone()
        connectwith.close()

        return result is not None

# The Writer
    def mark_processed(self,filename:str):
        connectwith = sqlite3.connect(self.db_path)
        cursor= connectwith.cursor()
        cursor.execute("INSERT OR REPLACE INTO processed_files(filename) VALUES(?)",(filename,))
        connectwith.commit()
        connectwith.close()
    

        