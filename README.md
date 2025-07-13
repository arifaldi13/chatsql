# ChatSQL: A Natural Language Business Intelligence Chatbot

This project is a proof-of-concept web application that allows non-technical users to query a SQL database using plain English. It leverages the power of Large Language Models (LLMs) to bridge the gap between complex data systems and business stakeholders.

<p align="center">
  <img src="showcase.gif" />
</p>


## The Problem

In many organizations, business intelligence is a bottleneck. Stakeholders need data to make decisions, but they must rely on data analysts to write custom SQL queries. This process can be slow and inefficient. ChatSQL is designed to solve this problem by providing a direct, conversational interface to the database.


## Features

- **Natural Language to SQL:** Translates plain English questions into executable SQL queries.
- **Conversational Interface:** Remembers chat history for follow-up questions.
- **Robust Agent Logic:** Uses a custom prompt to handle ambiguity and prevent database modification.
- **Responsive UI:** Provides loading feedback and handles errors gracefully.

## Database Schema

The application connects to a simple SQLite database (`bi_database.db`) designed to mimic a basic e-commerce business. The schema consists of three tables:

**1. `customers`**
Stores information about each customer.

| Column      | Type    | Description                      |
|-------------|---------|----------------------------------|
| `customer_id` | INTEGER | Primary Key for the customer.    |
| `name`        | TEXT    | The full name of the customer.   |
| `join_date`   | DATE    | The date the customer registered.|

**2. `products`**
Contains details for all available products.

| Column         | Type    | Description                       |
|----------------|---------|-----------------------------------|
| `product_id`   | INTEGER | Primary Key for the product.      |
| `product_name` | TEXT    | The name of the product.          |
| `category`     | TEXT    | The category (e.g., 'Electronics'). |
| `price`        | REAL    | The price of the product.         |

**3. `orders`**
A transactional table that links customers and the products they purchased.

| Column      | Type    | Description                                  |
|-------------|---------|----------------------------------------------|
| `order_id`  | INTEGER | Primary Key for the order.                   |
| `customer_id` | INTEGER | Foreign Key linking to the `customers` table. |
| `product_id`  | INTEGER | Foreign Key linking to the `products` table.  |
| `order_date`  | DATE    | The date the order was placed.               |
| `quantity`    | INTEGER | The number of units of the product ordered.  |


## Tech Stack & Architecture

This application is built using a modern, AI-native stack:

- **AI Framework:** [LangChain](https://www.langchain.com/) (using the SQL Agent)
- **LLM:** OpenAI's `text-davinci-003`
- **Database:** SQLite
- **Backend/UI:** [Streamlit](https://streamlit.io/)
- **Environment:** Anaconda / Python 3.x

The architecture is straightforward: the Streamlit frontend captures user input and sends it to the LangChain SQL Agent. The agent uses an LLM to generate a SQL query, executes it against the SQLite database, and then uses the LLM again to formulate a final, human-readable answer.


## How to Run Locally

**Prerequisites:**
- Anaconda or Miniconda installed
- An OpenAI API Key

**Instructions:**
1.  **Clone the repository:**
    ```bash
    git clone [Your GitHub Repository URL]
    cd chatsql_project
    ```
2.  **Set up the Anaconda environment:**
    *(If you have an environment.yml file, provide instructions here. Otherwise, list the packages.)*
    ```bash
    # Example for manual installation:
    conda create --name chatsql python=3.9
    conda activate chatsql
    pip install streamlit langchain openai python-dotenv sqlalchemy
    ```
3.  **Set up your API Key:**
    Create a `.env` file in the root directory and add your key:
    ```
    OPENAI_API_KEY="sk-..."
    ```
4.  **Create and populate the database:**
    *(You used a Jupyter Notebook, so explain that here.)*
    - Open `database_setup.ipynb` and run all cells to create and populate `bi_database.db`.

5.  **Launch the application:**
    ```bash
    streamlit run app.py
    ```

## Security Considerations

This is a proof-of-concept. Directly executing LLM-generated SQL queries in a production environment poses a significant security risk (SQL Injection). For a production-grade system, the following would be necessary:

- A robust validation and sanitization layer for all generated SQL.
- Strict, read-only database permissions for the application's role.
- Comprehensive monitoring and logging of all executed queries.