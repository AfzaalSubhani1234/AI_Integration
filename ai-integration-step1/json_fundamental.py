import json

students={
    "name": "Ali",
    "grade": 12,
    "subjects": ["Python", "Django", "AI"],
    "is_active": True,
    "favorite_subject": "Python"

}

json_text=json.dumps(students)

student_data=json.loads(json_text)

print("\nStudent Name:", student_data["name"])
print("Grade:", student_data["grade"])
print("Subjects:", student_data["subjects"])
print("Favorite Subject:", student_data["favorite_subject"])



