from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn, random

app = FastAPI()

# In-memory storage
users = {}
groups = {}


class InviteRequest(BaseModel):
    group_id: int
    inviter_id: int
    target_user_id: int

class JoinRequest(BaseModel):
    group_id: int
    user_id: int


@app.get("/")
def home():
    new_id = random.randint(1000, 9999)

    while new_id in users:
        new_id = random.randint(1000, 9999)

    users[new_id] = {}
    return {"message": f"your id is {new_id}", "user_id": new_id}


@app.post("/make_group")
def create_group(owner_id: int):
    if owner_id not in users:
        raise HTTPException(status_code=400, detail="Owner ID does not exist")

    group_id = random.randint(10000, 99999)
    while group_id in groups:
        group_id = random.randint(10000, 99999)

    groups[group_id] = {
        "owner": owner_id,
        "users": [owner_id],
        "pending": []
    }

    return {"message": f"group {group_id} created", "group_id": group_id}


@app.post("/invite")
def invite_user(req: InviteRequest):
    if req.group_id not in groups:
        raise HTTPException(status_code=400, detail="Group not found")

    group = groups[req.group_id]

    if req.inviter_id != group["owner"]:
        raise HTTPException(status_code=403, detail="Only group owner can invite")

    if req.target_user_id not in users:
        raise HTTPException(status_code=400, detail="Invited user does not exist")

    if req.target_user_id in group["users"]:
        raise HTTPException(status_code=400, detail="User already in group")

    if req.target_user_id in group["pending"]:
        return {"message": "User already invited"}

    group["pending"].append(req.target_user_id)

    return {
        "message": f"User {req.target_user_id} invited",
        "group": group
    }


@app.post("/join_group")
def join_group(req: JoinRequest):
    if req.group_id not in groups:
        raise HTTPException(status_code=400, detail="Group does not exist")

    group = groups[req.group_id]

    if req.user_id not in group["pending"]:
        raise HTTPException(
            status_code=403,
            detail="You are not invited to this group (bruteforce blocked)"
        )

    group["pending"].remove(req.user_id)
    group["users"].append(req.user_id)

    return {
        "message": f"User {req.user_id} joined group {req.group_id}",
        "group": group
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
