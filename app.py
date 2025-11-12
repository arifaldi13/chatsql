import sqlite3
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent

AGENT_PREFIX = """
You are a helpful and friendly AI assistant designed to interact with a SQL database.
Your goal is to help users get business intelligence from the data without needing to write SQL.

Database dialect: {dialect}
Always limit query results to top {top_k} rows unless the user asks otherwise.

Instructions:
1) Given a user's question, think about what you need to know to answer it.
2) Create a syntactically correct SQL query for the database dialect above.
3) Double-check your query and ensure it does not modify the database (no INSERT/UPDATE/DELETE/DROP).
4) Execute the query.
5) Look at the results and return a final, human-readable answer in a complete sentence.
6) If you get an error, fix the query and try again.
7) If the question is vague, ask for clarification (e.g., define “best customer”: by total spending vs order count).
8) Do not make up information—if data is not in the DB, say you cannot find it.
9) All prices are in Indonesian Rupiah (IDR).
10) Expect questions in Bahasa Indonesia as well as English.
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
db = SQLDatabase.from_uri("sqlite:///bi_database.db")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="tool-calling",
    prefix=AGENT_PREFIX,
    top_k=5,
    verbose=True,
)

st.set_page_config(page_title="ChatSQL", page_icon="💬", initial_sidebar_state="collapsed")
st.title("ChatSQL")
st.write("Your Business Intelligence Chatbot. Ask me questions about your sales, customers, and products!")
with st.sidebar:
    st.header("About")
    st.markdown("This chatbot uses LangChain + OpenAI to query a SQL database via natural language.")
    st.markdown("---")
    st.markdown("🔗 [View on GitHub](https://github.com/arifaldi13/chatsql)")

@st.cache_data
def load_data():
    """Connects to the SQLite DB and loads tables into pandas DataFrames."""
    conn = sqlite3.connect("bi_database.db")
    customers_df = pd.read_sql_query("SELECT * FROM customers", conn)
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    return customers_df, products_df, orders_df
with st.expander("📂 View Database Tables"):
    st.info("Here is the raw data from the three tables in the database.")
    try:
        customers_df, products_df, orders_df = load_data()
        st.subheader("Customers Table")
        st.dataframe(customers_df, use_container_width=True)
        st.subheader("Products Table")
        st.dataframe(products_df, use_container_width=True)
        st.subheader("Orders Table")
        st.dataframe(orders_df, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")

def set_prompt(prompt_text: str):
    st.session_state.prompt = prompt_text

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Who are our top 5 customers by order count?",
              on_click=set_prompt,
              args=("Who are our top 5 customers by order count?",))
with col2:
    st.button("What are our 5 best-selling products?",
              on_click=set_prompt,
              args=("What are our 5 best-selling products by quantity sold?",))
with col3:
    st.button("Berapa total pendapatan di bulan Maret 2024?",
              on_click=set_prompt,
              args=("Berapa total pendapatan dari seluruh pembelian di Bulan Maret 2024?",))

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
user_typed = st.chat_input("What would you like to know?")
quick_prompt = st.session_state.pop("prompt", None)
prompt = user_typed or quick_prompt
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = agent_executor.invoke({"input": prompt})
            answer = result.get("output", result) if isinstance(result, dict) else str(result)
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
