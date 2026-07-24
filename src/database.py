import sqlite3
from typing import List, Tuple, Dict, Any

DB_NAME = "monitor_precos.db"


def conectar_banco() -> sqlite3.Connection:
    return sqlite3.connect(DB_NAME)


def inicializar_banco() -> None:
    """Cria as tabelas do sistema seguindo a convenção de banco minúsculo e tabela maiúscula."""
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Tabela de Produtos Cadastrados
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS PRODUTOS_CADASTRADOS (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_produto TEXT NOT NULL,
        url_produto TEXT NOT NULL UNIQUE,
        preco_alvo REAL NOT NULL,
        ativo BOOLEAN DEFAULT 1
    )
    """
    )

    # Tabela de Histórico de Preços
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS HISTORICO_PRECOS (
        id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produto INTEGER NOT NULL,
        preco_coletado REAL NOT NULL,
        data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_produto) REFERENCES PRODUTOS_CADASTRADOS (id_produto)
    )
    """
    )

    conexao.commit()
    conexao.close()


def inserir_produto_teste(nome: str, url: str, preco_alvo: float) -> None:
    """Insere um produto inicial se a URL ainda não existir."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute(
        """
    INSERT OR IGNORE INTO PRODUTOS_CADASTRADOS (nome_produto, url_produto, preco_alvo)
    VALUES (?, ?, ?)
    """,
        (nome, url, preco_alvo),
    )
    conexao.commit()
    conexao.close()


def buscar_produtos_ativos() -> List[Tuple[int, str, str, float]]:
    """Retorna a lista de produtos ativos para monitoramento."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute(
        """
    SELECT id_produto, nome_produto, url_produto, preco_alvo
    FROM PRODUTOS_CADASTRADOS
    WHERE ativo = 1
    """
    )
    produtos = cursor.fetchall()
    conexao.close()
    return produtos


def registrar_historico(id_produto: int, preco: float) -> None:
    """Registra uma nova medição de preço no histórico."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute(
        """
    INSERT INTO HISTORICO_PRECOS (id_produto, preco_coletado)
    VALUES (?, ?)
    """,
        (id_produto, preco),
    )
    conexao.commit()
    conexao.close()
