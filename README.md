# Text_to_SQL


This Streamlit application allows users to manage an SQLite database using natural language queries. It leverages the Gemini API to convert natural language into SQL queries, providing an intuitive interface for database operations.
![proc](https://github.com/user-attachments/assets/b72ec237-3f74-4625-81ba-67bb5b577fde)
![proc2](https://github.com/user-attachments/assets/37492718-52ed-4fef-b37c-07ab10f81ca9)

## Features
# This app consist of SQL Database Manager
- Natural language to SQL query conversion
- Execute SELECT, INSERT, UPDATE, and DELETE operations
- Real-time database display
- Sample database creation and reset functionality
- User-friendly interface with Streamlit

## Prerequisites

- Python 3.7+
- Streamlit
- SQLite3
- google-generativeai
- python-dotenv
- pandas
- sqlparse

## Installation

1. Clone this repository:
   git clone https://github.com/RkanGen/Text_to_SQL.git
   cd Text_to_SQL
2. Install the required packages:
pip install -r requirements.txt
3. Create a `.env` file in the project root and add your Gemini API key:
## Usage
1. Run the Streamlit app:
streamlit run app.py


2. Use the interface to interact with the database:
- Enter natural language queries in the text area
- Click "Generate SQL" to convert your query to SQL
- Click "Execute SQL" to run the generated query
- Use the "Create Sample Database" and "Reset Database" buttons to manage the database state


## Database Schema

The application uses a simple `employees` table with the following structure:

```sql
CREATE TABLE employees (
 id INTEGER PRIMARY KEY,
 name TEXT,
 department TEXT,
 salary REAL
)
```
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

License
This project is open source and available under the MIT License.

Acknowledgements
Streamlit for the web application framework
Google's Gemini API for natural language processing
