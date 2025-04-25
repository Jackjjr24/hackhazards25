from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
import re
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

def clean_sql_output(raw_sql: str):
    """Remove markdown code block formatting like ```sql ... ```."""
    cleaned = re.sub(r"```sql|```", "", raw_sql, flags=re.IGNORECASE).strip()
    return cleaned

def get_sql_chain(db, db_type):
    prompt = ChatPromptTemplate.from_template("""
    You are a data analyst. Given the schema <SCHEMA>{schema}</SCHEMA>
    and database name '{db_name}', and the question: {question}, generate a SQL query.
    Write only the SQL query.
    """)

    llm = ChatGroq(model="mistral-saba-24b", temperature=0, groq_api_key=groq_api_key)

    def get_schema(_):
        return db.get_table_info()

    def get_db_name(_):
        return db._engine.url.database

    return (
        RunnablePassthrough.assign(
            schema=get_schema,
            db_name=get_db_name
        )
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query, db, chat_history, db_type):
    sql_chain = get_sql_chain(db, db_type)
    raw_sql = sql_chain.invoke({"question": user_query})
    cleaned_sql = clean_sql_output(raw_sql)
    db_name = db._engine.url.database
    final_sql = cleaned_sql.replace("'your_database_name'", f"'{db_name}'")
    
    try:
        result = db.run(final_sql)
        
        # Handle data retrieval queries (e.g., SELECT queries)
        if isinstance(result, list):
            # Flatten single-value tuples and convert to natural language
            if all(isinstance(row, tuple) and len(row) == 1 for row in result):
                # For queries like "give available table name", format it as a simple list of values
                formatted = f"The available table names are: {', '.join(row[0] for row in result)}."
            else:
                # For multi-column results, format them as a readable table
                formatted = "\n".join([" | ".join(map(str, row)) for row in result])
        else:
            formatted = str(result)

        # Handle schema changes (e.g., CREATE, DELETE queries)
        if 'CREATE' in user_query.upper() or 'DELETE' in user_query.upper():
            formatted = "Done"

    except Exception as e:
        formatted = f"Error occurred: {str(e)}"
    
    return formatted.strip()  # Ensure no extra spaces or newlines are included


