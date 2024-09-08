def prompt_for_trends(user_query: str) -> str:
    """
    Generates a prompt for answering questions related to Indian manufacturing trends and technologies.

    Args:
        user_query (str): The user's question related to manufacturing trends and technologies.

    Returns:
        str: A well-structured prompt for generating a detailed response to the query. 
        The response includes relevant company names, key industry trends, emerging technologies, innovations, 
        and their potential impact on the industry.
    """
    return (f"You are an expert in Indian manufacturing trends and technologies. "
            f"Based on the following question: '{user_query}', provide a detailed response. "
            f"Your answer should include any relevant company names, key industry trends, "
            f"emerging technologies, innovations, and the potential impact of these technologies on the industry.")


def prompt_for_summary(article_content: str) -> str:
    """
    Generates a prompt for summarizing an article related to Indian manufacturing.

    Args:
        article_content (str): The content of the article to be summarized.

    Returns:
        str: A structured prompt for generating a summary that highlights key points, including company names, 
        technologies mentioned, industry trends, and the potential impact on the manufacturing sector.
    """
    return (f"You are an expert in summarizing manufacturing trends and technologies. "
            f"Please summarize the following article on Indian manufacturing. "
            f"Ensure the summary highlights the key points, including relevant company names, "
            f"the technologies mentioned, industry trends, and the potential impact on the manufacturing sector: {article_content}")


def prompt_for_explanation(industry_term: str) -> str:
    """
    Generates a prompt for explaining industry-specific terms and concepts within the context of Indian manufacturing.

    Args:
        industry_term (str): The term or concept to be explained.

    Returns:
        str: A well-structured prompt for explaining the term, ensuring clarity, practical examples, 
        and an understanding of its significance in the Indian manufacturing sector.
    """
    return (f"You are an expert in Indian manufacturing trends and technologies. "
            f"Please explain the term '{industry_term}' in the context of the Indian manufacturing sector. "
            f"Ensure that the explanation is easy to understand, includes practical examples, and highlights its significance in the industry.")


# Example usage
prompt = prompt_for_trends("What are the current trends in robotics?")
