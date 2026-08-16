from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from banco import Session, Cliente, Evento
from pydantic import BaseModel
from datetime import datetime
import random
import string


app = FastAPI(
    title="NEXUS API",
    version="3.1"
)


# =====================================
# LIBERA SITE / CELULAR / PAINEL WEB
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# MODELOS
# =====================================

class PrimeiroAcesso(BaseModel):
    nome_cliente: str
    id_maquina: str
    nome_pc: str


class EventoEntrada(BaseModel):
    licenca: str
    evento: str



# =====================================
# GERAR LICENÇA
# =====================================

def gerar_licenca():

    return "NXS-" + ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=8
        )
    )



# =====================================
# INICIO
# =====================================

@app.get("/")
def inicio():

    return {
        "sistema":"NEXUS SERVER",
        "status":"ONLINE",
        "versao":"3.1"
    }



# =====================================
# PRIMEIRO ACESSO
# =====================================

@app.post("/primeiro_acesso")
def primeiro_acesso(dados: PrimeiroAcesso):

    banco = Session()

    try:

        cliente = banco.query(
            Cliente
        ).filter(
            Cliente.id_maquina == dados.id_maquina
        ).first()


        if cliente:

            cliente.ultimo_acesso = datetime.now()

            banco.add(
                Evento(
                    cliente=cliente.nome_cliente,
                    tipo_evento="ACESSO_VALIDADO"
                )
            )

            banco.commit()


            return {

                "liberado": cliente.ativo,
                "licenca": cliente.licenca,
                "cliente": cliente.nome_cliente

            }



        cliente = Cliente(

            nome_cliente=dados.nome_cliente,

            licenca=gerar_licenca(),

            id_maquina=dados.id_maquina,

            pc_id=dados.id_maquina,

            nome_pc=dados.nome_pc,

            ativo=True,

            ultimo_acesso=datetime.now()

        )


        banco.add(cliente)

        banco.commit()

        banco.refresh(cliente)



        banco.add(
            Evento(
                cliente=cliente.nome_cliente,
                tipo_evento="PRIMEIRO_ACESSO"
            )
        )

        banco.commit()



        return {

            "liberado": True,
            "licenca": cliente.licenca,
            "cliente": cliente.nome_cliente

        }


    finally:

        banco.close()




# =====================================
# VALIDAR LICENÇA
# =====================================

@app.get("/validar/{licenca}")
def validar(licenca:str):

    banco = Session()

    try:

        cliente = banco.query(
            Cliente
        ).filter(
            Cliente.licenca == licenca
        ).first()



        if not cliente:

            return {
                "liberado":False
            }



        cliente.ultimo_acesso = datetime.now()


        banco.add(
            Evento(
                cliente=cliente.nome_cliente,
                tipo_evento="LICENCA_VALIDADA"
            )
        )


        banco.commit()



        return {

            "liberado":cliente.ativo,

            "cliente":cliente.nome_cliente

        }


    finally:

        banco.close()




# =====================================
# BLOQUEAR
# =====================================

@app.post("/bloquear/{licenca}")
def bloquear(licenca:str):

    banco = Session()


    try:

        cliente = banco.query(
            Cliente
        ).filter(
            Cliente.licenca == licenca
        ).first()



        if cliente:

            cliente.ativo=False


            banco.add(
                Evento(
                    cliente=cliente.nome_cliente,
                    tipo_evento="CLIENTE_BLOQUEADO"
                )
            )


            banco.commit()



            return {
                "mensagem":"Cliente bloqueado",
                "cliente":cliente.nome_cliente
            }



        return {
            "mensagem":"Cliente não encontrado"
        }



    finally:

        banco.close()




# =====================================
# ATIVAR
# =====================================

@app.post("/ativar/{licenca}")
def ativar(licenca:str):

    banco = Session()


    try:

        cliente = banco.query(
            Cliente
        ).filter(
            Cliente.licenca == licenca
        ).first()



        if cliente:

            cliente.ativo=True


            banco.add(
                Evento(
                    cliente=cliente.nome_cliente,
                    tipo_evento="CLIENTE_ATIVADO"
                )
            )


            banco.commit()



            return {
                "mensagem":"Cliente ativado",
                "cliente":cliente.nome_cliente
            }



        return {
            "mensagem":"Cliente não encontrado"
        }



    finally:

        banco.close()




# =====================================
# RECEBER EVENTOS
# =====================================

@app.post("/evento")
def evento(dados:EventoEntrada):

    banco=Session()


    try:

        cliente=banco.query(
            Cliente
        ).filter(
            Cliente.licenca==dados.licenca
        ).first()



        if not cliente:

            return {
                "mensagem":"Cliente não encontrado"
            }



        banco.add(
            Evento(
                cliente=cliente.nome_cliente,
                tipo_evento=dados.evento
            )
        )


        banco.commit()



        return {
            "mensagem":"Evento salvo"
        }


    finally:

        banco.close()




# =====================================
# TODOS EVENTOS
# =====================================

@app.get("/eventos")
def eventos():

    banco=Session()


    try:

        return [

            {

            "cliente":e.cliente,

            "evento":e.tipo_evento,

            "data_hora":e.data_hora

            }

            for e in banco.query(Evento).all()

        ]


    finally:

        banco.close()




# =====================================
# EVENTOS DO CLIENTE
# =====================================

@app.get("/eventos/{cliente}")
def eventos_cliente(cliente:str):

    banco=Session()


    try:

        lista=banco.query(
            Evento
        ).filter(
            Evento.cliente==cliente
        ).all()



        return [

            {

            "evento":e.tipo_evento,

            "data_hora":e.data_hora

            }

            for e in lista

        ]


    finally:

        banco.close()




# =====================================
# CLIENTES
# =====================================

@app.get("/clientes")
def clientes():

    banco=Session()


    try:

        return [

            {

            "id":c.id,

            "nome_cliente":c.nome_cliente,

            "licenca":c.licenca,

            "nome_pc":c.nome_pc,

            "ativo":c.ativo,

            "data_cadastro":c.data_cadastro,

            "ultimo_acesso":c.ultimo_acesso

            }

            for c in banco.query(Cliente).all()

        ]


    finally:

        banco.close()




# =====================================
# EXCLUIR CLIENTE
# =====================================

@app.delete("/cliente/{licenca}")
def excluir_cliente(licenca:str):

    banco=Session()


    try:

        cliente=banco.query(
            Cliente
        ).filter(
            Cliente.licenca==licenca
        ).first()



        if cliente:

            banco.add(
                Evento(
                    cliente=cliente.nome_cliente,
                    tipo_evento="CLIENTE_REMOVIDO"
                )
            )


            banco.delete(cliente)

            banco.commit()



            return {
                "mensagem":"Cliente removido"
            }



        return {
            "mensagem":"Cliente não encontrado"
        }



    finally:

        banco.close()
