import sqlite3
import pandas as pd
import streamlit as st
from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

AGENT_PREFIX = """
You are a helpful and friendly AI assistant designed to interact with a SQL database.
Your goal is to help users get business intelligence from the data without needing to write SQL.

Here are your instructions:
1.  Given a user's question, first think about what you need to know to answer it.
2.  Create a syntactically correct SQLite query to get that information.
3.  Before executing, double-check your query to ensure it is correct and does not modify the database (no INSERT, UPDATE, DELETE).
4.  Execute the query.
5.  Look at the results and return a final, human-readable answer in a complete sentence.
6.  If you get an error, try to fix your query and run it again.
7.  If a question is vague, ask the user for clarification. For example, if they ask "who is the best customer?", ask them to define "best" (e.g., by total spending, or by number of orders).
8.  Do not make up information. If the data is not in the database, say that you cannot find the answer.
9.  The price is in Indonesian Rupiah
10. Expect questions in Bahasa Indonesia too (not only english).
"""

db = SQLDatabase.from_uri("sqlite:///bi_database.db")
llm = OpenAI(temperature=0, verbose=True)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    prefix=AGENT_PREFIX,
)

st.set_page_config(
    page_title="ChatSQL",
    page_icon="💬",
    initial_sidebar_state="collapsed"
)

st.title("ChatSQL")
st.write("Your Business Intelligence Chatbot. Ask me questions about your sales, customers, and products! Or try one of the suggestions below.")

with st.sidebar:
    st.header("About")
    st.markdown("""
    This chatbot is powered by LangChain and OpenAI to allow you to query a SQL database using natural language.
    """)
    st.markdown("---")
    st.markdown("🔗 [View on GitHub](https://github.com/arifaldi13)")

@st.cache_data
def load_data():
    """Connects to the SQLite DB and loads tables into pandas DataFrames."""
    conn = sqlite3.connect('bi_database.db')
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

def set_prompt(prompt_text):
    st.session_state.prompt = prompt_text

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Who are our top 5 customers by order count?", on_click=set_prompt, args=("Who are our top 5 customers by order count?",))
with col2:
    st.button("What are our 5 best-selling products?", on_click=set_prompt, args=("What are our 5 best-selling products by quantity sold?",))
with col3:
    st.button("Berapa total pendapatan di bulan Maret 2024?", on_click=set_prompt, args=("Berapa total pendapatan dari seluruh pembelian di Bulan Maret 2024",))

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if prompt := st.chat_input("What would you like to know?", key="chat_input") or st.session_state.get("prompt"):
    if "prompt" in st.session_state:
        st.session_state.prompt = None
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = agent_executor.run(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})