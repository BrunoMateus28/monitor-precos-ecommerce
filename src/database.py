import sqlite3
from datetime import datetime, timedelta


def conectar_banco():
    return sqlite3.connect("database.db")


def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_precos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            preco REAL NOT NULL,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """
    )
    conn.commit()
    conn.close()


def inserir_produto_teste(nome, url):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO produtos (nome, url)
        VALUES (?, ?)
    """,
        (nome, url),
    )
    conn.commit()
    conn.close()


def buscar_produtos_ativos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, url FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos


def registrar_historico(produto_id, preco):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO historico_precos (produto_id, preco)
        VALUES (?, ?)
    """,
        (produto_id, preco),
    )
    conn.commit()
    conn.close()


def verificar_alertas(produto_id, preco_atual):
    """Valida os alertas comparando com o histórico anterior (ignorando o registro inserido no momento)."""
    conn = conectar_banco()
    cursor = conn.cursor()

    # 1. Menor preço histórico (ignorando o preço atual que acabou de entrar, se já foi inserido)
    cursor.execute(
        """
        SELECT MIN(preco) FROM historico_precos
        WHERE produto_id = ? AND id NOT IN (
            SELECT id FROM historico_precos WHERE produto_id = ? ORDER BY data_coleta DESC LIMIT 1
        )
    """,
        (produto_id, produto_id),
    )
    resultado_min = cursor.fetchone()
    menor_historico = (
        resultado_min[0]
        if resultado_min and resultado_min[0] is not None
        else preco_atual
    )

    # 2. Média de preço dos últimos 30 dias
    trinta_dias_atras = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT AVG(preco) FROM historico_precos
        WHERE produto_id = ? AND data_coleta >= ?
    """,
        (produto_id, trinta_dias_atras),
    )
    resultado_avg = cursor.fetchone()
    media_30d = (
        resultado_avg[0]
        if resultado_avg and resultado_avg[0] is not None
        else preco_atual
    )

    # 3. O último preço real ANTES desta execução (pegando o segundo mais recente do banco)
    cursor.execute(
        """
        SELECT preco FROM historico_precos
        WHERE produto_id = ?
        ORDER BY data_coleta DESC LIMIT 1 OFFSET 1
    """,
        (produto_id,),
    )
    resultado_ultimo = cursor.fetchone()
    ultimo_preco = (
        resultado_ultimo[0]
        if resultado_ultimo and resultado_ultimo[0] is not None
        else preco_atual
    )

    conn.close()

    alerta_disparado = False
    motivos = []

    if preco_atual < menor_historico:
        alerta_disparado = True
        motivos.append("📉 Menor preço histórico registrado!")

    if preco_atual < media_30d and preco_atual < ultimo_preco:
        alerta_disparado = True
        motivos.append(f"📊 Abaixo da média de 30 dias (R$ {media_30d:.2f}).")

    return alerta_disparado, motivos
