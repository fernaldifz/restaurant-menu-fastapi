from datetime import datetime, timedelta
from typing import Optional

import json
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

#authentication
SECRET_KEY = "5dd606c980b456f773dfb2993fc4b0f517a2eaebf6b3b129e1d4c4604e29a9d8"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

#class
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

with open("menu.json", "r") as read_file:
    data = json.load(read_file)
app = FastAPI()

@app.get('/', tags=["root"])
async def read_root():
    return {"Message": "Welcome! Visit restaurant-menu-fastapi-python.herokuapp.com/docs to try API"}

@app.get('/menu', tags=["menu"])
async def read_all_menu(token: str = Depends(oauth2_scheme)):
    return data['menu']

@app.get('/menu/{item_id}', tags=["menu"])
async def read_menu(item_id: int, token: str = Depends(oauth2_scheme)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

@app.post('/menu', tags=["menu"])
async def add_menu(item_name: str, token: str = Depends(oauth2_scheme)):
    if (len(data['menu']) > 0):
        item_id = data['menu'][len(data['menu'])-1]['id'] + 1
    else:
        item_id = 1
        
    new_data = {'id': item_id, 'name': item_name}
    data['menu'].append(dict(new_data))

    read_file.close()
    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
    write_file.close()

    return (new_data)
    raise HTTPException(
        status_code=500, detail=f'Internal server error'
    )

@app.put('/menu/{item_id}', tags=["menu"])
async def update_menu(item_id: int, item_name: str, token: str = Depends(oauth2_scheme)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            menu_item['name'] = item_name
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()
            return{"message": "Menu item updated"}

    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

@app.delete('/menu/{item_id}', tags=["menu"])
async def delete_menu(item_id: int, token: str = Depends(oauth2_scheme)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()
            return{"message": "Menu item deleted"}

    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(data["users"], username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token, tags=["user"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(data["users"], form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", tags=["user"])
async def create_user(new_user: User):
    user = get_user(data["users"], new_user.username)
    if user:
        return {"message": "Username is not available"}
    else:
        new_data = data
        new_data["users"][new_user.username] = {
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "hashed_password": get_password_hash(new_user.password),
            "disabled": False
        }

        read_file.close()
        with open("menu.json", "w") as write_file:
            json.dump(new_data, write_file, indent=4)
        write_file.close()
        
        return new_data["users"][new_user.username]