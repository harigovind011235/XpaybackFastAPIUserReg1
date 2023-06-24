from fastapi import FastAPI
from pydantic import BaseModel,EmailStr
from database import get_postgresql_connection, get_mongodb_connection
from fastapi import UploadFile
from typing import Optional
from bson import ObjectId
from bson.binary import Binary

app = FastAPI()

class User(BaseModel):
    id:int
    first_name:str
    last_name:str
    email:EmailStr
    password:str
    phone:int
    profile_picture: Optional[UploadFile]


#POST method for submitting User Data
@app.post("/register")
def register_user(user: User):
    pg_conn = get_postgresql_connection()
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (user.email,))
    email_count = pg_cursor.fetchone()[0]
    pg_conn.close()

    if email_count > 0:
        return {"message": "Email already exists"}
    pg_conn = get_postgresql_connection()
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(
        "INSERT INTO users (first_name, last_name, email, password, phone) VALUES (%s, %s, %s, %s, %s)",
        (user.first_name, user.last_name, user.email, user.password, user.phone),
    )
    pg_conn.commit()
    pg_conn.close()

    mongo_conn = get_mongodb_connection()
    profile_picture = user.profile_picture.file.read()
    file_id = ObjectId()
    mongo_conn["profile_pictures"].insert_one({"_id": file_id, "picture": profile_picture})
    mongo_conn.close()

    pg_conn = get_postgresql_connection()
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(
        "INSERT INTO users (first_name, last_name, email, password, phone, profile_picture_id) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (user.first_name, user.last_name, user.email, user.password, user.phone, str(file_id)),
    )
    pg_conn.commit()
    pg_conn.close()

    return {"message": "User registered successfully"}


# Get method for retrieving individual employee details
@app.get("/users/{user_id}")
def get_user(user_id: int):
    pg_conn = get_postgresql_connection()
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = pg_cursor.fetchone()
    pg_conn.close()

    if not user_data:
        return {"message": "User not found"}

    mongo_conn = get_mongodb_connection()
    profile_picture_doc = mongo_conn["profile_pictures"].find_one({"_id": str(user_id)})
    mongo_conn.close()

    if profile_picture_doc:
        profile_picture = profile_picture_doc["picture"]
        user_data += (Binary(profile_picture),)
    else:
        user_data += (None,)

    user = {
        "id": user_data[0],
        "first_name": user_data[1],
        "last_name": user_data[2],
        "email": user_data[3],
        "password": user_data[4],
        "phone": user_data[5],
        "profile_picture": user_data[6]
    }

    return user