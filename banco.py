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

DATABASE = "sqlite:///nexus_clientes.db"


engine = create_engine(
    DATABASE,
    connect_args={
        "check_same_thread": False
    }
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
    "Banco NEXUS atualizado com sucesso!"
)