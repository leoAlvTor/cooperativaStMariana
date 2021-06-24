import uvicorn
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from datetime import datetime

from model.model import Base, Usuario, Trabajo, DerechoAgua
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_session():
    engine = create_engine('mysql://admin:patito.local@localhost/coop_st_mariana')
    Base.metadata.create_all(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


from fastapi import FastAPI, File, UploadFile, HTTPException
from starlette.middleware.cors import CORSMiddleware
from model.api_model import Usuario_API, Usuario_Login_API, Usuario_Get, Derecho_Create_API, Derecho_Get

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
)


@app.post('/register/', status_code=200)
async def register(usuario: Usuario_API):
    try:
        print(usuario.__repr__())
        session = create_session()
        usuario = Usuario(id=usuario.id, nombre=usuario.nombre, apellido=usuario.apellido, direccion=usuario.direccion,
                          correo=usuario.correo,
                          password=usuario.password, rol='cliente')
        session.add(usuario)
        session.commit()
        session.close()

        return {'ESTADO': 'Correcto!'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400)


@app.post('/login/')
async def login(usuario: Usuario_Login_API):
    print(usuario.__repr__())
    session = create_session()
    try:
        result: Usuario = session.query(Usuario).filter(Usuario.correo == usuario.correo,
                                                        Usuario.password == usuario.password).one()
        session.close()
        return {'ESTADO': 'CORRECTO', 'id': result.id, 'nombre': result.nombre, 'apellido': result.apellido,
                'direccion': result.direccion,
                'correo': result.correo, 'rol': result.rol}
    except MultipleResultsFound as mrf:
        raise HTTPException(status_code=404, detail="Hay mas de un registro con los datos")
    except NoResultFound as nrf:
        print('ERROR: No hay resultados!')
        raise HTTPException(status_code=404, detail='No hay ningun usuario')


@app.post('/user/update')
async def user_update(usuario: Usuario_Login_API):

    ...


@app.post('/derecho/create')
async def derecho_create(derecho: Derecho_Create_API):
    session = create_session()
    try:
        print(derecho.fecha_adquisicion)
        derecho_agua = DerechoAgua(fechaAdquisicion=datetime.strptime(derecho.fecha_adquisicion, '%d/%m/%Y'), numeroMedidor=derecho.numero_medidor,
                                   usuario_id=derecho.usuario_id)
        session.add(derecho_agua)
        session.commit()
        session.close()
        return {'Hola': 'Al parecer si se guardo bien ajio ajio'}
    except Exception as e:
        print(e)
        print('ERRORRRRRRRRRRRRRR')
    ...


@app.get('/user/users', response_model=list[Usuario_Get])
async def user_get():
    session = create_session()
    try:
        result = session.query(Usuario).all()
        usuarios = []
        for rst in result:
            usuario = {'id': rst.id, 'nombre': rst.nombre, 'apellido': rst.apellido,
                             'direccion': rst.direccion, 'correo': rst.correo}
            usuarios.append(usuario)
        return usuarios
    except Exception as e:
        print(e)


@app.get('/derecho/derechos', response_model=list[Derecho_Get])
async def derecho_get():
    session = create_session()
    try:
        result = session.query(DerechoAgua).all()
        usuarios = []
        for rst in result:
            usuario = {'id': rst.id, 'fecha': str(rst.fechaAdquisicion), 'numero_medidor': rst.numeroDeMedidor, 'usuario_id': rst.usuario_id}
            usuarios.append(usuario)
        return usuarios
    except Exception as e:
        print(e)

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', reload=True)
