from fastapi import FastAPI
from banco import Session, Cliente, Evento
from pydantic import BaseModel
import random
import string
from datetime import datetime


app = FastAPI(
    title="NEXUS API",
    version="2.0"
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
# INICIO
# =====================================

@app.get("/")
def inicio():

    return {

        "sistema": "NEXUS SERVER",

        "status": "ONLINE"

    }



# =====================================
# GERAR LICENÇA
# =====================================

def gerar_licenca():

    codigo = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=8
        )
    )

    return "NXS-" + codigo



# =====================================
# PRIMEIRO ACESSO AUTOMÁTICO
# =====================================

@app.post("/primeiro_acesso")
def primeiro_acesso(
    dados: PrimeiroAcesso
):

    banco = Session()


    cliente_existente = banco.query(
        Cliente
    ).filter(
        Cliente.id_maquina == dados.id_maquina
    ).first()



    # Se já existe, retorna a licença

    if cliente_existente:

        cliente_existente.ultimo_acesso = datetime.now()

        banco.commit()


        return {

            "liberado": cliente_existente.ativo,

            "licenca": cliente_existente.licenca,

            "cliente": cliente_existente.nome_cliente,

            "mensagem": "Cliente reconhecido"

        }



    # Novo cliente

    nova_licenca = gerar_licenca()


    novo_cliente = Cliente(

        nome_cliente=dados.nome_cliente,

        licenca=nova_licenca,

        id_maquina=dados.id_maquina,

        pc_id=dados.id_maquina,

        nome_pc=dados.nome_pc,

        ativo=True,

        ultimo_acesso=datetime.now()

    )


    banco.add(
        novo_cliente
    )

    banco.commit()

    banco.refresh(
        novo_cliente
    )


    return {

        "liberado": True,

        "licenca": novo_cliente.licenca,

        "cliente": novo_cliente.nome_cliente,

        "mensagem": "Cliente ativado automaticamente"

    }



# =====================================
# VALIDAR LICENÇA
# =====================================

@app.get("/validar/{licenca}")
def validar_licenca(
    licenca: str
):

    banco = Session()


    cliente = banco.query(
        Cliente
    ).filter(
        Cliente.licenca == licenca
    ).first()



    if not cliente:

        return {

            "liberado": False,

            "mensagem": "Licença não encontrada"

        }



    cliente.ultimo_acesso = datetime.now()

    banco.commit()



    return {

        "liberado": cliente.ativo,

        "cliente": cliente.nome_cliente,

        "mensagem":
        "Acesso autorizado"
        if cliente.ativo
        else
        "Licença bloqueada"

    }



# =====================================
# BLOQUEAR
# =====================================

@app.post("/bloquear/{licenca}")
def bloquear(
    licenca: str
):

    banco = Session()


    cliente = banco.query(
        Cliente
    ).filter(
        Cliente.licenca == licenca
    ).first()


    if not cliente:

        return {

            "mensagem": "Cliente não encontrado"

        }


    cliente.ativo = False


    banco.commit()


    return {

        "mensagem": "Cliente bloqueado",

        "cliente": cliente.nome_cliente

    }



# =====================================
# ATIVAR NOVAMENTE
# =====================================

@app.post("/ativar/{licenca}")
def ativar(
    licenca: str
):

    banco = Session()


    cliente = banco.query(
        Cliente
    ).filter(
        Cliente.licenca == licenca
    ).first()



    if not cliente:

        return {

            "mensagem": "Cliente não encontrado"

        }


    cliente.ativo = True


    banco.commit()


    return {

        "mensagem": "Cliente ativado",

        "cliente": cliente.nome_cliente

    }



# =====================================
# EVENTOS
# =====================================

@app.post("/evento")
def evento(
    dados: EventoEntrada
):

    banco = Session()


    cliente = banco.query(
        Cliente
    ).filter(
        Cliente.licenca == dados.licenca
    ).first()



    if not cliente:

        return {

            "mensagem": "Cliente não encontrado"

        }



    novo_evento = Evento(

        cliente=cliente.nome_cliente,

        tipo_evento=dados.evento

    )


    banco.add(
        novo_evento
    )


    banco.commit()



    return {

        "mensagem": "Evento salvo"

    }



# =====================================
# LISTAR CLIENTES
# =====================================

@app.get("/clientes")
def clientes():

    banco = Session()


    lista = banco.query(
        Cliente
    ).all()


    retorno = []


    for cliente in lista:

        retorno.append({

            "id": cliente.id,

            "nome_cliente": cliente.nome_cliente,

            "licenca": cliente.licenca,

            "nome_pc": cliente.nome_pc,

            "ativo": cliente.ativo,

            "ultimo_acesso": cliente.ultimo_acesso

        })


    return retorno
@app.post("/ativar/{licenca}")
def ativar_cliente(licenca: str):

    banco = Session()

    cliente = banco.query(
        Cliente
    ).filter(
        Cliente.licenca == licenca
    ).first()


    if not cliente:

        return {
            "mensagem": "Cliente não encontrado"
        }


    cliente.ativo = True

    banco.commit()


    return {
        "mensagem": "Cliente ativado novamente"
    }
@app.delete("/cliente/{licenca}")
def excluir_cliente(licenca: str):

    banco = Session()

    cliente = banco.query(Cliente).filter(
        Cliente.licenca == licenca
    ).first()

    if not cliente:
        return {
            "mensagem": "Cliente não encontrado"
        }

    banco.delete(cliente)
    banco.commit()

    return {
        "mensagem": "Cliente removido com sucesso"
    }