import re
import os
import sqlite3
import pinecone
from typing import List, Tuple
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pinecone import ServerlessSpec, Index
from dotenv import load_dotenv
import asyncio
from aiohttp import ClientSession

# Loading the keys
load_dotenv()

# Function to clean the vector ID by removing non-ASCII characters
def clean_vector_id(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text)


def fetch_articles_from_db(db_path: str) -> List[Tuple[str, str, str, str]]:
    """
    Fetch articles from the SQLite database.

    Args:
        db_path (str): Path to the SQLite database.

    Returns:
        List[Tuple[str, str, str, str]]: List of tuples containing title, synopsis, link, and content.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, synopsis, link, content FROM articles")
        articles = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()
    
    print(f"Fetched {len(articles)} articles from the database.")
    return articles


def split_articles_into_documents(articles: List[Tuple[str, str, str, str]], chunk_size: int = 510, chunk_overlap: int = 50) -> List[Document]:
    """
    Splits the article content into smaller documents.

    Args:
        articles (List[Tuple[str, str, str, str]]): List of articles fetched from the database.
        chunk_size (int): Maximum size of each text chunk.
        chunk_overlap (int): Overlap size between chunks.

    Returns:
        List[Document]: List of documents containing chunked content and metadata.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = []

    for title, description, link, content in articles:
        try:
            chunks = splitter.split_text(content)
            for chunk in chunks:
                doc = Document(page_content=chunk, metadata={"title": title, "description": description, "link": link})
                documents.append(doc)
        except Exception as e:
            print(f"Error splitting article '{title}': {e}")
    
    print(f"Prepared {len(documents)} documents from the articles.")
    return documents


async def initialize_pinecone(api_key: str, index_name: str, dimension: int = 768, metric: str = 'cosine') -> Index:
    """
    Initializes and connects to the Pinecone index.

    Args:
        api_key (str): API key for Pinecone.
        index_name (str): Name of the Pinecone index.
        dimension (int): Embedding dimension size.
        metric (str): Similarity metric used in Pinecone.

    Returns:
        Index: Pinecone index object.
    """
    pc = pinecone.Pinecone(api_key=api_key)
    
    # Create or connect to an index
    if index_name not in pc.list_indexes():
        pc.create_index(
            name=index_name,
            dimension=dimension, # Embedding dimension size based on the Hugging Face model
            metric=metric, 
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ) 
        )    
    return pc.Index(index_name)


async def get_embeddings(model: SentenceTransformer, text: str) -> List[float]:
    """
    Generates embeddings for the provided text using the sentence-transformers model.

    Args:
        model (SentenceTransformer): The embedding model.
        text (str): The text to embed.

    Returns:
        List[float]: Embedding vector.
    """
    try:
        return model.encode(text).tolist()
    except Exception as e:
        print(f"Error generating embedding for text: {e}")
        return []
    

async def index_documents_to_pinecone(documents: List[Document], index: Index, model: SentenceTransformer) -> None:
    """
    Indexes the documents into the Pinecone vector database.

    Args:
        documents (List[Document]): List of documents to be indexed.
        index (Index): Pinecone index object.
        model (SentenceTransformer): Model used for generating embeddings.
    """
    for i, doc in enumerate(documents):
        title = clean_vector_id(doc.metadata['title'])
        vector = await get_embeddings(model, doc.page_content)
        if vector:
            vector_id = f"{title}_{i}"
            try:
                # Add 'content' to metadata
                metadata = {
                    "title": doc.metadata['title'],
                    "description": doc.metadata.get('description', ''),
                    "link": doc.metadata.get('link', ''),
                    "content": doc.page_content  # Store the chunked content
                }
                # Await the upsert call directly
                await index.upsert([(vector_id, vector, metadata)])
            except Exception as e:
                print(f"Failed to index document '{doc.metadata['title']}': {e}")
        else:
            print(f"Skipping document '{doc.metadata['title']}' due to empty embedding.")



async def main():
    # Define paths and constants
    db_path = 'manufacturing_articles.db'
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    index_name = 'manufacturing-articles-index'
    embedding_model_name = 'All-MPNet-Base-v2'
    
    # Step 1: Fetch articles from SQLite database
    articles = fetch_articles_from_db(db_path)
    
    if not articles:
        print("No articles fetched, terminating process.")
        return

    # Step 2: Split articles into smaller documents
    documents = split_articles_into_documents(articles)
    
    if not documents:
        print("No documents created, terminating process.")
        return

    # Step 3: Initialize Pinecone
    pinecone_index = await initialize_pinecone(api_key=pinecone_api_key, index_name=index_name)

    # Step 4: Load the sentence-transformers embedding model
    embedding_model = SentenceTransformer(embedding_model_name)

    # Step 5: Index documents into Pinecone
    await index_documents_to_pinecone(documents, pinecone_index, embedding_model)
    
    print("Data has been successfully indexed into Pinecone.")
    

if __name__ == "__main__":
    asyncio.run(main())