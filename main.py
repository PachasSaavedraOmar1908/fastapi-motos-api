import os
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from sqlmodel import Field,Session, create_engine, select, SQLModel
from fastapi.staticfiles import StaticFiles

load_dotenv();


#Datos de conexión
db_user = os.getenv('USER_DB')
db_password = os.getenv('PASSWORD')
db_host = os.getenv('HOST_DB')
db_name = os.getenv('DB_NAME')

#Conectar con base de datos
url_connection = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}'
engine = create_engine(url_connection)

#Funcion que llama a SQLModel para que cree la conexión y tablas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

#Trabajar con una conexión por sesion
def get_session():
    with Session(engine) as session:
        yield session

#Preparar y proporcionar las sesiones
session_dep = Annotated[Session, Depends(get_session)]

#Definir modelo para la base de datos
class MotoBase(SQLModel):
    model: str = Field(index = True)
    brand: str = Field(index = True)
    cylinder: int = Field(index = True)
    img: str = Field(index = True)

class Moto(MotoBase, table = True):
    id: int = Field(default=None, primary_key=True)
    propietary: str

class MotoPublic(MotoBase):
    id: int 

class MotoCreate(MotoBase):
    propietary: str

class MotoUpdate(MotoBase):
    model: str | None = None
    brand: str | None = None
    cylinder: int | None = None
    propietary: str | None = None
    img: str | None = None
    
app = FastAPI()

@app.get("/")
def retornar_datos():
    return{
        
    }

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event('startup')
def on_startup():
    create_db_and_tables()

#Crear moto
@app.post("/motos/", response_model = MotoPublic)
def create_moto(moto: MotoCreate, session: session_dep):
    db_moto = Moto.model_validate(moto)
    session.add(db_moto)
    session.commit()
    session.refresh(db_moto)
    return db_moto

#Obtener moto
@app.get("/motos/", response_model = list[MotoPublic])
def get_motos(session: session_dep):
    motos = session.exec(select(Moto))
    return motos

#Obtener moto por id
@app.get("/motos/{id_moto}", response_model = MotoPublic)
def get_moto(id_moto: int, session: session_dep):
    moto = session.get(Moto, id_moto)
    if not moto:
        raise HTTPException(status_code = 404, detail="Moto no encontrada")
    return moto

#Actualizar moto
@app.patch("/motos/{id_moto}", response_model = MotoPublic)
def update_moto(id_moto: int, moto: MotoUpdate,session: session_dep):
    moto_db = session.get(Moto, id_moto)
    if not moto_db:
        raise HTTPException(status_code = 404, detail = "Moto no encontrada")
    moto_data = moto.model_dump(exclude_unset = True)
    moto_db.sqlmodel_update(moto_data)
    session.add(moto_db)
    session.commit()
    session.refresh(moto_db)
    return moto_db

@app.delete("/motos/{id_moto}")
def delete_moto(id_moto: int, session: session_dep):
    moto = session.get(Moto, id_moto)
    if not moto:
        raise HTTPException(status_code = 404, detail = "Moto no econtrada")
    session.delete(moto)
    session.commit()
    return HTTPException(status_code = 200, detail = f"Moto {moto} eliminada correctamente")

