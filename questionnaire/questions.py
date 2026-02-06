from tools.toolbi import update_questions_and_choices

question = {
    "object_id": "c2066684-0347-5861-b51d-0000930ec73a",
    "title": "What is the capital of X?",
    "body": "Choose the correct answer",
    "explanation": "Because of Y",
    "difficulty": 3,
    "sponsor": "",
    "sponsor_body": "",
    "sponsor_link": "",
    "is_active": True,
}

choices = [
    {"question_id": 1, "content": "City A", "is_correct": False},
    {"question_id": 1, "content": "City B", "is_correct": True},
    {"question_id": 1, "content": "City C", "is_correct": False},
]

update_questions_and_choices(
    questions=[question],
    choices=choices,
    overwrite_existing=True
)
