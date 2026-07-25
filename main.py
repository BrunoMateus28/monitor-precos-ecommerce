import os
import csv
import requests
from dotenv import load_dotenv

from src.database import (
    inicializar_banco,
    inserir_produto_teste,
    buscar_produtos_ativos,
    registrar_historico,
    verificar_alertas,
)
from src.extractor import extrair_preco_generico
from src.notifier import notificar_promocao

load_dotenv()


def sincronizar_produtos_da_planilha():
    """Baixa o CSV público do Google Sheets e atualiza os produtos no banco de dados."""
    url_csv = os.getenv("GOOGLE_SHEETS_CSV_URL")

    if not url_csv:
        print("-> AVISO: GOOGLE_SHEETS_CSV_URL não configurada. Pulando sincronização.")
        return

    print("-> Sincronizando lista de produtos com o Google Sheets...")
    try:
        response = requests.get(url_csv, timeout=15)
        response.raise_for_status()

        # O decode garante que caracteres com acento (ex: creme de pentear) funcionem perfeitamente
        linhas_csv = response.text.splitlines()
        leitor = csv.DictReader(linhas_csv)

        contador = 0
        for linha in leitor:
            nome = linha.get("nome")
            url = linha.get("url")

            if nome and url:
                inserir_produto_teste(nome=nome.strip(), url=url.strip())
                contador += 1

        print(f"-> Sincronização concluída! {contador} produtos processados do Sheets.")

    except Exception as e:
        print(f"-> Erro ao sincronizar produtos do Google Sheets: {e}")


def rodar_pipeline() -> None:
    print("=== Inicializando Pipeline de Monitoramento de Skincare ===")
    inicializar_banco()

    # Atualiza o banco SQLite com o que estiver na planilha antes de varrer os preços
    sincronizar_produtos_da_planilha()

    produtos = buscar_produtos_ativos()
    print(f"Total de produtos ativos para monitoramento: {len(produtos)}\n")

    for id_prod, nome, url in produtos:
        print(f"Processando: {nome}")

        preco_atual = extrair_preco_generico(url)

        if preco_atual is not None and preco_atual > 0:
            print(f"Preço Coletado: R$ {preco_atual:.2f}")

            # Registra o preço atual no histórico do banco
            registrar_historico(id_prod, preco_atual)

            # Validação inteligente baseada no histórico
            alerta_valido, motivos = verificar_alertas(id_prod, preco_atual)

            if alerta_valido:
                print("-> Oportunidade detectada! Disparando alerta no Telegram...")
                notificar_promocao(
                    produto_nome=nome,
                    preco_atual=preco_atual,
                    url_produto=url,
                    motivos=motivos,
                )
            else:
                print(
                    "-> Preço estável ou sem queda significativa. Nenhuma notificação enviada."
                )
        else:
            print("-> Falha na extração do preço ou produto indisponível.")
        print("-" * 50)


if __name__ == "__main__":
    rodar_pipeline()
