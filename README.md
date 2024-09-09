# Manufacturing_SupplyChain_Chatbot

Helps in generating response as per the User queries, summaries and explaining industry specific terms with example.

## How to run?
### STEPS:

Clone the respository

Project repo: https://github.com/PavanBuddhi/Manufacturing_SupplyChain_Chatbot.git

#### STEP 01- Create a conda environment after opening the repository

```bash
conda create -n mscchatbot python=3.10 -y
```

```bash
conda activate mscchatbot
```

#### STEP 02- Install the requirements

```bash
pip install -r requirements.txt
```

### STEP 03 - Create a .env file and add your api keys as follows:

```bash
PINECONE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GOOGLE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### STEP 04 - Scrape the manufacturing articles from website

Run the below command in order to scrape the articles from website and store it in sqlite database

```bash
python web_scraper.py
```

### STEP 05 - Implement Full Text Search from Sqlite

Run the below command to fetch results using full text search

```bash
python full_text_search.py
```

### STEP 06 - Chunking and Data Ingestion into Pinecone Vector Database

Run the below command to perform chunking and index vectors into Pinecone Vector Database

```bash
python data_ingestion.py
```

### STEP 07 - Combine the chunks from both FTS and Embedding based search and generate response

Run the below command to perform hybrid search and generate response

```bash
python hybrid_search.py
```