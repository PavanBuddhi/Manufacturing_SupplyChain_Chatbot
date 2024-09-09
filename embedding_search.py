import os
import pinecone
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from warnings import filterwarnings
import google.generativeai as genai

filterwarnings('ignore')

# loading api key's
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Loading the already created index in Pinecone
pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("manufacturing-articles-index")


def retrieve_context_from_pinecone(query: str, num_results: int = 10):
    embedding_model = SentenceTransformer("All-MPNet-Base-v2")
    query_vector = embedding_model.encode(query).tolist()

    # Query Pinecone to get top matching documents
    results = index.query(vector=query_vector, top_k=num_results, include_metadata=True)
    
    # Extract relevant content from the retrieved matches
    context_chunks = []
    for match in results['matches']:
        if 'metadata' in match and 'content' in match['metadata']:
            context_chunks.append(match['metadata']['content'])
    
    # Combine the top results into a single context block
    return " ".join(context_chunks)


# print(retrieve_context_from_pinecone("How much was the amount chevron wants to invest in Karnatka?"))


# def generate_prompt(user_query: str, context: str, prompt_type: str) -> str:
#     if prompt_type == "trends":
#         return (f"You are an expert in Indian manufacturing trends and technologies. "
#                 f"Based on the following question: '{user_query}', provide a detailed response. "
#                 f"Here is the context: {context}. "
#                 f"If the related context is not found then don't try to make up an answer. "
#                 f"Your answer should include relevant company names, key industry trends, "
#                 f"emerging technologies, and the impact of these technologies.")
    
#     elif prompt_type == "summary":
#         return (f"You are an expert in summarizing manufacturing trends and technologies. "
#                 f"Summarize the following content on Indian manufacturing. "
#                 f"Ensure the summary highlights key points, company names, technologies, "
#                 f"trends, and the impact on the sector: {context}")
    
#     elif prompt_type == "explanation":
#         return (f"You are an expert in Indian manufacturing trends and technologies. "
#                 f"Please explain the term '{user_query}' in the context of the Indian manufacturing sector. "
#                 f"Here is some context for you: {context}. "
#                 f"Ensure the explanation is easy to understand, includes examples, "
#                 f"and highlights its significance in the industry.")
    
#     return ""


# # Initialize the Gemini model ()
# def generate_answer_with_gemini(prompt: str) -> str:
    
#     model = genai.GenerativeModel(model_name='gemini-1.0-pro')
#     response = model.generate_content(prompt)
#     print(response.text)
    
    
# # Example of generating an answer
# def answer_query(user_query: str, prompt_type: str):
#     context = retrieve_context_from_pinecone(user_query)
#     prompt = generate_prompt(user_query, context, prompt_type)
    
#     # Get the answer from the Gemini model
#     answer = generate_answer_with_gemini(prompt)
    
#     return answer

# answer_query("Deep tech powerhouse", "trends")