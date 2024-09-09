def generate_prompt(user_query: str, combined_context: str, prompt_type: str) -> str:
    
    """
    Generates a prompt for answering questions as per the prompt type specified.

    Args:
        user_query (str): The user's question related to manufacturing and supply chain sector trends and technologies.
        combined_context (str): Context for the prompt to include
        prompt_type (str): Specifies the prompt type

    Returns:
        str: A well-structured prompt for generating a detailed response to the query. 
        The response includes relevant company names, key industry trends, emerging technologies, innovations, 
        and their potential impact on the industry.
    """
    
    if prompt_type == "trends":
        return (f"You are an expert in Indian manufacturing and supply chain sector trends and technologies. "
                f"Based on the following question: '{user_query}', provide a detailed response in less than 300 words. "
                f"Here is the context: {combined_context}. "
                f"If the related context is not found then don't try to make up an answer. "
                f"Your answer should include relevant company names, key industry trends, "
                f"emerging technologies, and the impact of these technologies.")
    
    elif prompt_type == "summary":
        return (f"As an expert in the manufacturing and supply chain sector, "
                f"provide a clear and concise summary of the following content in less than 200 words. "
                f"Highlight key insights, including important company names, "
                f"emerging technologies, industry trends, and their impact on the sector: {combined_context}.")
    
    elif prompt_type == "explanation":
        return (f"You are an expert in Indian manufacturing and supply chain sector trends and technologies. "
                f"Please explain the term '{user_query}' in the context of the Indian manufacturing and supply chain sector. "
                f"Here is some context for you: {combined_context}. "
                f"Ensure the explanation is easy to understand, includes examples, "
                f"and highlights its significance in the industry in less than 100 words.")
    
    return ""