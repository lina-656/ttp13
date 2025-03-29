# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./test.db"  # Используем SQLite для простоты

# Создаем базовый класс для моделей
Base = declarative_base()

# Определяем модель данных Todo
class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)

# Создаем сущность базы данных
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Создаем объект FastAPI
app = FastAPI()

# Создаем класс для входных данных
class TodoCreate(BaseModel):
    title: str
    description: str

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# Создаем объект SessionLocal для получения сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoModel(title=todo.title, description=todo.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db_todo.title = todo.title
    db_todo.description = todo.description
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
