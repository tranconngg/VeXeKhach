from fastapi import APIRouter, HTTPException,Request
from app.database import get_user_collection
from app import auth, schemas
from pymongo.errors import DuplicateKeyError
from datetime import timedelta, datetime
from app.auth import verify_password, create_access_token
from app.validators import validate_password, validate_username
from app.email_service import email_service
import secrets
from fastapi import Request
from fastapi.responses import HTMLResponse
from app.schemas import LoginResponse, UserLogin

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, request: Request):
    # Validate username
    is_valid_username, username_message = validate_username(user.username)
    if not is_valid_username:
        raise HTTPException(status_code=400, detail=username_message)

    # Validate password
    is_valid_password, password_message = validate_password(user.password)
    if not is_valid_password:
        raise HTTPException(status_code=400, detail=password_message)

    user_collection = get_user_collection()
    # check email
    existing_user = await user_collection.find_one({
        "$or": [
            {"username": user.username},
            {"email": user.email}
        ]
    })
    
    if existing_user:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email has been registered")
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already in use")

    # Tạo verification token
    verification_token = secrets.token_urlsafe(32)
    current_time = datetime.utcnow()
    hashed_password = auth.hash_password(user.password)
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_email_verified": False,
        "verification_token": verification_token,
        "verification_token_expires": current_time + timedelta(hours=24),
        "created_at": current_time,
        "email_verified_at": None
    }

    try:
        result = await user_collection.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        
        # Gửi email xác thực
        await email_service.send_verification_email(user.email, verification_token)
        
        return schemas.UserResponse(
            id=user_data["_id"], 
            username=user_data["username"], 
            email=user_data["email"],
            created_at=user_data["created_at"],
            email_verified_at=user_data["email_verified_at"],
            is_email_verified=user_data["is_email_verified"]
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email or username already exists!")

@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email(token: str):

    user_collection = get_user_collection()
    user = await user_collection.find_one({
        "verification_token": token,
        "verification_token_expires": {"$gt": datetime.utcnow()}
    })

    if not user:
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>Verification Failed</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .container { max-width: 500px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
                        .error { color: red; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2 class="error">Verification Failed</h2>
                        <p>The verification link is invalid or has expired.</p>
                    </div>
                </body>
            </html>
            """, 
            status_code=400
        )
    current_time = datetime.utcnow()
    await user_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "is_email_verified": True,
                "verification_token": None,
                "verification_token_expires": None,
                "email_verified_at": current_time
            }
        }
    )

    return HTMLResponse(
        content=f"""
        <html>
            <head>
                <title>Email Verified</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .container {{ max-width: 500px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }}
                    h2 {{ color: #2ecc71; }}
                    .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        font-size: 16px;
                        color: white;
                        background-color: #007bff;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Email Successfully Verified</h2>
                    <p>Welcome to <strong>VeXeKhach</strong>, {user['username']}! 🎉</p>
                    <p>Your email <strong>{user['email']}</strong> has been successfully verified.</p>
                </div>
            </body>
        </html>
        """
    )

@router.post("/login", response_model=LoginResponse)
async def login(user: UserLogin):
    users = get_user_collection()
    user_data = await users.find_one({"email": user.email})
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect email or password!")

    if "hashed_password" not in user_data:
        raise HTTPException(status_code=500, detail="User data error: missing password!")
    if not verify_password(user.password, user_data["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password!")
    if not user_data.get("is_email_verified", False):
        raise HTTPException(
            status_code=403, 
            detail="Please verify your email before logging in. Check your inbox for verification."
        )

    access_token = create_access_token(data={"sub": str(user_data["_id"])}, expires_delta=timedelta(minutes=60))
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse(
            id=str(user_data["_id"]),
            username=user_data["username"],
            email=user_data["email"],
            created_at=user_data.get("created_at"),
            email_verified_at=user_data.get("email_verified_at"),
            is_email_verified=user_data.get("is_email_verified", False)
        )
    )
