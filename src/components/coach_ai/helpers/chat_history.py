# Import standard library modules
from typing import Dict, List

# Import third-party library modules
import pandas as pd
import pymssql
from langchain_core.messages import AIMessage, HumanMessage

# Import local modules
from src.components.coach_ai.settings import database_connection_params

# Connect to your SQL Server

retention_period = 4


def get_librarian_chat_history(conversation_id: str):
    conn = pymssql.connect(**database_connection_params)
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Execute the SQL command
    sql = f"SELECT * FROM dbo.KnowledgebaseMessage WHERE conversationId = '{conversation_id}'"
    cursor.execute(sql)

    # Fetch all rows from the executed SQL command
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    chat_history = parse_chat_history_with_langchain_message_format(data, columns)

    conn.close()

    return chat_history


def get_relationship_manager_chat_history(conversation_id: str):
    conn = pymssql.connect(**database_connection_params)
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Execute the SQL command
    sql = f"SELECT * FROM dbo.Message WHERE conversationId = '{conversation_id}'"
    cursor.execute(sql)

    # Fetch all rows from the executed SQL command
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    chat_history = parse_chat_history(data, columns)

    conn.close()

    return chat_history


def get_agent_chat_history(conversation_id: str, persona_name: str):
    conn = pymssql.connect(**database_connection_params)
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Execute the SQL command
    sql = f"SELECT * FROM dbo.AgentMessage WHERE conversationId = '{conversation_id}'"
    cursor.execute(sql)

    # Fetch all rows from the executed SQL command
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    sender_labels = {False: "Agent", True: persona_name}
    chat_history = parse_chat_history(data, columns, sender_labels=sender_labels)

    conn.close()

    return chat_history


def get_agent_chat_history_with_evaluation(conversation_id: str):
    conn = pymssql.connect(**database_connection_params)
    # Create a cursor from the connection
    cursor = conn.cursor()

    # Execute the SQL command
    sql = f"""
        SELECT * FROM dbo.AgentMessage am
        LEFT JOIN dbo.AgentConversationSessionMetadata acsm ON am.id = acsm.messageId
        WHERE conversationId = '{conversation_id}'
    """
    cursor.execute(sql)

    # Fetch all rows from the executed SQL command
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    chat_history = parse_chat_history_with_evaluation(data, columns)

    conn.close()

    return chat_history


def parse_chat_history(
    data: List, columns: List, sender_labels: Dict[bool, str] = None
):
    if not sender_labels:
        sender_labels = {False: "User", True: "AI"}

    chat_history_df = pd.DataFrame(data, columns=columns).sort_values(by="createdAt")
    chat_history_df = chat_history_df.tail(retention_period)
    chat_history_df["sender"] = chat_history_df["is_bot"].replace(sender_labels)
    chat_history_df["context"] = (
        chat_history_df["sender"] + ": " + chat_history_df["text"]
    )
    chat_history = chat_history_df["context"].tolist()
    return chat_history


def parse_chat_history_with_evaluation(data: List, columns: List):
    chat_history_df = pd.DataFrame(data, columns=columns).sort_values(by="createdAt")

    chat_history = []

    agent_message = None
    customer_message = None

    for _, row in chat_history_df.iterrows():
        if not row["is_bot"]:
            agent_message = row["text"]
        else:
            customer_message = row["text"]

        if agent_message and customer_message:
            chat_history.append(
                {
                    "agent_message": agent_message,
                    "customer_message": customer_message,
                    "reception_assessment": row["receptionAnalysis"],
                    "reception_score": round(float(row["receptionScore"]), 4),
                }
            )
            # Reset holder variables
            agent_message = None
            customer_message = None

    return chat_history


def parse_chat_history_with_langchain_message_format(data: List, columns: List):
    chat_history_df = pd.DataFrame(data, columns=columns).sort_values(by="createdAt")
    chat_history_df = chat_history_df.tail(retention_period)

    formatted_chat_history = []
    for index, row in chat_history_df.iterrows():
        if row["is_bot"]:
            formatted_chat_history.append(AIMessage(row["text"]))
        else:
            formatted_chat_history.append(HumanMessage(row["text"]))

    return formatted_chat_history
