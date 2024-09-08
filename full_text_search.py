import sqlite3

def create_fts_table_with_link(db_path: str):
    """
    Create an FTS5-enabled virtual table for articles in SQLite, including the 'link' attribute.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create FTS5 virtual table for full-text search on the articles, including the 'link' attribute (unindexed)
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
                title, synopsis, content, link UNINDEXED
            )
        ''')

        # Migrate existing data to the FTS table, including the 'link'
        cursor.execute('''
            INSERT INTO articles_fts (title, synopsis, content, link)
            SELECT title, synopsis, content, link FROM articles
        ''')

        conn.commit()
        # print("FTS5 table with 'link' attribute created and data inserted.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# Call the function to create the FTS5 table and index the data, including the link attribute
db_path = 'manufacturing_articles.db'
create_fts_table_with_link(db_path)


def remove_duplicates_from_articles(db_path: str):
    """
    Remove duplicate rows from the 'articles' table based on the combination of title, synopsis, content, and link.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Remove duplicates based on unique (title, synopsis, content, link)
        cursor.execute('''
            DELETE FROM articles
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM articles
                GROUP BY title, synopsis, content, link
            )
        ''')

        conn.commit()
        print("Duplicates removed from 'articles' table.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

# # Call this function to clean up the articles table
# remove_duplicates_from_articles(db_path)


def search_articles_with_link(db_path: str, query: str, limit: int = 3):
    """
    Search articles using full-text search (FTS5) based on the query and include the 'link' attribute in the results.
    
    Args:
        db_path (str): Path to the SQLite database.
        query (str): The full-text search query string.
        limit (int): The maximum number of results to return.
    
    Returns:
        List[Tuple[str, str, str, str]]: List of tuples containing title, synopsis, content, and link of the matched articles.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Perform full-text search with DISTINCT to remove duplicates
        cursor.execute(f'''
            SELECT DISTINCT title, synopsis, content, link
            FROM articles_fts
            WHERE articles_fts MATCH ?
            LIMIT ?
        ''', (query, limit))

        results = cursor.fetchall()
        return results

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

# Perform a full-text search on the articles, including the link attribute
query = 'Garuda Aerospace signs pact with French Thales to promote drone ecosystem'
results = search_articles_with_link(db_path, query)

# Display the results with the link
for content in results:
    # print(f"Title: {title}\nSynopsis: {synopsis}\nLink: {link}\nContent: {content[:200]}...\n")
    print(f"Content: {content}...\n")