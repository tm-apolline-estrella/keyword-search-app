# Import third-party library modules
import pandas as pd
import pymssql

# Import local modules
from src.components.coach_ai.settings import database_connection_params

# Connect to your SQL Server


def get_session(session_id: str):
    conn = pymssql.connect(**database_connection_params)
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Execute the SQL command
    sql = f"SELECT * FROM dbo.AgentConversationSession WHERE id = '{session_id}'"
    cursor.execute(sql)

    # Fetch all rows from the executed SQL command
    data = cursor.fetchone()

    columns = [column[0] for column in cursor.description]

    result = {column: value for column, value in zip(columns, data)}

    conn.close()

    return result


def get_session_conversation(session_id: str):
    conn = pymssql.connect(**database_connection_params)
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Execute the SQL command
    sql = f"SELECT * FROM dbo.AgentConversation WHERE sessionId = '{session_id}'"
    cursor.execute(sql)

    # Fetch all rows from the executed SQL command
    data = cursor.fetchone()

    columns = [column[0] for column in cursor.description]

    result = {column: value for column, value in zip(columns, data)}

    conn.close()

    return result


def get_session_metadata(session_id: str):
    conn = pymssql.connect(**database_connection_params)
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Execute the SQL command
    sql = f"SELECT * FROM dbo.AgentConversationSessionMetadata WHERE sessionId = '{session_id}' ORDER BY dateCreated DESC"
    cursor.execute(sql)

    # Fetch all rows from the executed SQL command
    data = cursor.fetchall()

    columns = [column[0] for column in cursor.description]

    data_df = pd.DataFrame(data, columns=columns)

    result = data_df.to_dict("records")

    conn.close()

    return result
