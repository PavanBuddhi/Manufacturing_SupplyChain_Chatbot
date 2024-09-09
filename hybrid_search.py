import os
import google.generativeai as genai
from warnings import filterwarnings
from dotenv import load_dotenv
from full_text_search import search_articles_with_link
from embedding_search import retrieve_context_from_pinecone
from prompt import generate_prompt


filterwarnings('ignore')

# loading api key's
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def combine_results(fts_results, pinecone_chunks, max_token_limit=7000):
    """
    Combine FTS search results and Pinecone chunks efficiently to stay within token limit.

    Args:
        fts_results (list): List of FTS search results (only content).
        pinecone_chunks (list): List of Pinecone chunk results (vector search).
        max_token_limit (int): Maximum token limit for LLM input.

    Returns:
        str: Combined text ready to be passed to LLM.
    """
    # Helper function to calculate word count (approximating tokens)
    def calculate_token_count(text):
        return len(text.split())

    # Combine FTS results and Pinecone chunks
    combined_content = ""

    # Step 1: Add FTS results first
    for content in fts_results:
        combined_content += f"\nContent: {content}\n"
        
        # Check if we're near the token limit
        if calculate_token_count(combined_content) > max_token_limit:
            break

    # Step 2: Add Pinecone chunks (additional semantic context)
    for chunk in pinecone_chunks:
        # If chunk is a string, add it directly
        if isinstance(chunk, str):
            chunk_content = chunk
        # Otherwise, extract content from dictionary
        elif isinstance(chunk, dict) and 'metadata' in chunk and 'content' in chunk['metadata']:
            chunk_content = chunk['metadata']['content']
        else:
            continue  # Skip if the chunk doesn't have content

        combined_content += f"\nChunk: {chunk_content}\n"
        
        # Check if we're exceeding token limit
        if calculate_token_count(combined_content) > max_token_limit:
            break

    # Ensure final content respects token limit
    return combined_content[:max_token_limit]


# def generate_prompt(user_query: str, combined_context: str, prompt_type: str) -> str:
#     if prompt_type == "trends":
#         return (f"You are an expert in Indian manufacturing and supply chain sector trends and technologies. "
#                 f"Based on the following question: '{user_query}', provide a detailed response. "
#                 f"Here is the context: {combined_context}. "
#                 f"If the related context is not found then don't try to make up an answer. "
#                 f"Your answer should include relevant company names, key industry trends, "
#                 f"emerging technologies, and the impact of these technologies.")
    
#     elif prompt_type == "summary":
#         return (f"As an expert in the manufacturing and supply chain sector, "
#                 f"provide a clear and concise summary of the following content in less than 300 words. "
#                 f"Highlight key insights, including important company names, "
#                 f"emerging technologies, industry trends, and their impact on the sector: {combined_context}.")
    
#     elif prompt_type == "explanation":
#         return (f"You are an expert in Indian manufacturing and supply chain sector trends and technologies. "
#                 f"Please explain the term '{user_query}' in the context of the Indian manufacturing sector. "
#                 f"Here is some context for you: {combined_context}. "
#                 f"Ensure the explanation is easy to understand, includes examples, "
#                 f"and highlights its significance in the industry in less than 200 words.")
    
#     return ""


# Initialize the Gemini model ()
def generate_answer_with_gemini(prompt: str) -> str:
    
    """
    Generate a response using LLM based on the query and combined content.

    Args:
        query (str): User query.
        combined_text (str): Combined content from FTS and Pinecone.

    Returns:
        str: LLM-generated response.
    """    
    model = genai.GenerativeModel(model_name='gemini-1.0-pro')
    response = model.generate_content(prompt, stream=True)
    for part in response:
        print(part.text)
    
    
# Example of generating an answer
def answer_query(user_query: str, prompt_type: str):
    
    results = search_articles_with_link("manufacturing_articles.db", user_query)
    fts_results = []
    for content in results:
        # print(f"Title: {title}\nSynopsis: {synopsis}\nLink: {link}\nContent: {content[:200]}...\n")
        # print(f"Content: {content}...\n")
        fts_results.append(content)
    
    pinecone_chunks = retrieve_context_from_pinecone(user_query)
    combined_context = combine_results(fts_results, pinecone_chunks)
    prompt = generate_prompt(user_query, combined_context, prompt_type)
    
    # Get the answer from the Gemini model
    answer = generate_answer_with_gemini(prompt)
    
    return answer

answer_query("destination plant", "trends")