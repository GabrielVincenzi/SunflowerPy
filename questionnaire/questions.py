import pandas as pd
import os
from tools.toolbi import send_df

# ----------------- QUESTIONS -----------------
q_file_path = "questionnaire/questions.csv"
q_columns = ["id", "object_id", "title", "body", "explanation", "difficulty", 
             "sponsor", "sponsor_body", "sponsor_link", "is_active"]

# Ensure file exists
if os.path.exists(q_file_path):
    try:
        df_q = pd.read_csv(q_file_path)
        if df_q.empty and len(df_q.columns) == 0:
            df_q = pd.DataFrame(columns=q_columns)
    except pd.errors.EmptyDataError:
        df_q = pd.DataFrame(columns=q_columns)
else:
    df_q = pd.DataFrame(columns=q_columns)

# Determine ID
next_question_id = 1 if df_q.empty else int(df_q["id"].max()) + 1

# Question row to insert
q_rows = [{
    "id": next_question_id,
    "object_id": "",
    "title": "Example question",
    "body": "What is the capital of X?",
    "explanation": "Because of Y...",
    "difficulty": 3,
    "sponsor": "",
    "sponsor_body": "",
    "sponsor_link": "",
    "is_active": True,
}]

# Modify DataFrame
df_q = pd.concat([df_q, pd.DataFrame(q_rows)], ignore_index=True)
df_q.to_csv(q_file_path, index=False)

send_df(df_q, dest_table="questions", new_rows=q_rows, file_path=q_file_path,
        by_row=True, vectorization=False)

# Store question ID for choices
question_id_for_choices = next_question_id


# ----------------- CHOICES -----------------
a_file_path = "questionnaire/choices.csv"
a_columns = ["id", "question_id", "content", "is_correct"]

# Ensure file exists
if os.path.exists(a_file_path):
    try:
        df_a = pd.read_csv(a_file_path)
        if df_a.empty and len(df_a.columns) == 0:
            df_a = pd.DataFrame(columns=a_columns)
    except pd.errors.EmptyDataError:
        df_a = pd.DataFrame(columns=a_columns)
else:
    df_a = pd.DataFrame(columns=a_columns)

# Determine ID
next_choice_id = 1 if df_a.empty else int(df_a["id"].max()) + 1

# Choice rows
a_rows = [
    {
        "id": next_choice_id,
        "question_id": question_id_for_choices,
        "content": "City A",
        "is_correct": False,
    },
    {
        "id": next_choice_id + 1,
        "question_id": question_id_for_choices,
        "content": "City B",
        "is_correct": True,
    },
    {
        "id": next_choice_id + 2,
        "question_id": question_id_for_choices,
        "content": "City C",
        "is_correct": False,
    },
]

# Modify DataFrame
df_a = pd.concat([df_a, pd.DataFrame(a_rows)], ignore_index=True)
df_a.to_csv(a_file_path, index=False)

send_df(df_a, dest_table="choices", new_rows=a_rows, file_path=a_file_path,
        by_row=True, vectorization=False)

print(f"Inserted question {question_id_for_choices} with {len(a_rows)} choices.")
