import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


# =====================================
# CONFIGURAÇÃO DO BANCO
# =====================================

DATABASE = os.getenv("DATABASE_URL")


if not DATABASE:
    raise Exception(
        "DATABASE_URL não configurada no servidor."
    )


# Ajuste necessário para PostgreSQL no Render
if DATABASE.startswith("postgres://"):
    DATABASE = DATABASE.replace(
        "postgres://",
        "postgresql://",
        1
    )


engine = create_engine(
    DATABASE
)


Session = sessionmaker(
    bind=engine
)


Base = declarative_base()


# =====================================
# TABELA DE CLIENTES
# =====================================

class Cliente(Base):

    __tablename__ = "clientes"


    id = Column(
        Integer,
        primary_key=True
    )


    nome_cliente = Column(
        String
    )


    licenca = Column(
        String,
        unique=True
    )


    id_maquina = Column(
        String,
        unique=True
    )


    pc_id = Column(
        String
    )


    nome_pc = Column(
        String
    )


    ativo = Column(
        Boolean,
        default=True
    )


    data_cadastro = Column(
        DateTime,
        default=datetime.now
    )


    ultimo_acesso = Column(
        DateTime,
        default=datetime.now
    )



# =====================================
# TABELA DE EVENTOS
# =====================================

class Evento(Base):

    __tablename__ = "eventos"


    id = Column(
        Integer,
        primary_key=True
    )


    cliente = Column(
        String
    )


    tipo_evento = Column(
        String
    )


    data_hora = Column(
        DateTime,
        default=datetime.now
    )



# =====================================
# CRIAR TABELAS
# =====================================

Base.metadata.create_all(
    engine
)


print(
    "Banco NEXUS PostgreSQL atualizado com sucesso!"
)
)
