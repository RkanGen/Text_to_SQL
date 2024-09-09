import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai
import re
import pandas as pd

# (Keep all the previous imports and function definitions)
# Load environment variables
load_dotenv()

# Set up Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')
# Create a connection to the SQLite database

conn = sqlite3.connect('example.db', check_same_thread=False)
cursor = conn.cursor()
# Function to create sample database
def create_sample_database():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary REAL
    )
    ''')
    
    # Insert sample data
    sample_data = [
        (1, 'John Doe', 'IT', 75000),
        (2, 'Jane Smith', 'HR', 65000),
        (3, 'Mike Johnson', 'Sales', 80000),
        (4, 'Emily Brown', 'Marketing', 70000),
        (5, 'David Lee', 'IT', 78000)
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?)', sample_data)
    conn.commit()

# Function to execute SQL query
def execute_query(query, fetch=True):
    try:
        query = query.strip()
        if not query.endswith(';'):
            query += ';'
        
        cursor.execute(query)
        
        if fetch:
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return f"Query executed successfully. Rows affected: {cursor.rowcount}"
    except sqlite3.Error as e:
        return f"SQLite error: {e}"
# Function to generate SQL query using Gemini API
def generate_sql_query(prompt):
    try:
        response = model.generate_content(f"Convert the following text to a SQL query for a table named 'employees' with columns 'id', 'name', 'department', and 'salary'. The query can be SELECT, INSERT, UPDATE, or DELETE. Return only the SQL query without any explanation or formatting: {prompt}")
        sql_query = response.text.strip()
        
        sql_query = re.sub(r'```sql|```', '', sql_query)
        sql_query = re.sub(r'[^\w\s*()=\'"%,;]', '', sql_query)
        
        return sql_query.strip()
    except Exception as e:
        return f"Error generating SQL query: {e}"

# Function to validate SQL query
def validate_sql_query(query):
    if not re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE)', query, re.IGNORECASE):
        return False, "Only SELECT, INSERT, UPDATE, or DELETE statements are allowed"
    
    tables = re.findall(r'\b(FROM|INTO|UPDATE)\s+(\w+)', query, re.IGNORECASE)
    if not all(table[1].lower() == 'employees' for table in tables):
        return False, "Only the 'employees' table is allowed in the query"
    
    return True, "Valid SQL query"
def get_all_data():
    return pd.read_sql_query("SELECT * FROM employees", conn)

# Streamlit UI
st.set_page_config(page_title="SQL Database Manager", page_icon="🔍", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        padding-bottom: 100px;
    }
    .query-output {
        background-color: black;
        color: #00ff00;
        padding: 20px;
        border-radius: 5px;
        margin-top: 20px;
        font-size: 16px;
        min-height: 200px;
    }
    .sql-query {
        color: #00ff00;
        font-family: monospace;
    }
    .footer {
        position: bottom;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        padding: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("SQL Database Manager")

# Sidebar with database display
st.sidebar.header("Current Database")
st.sidebar.dataframe(get_all_data())

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Enter your query in natural language")
    user_input = st.text_area("For example: 'Show all employees in the IT department' or 'Add a new employee named Alice Johnson in Marketing with a salary of 72000'", height=100)
    
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        if st.button("Generate SQL"):
            if user_input:
                sql_query = generate_sql_query(user_input)
                if sql_query.startswith("Error"):
                    st.error(sql_query)
                else:
                    st.session_state['generated_sql'] = sql_query
                    st.subheader("Generated SQL Query")
                    st.markdown(f'<div class="query-output"><pre class="sql-query">{sql_query}</pre></div>', unsafe_allow_html=True)
            else:
                st.warning("Please enter a query.")
    
    with col1_2:
        if st.button("Execute SQL"):
            if 'generated_sql' in st.session_state:
                sql_query = st.session_state['generated_sql']
                is_valid, validation_message = validate_sql_query(sql_query)
                if is_valid:
                    st.success(validation_message)
                    
                    if sql_query.lower().startswith("select"):
                        results = execute_query(sql_query, fetch=True)
                    else:
                        results = execute_query(sql_query, fetch=False)
                    
                    st.subheader("Query Results")
                    if isinstance(results, list):
                        if len(results) > 0:
                            column_names = [description[0] for description in cursor.description]
                            results_dict = [dict(zip(column_names, row)) for row in results]
                            st.markdown('<div class="query-output">', unsafe_allow_html=True)
                            st.table(results_dict)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.info("No results found.")
                    else:
                        st.markdown(f'<div class="query-output">{results}</div>', unsafe_allow_html=True)
                    
                    # Update sidebar after execution
                    st.sidebar.dataframe(get_all_data())
                else:
                    st.error(f"Invalid SQL query: {validation_message}")
            else:
                st.warning("Please generate an SQL query first.")

with col2:
    st.subheader("Database Schema")
    st.code('''
    Table: employees
    Columns:
    - id (INTEGER, PRIMARY KEY)
    - name (TEXT)
    - department (TEXT)
    - salary (REAL)
    ''')
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        if st.button("Create Sample Database"):
            create_sample_database()
            st.success("Sample database created successfully!")
            st.sidebar.dataframe(get_all_data())
    
    with col2_2:
        if st.button("Reset Database"):
            cursor.execute("DELETE FROM employees")
            create_sample_database()
            st.success("Database reset to initial state!")
            st.sidebar.dataframe(get_all_data())

# Footer
st.markdown("""
<div class="footer">
    <p>About: This app allows you to manage an SQLite database using natural language queries. You can select, insert, update, or delete data.</p>
    <p>Created with ❤️ using Streamlit, SQLite, and Gemini API</p>
</div>
""", unsafe_allow_html=True)