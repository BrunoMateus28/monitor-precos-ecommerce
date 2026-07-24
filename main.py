import os
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


def cadastrar_produtos_iniciais():
    """Cadastra a sua curadoria inicial de produtos de skincare no banco."""
    produtos_iniciais = [
        {
            "nome": "creme de pentear ondulando a juba",
            "url": "https://lojawidicare.com.br/produtos/creme-de-pentear-ondulando-a-juba-500ml",
        },
        {
            "nome": "protetor solar facial biore",
            "url": "https://www.drogariavenancio.com.br/protetor-solar-biore-uv-aqua-rich-watery-essence-50g/p",
        },
        {
            "nome": "acido salicilico creamy",
            "url": "https://www.creamy.com.br/acido-salicilico-1/p",
        },
    ]

    for p in produtos_iniciais:
        try:
            inserir_produto_teste(nome=p["nome"], url=p["url"])
        except Exception:
            pass  # Evita erro caso o produto já exista na base


def rodar_pipeline() -> None:
    print("=== Inicializando Pipeline de Monitoramento de Skincare ===")
    inicializar_banco()

    # Garante que a sua lista de produtos curados esteja cadastrada
    cadastrar_produtos_iniciais()

    produtos = buscar_produtos_ativos()
    print(f"Total de produtos ativos para monitoramento: {len(produtos)}\n")

    for id_prod, nome, url in produtos:
        print(f"Processando: {nome}")

        preco_atual = extrair_preco_generico(url)

        if preco_atual is not None and preco_atual > 0:
            print(f"Preço Coletado: R$ {preco_atual:.2f}")

            # Registra o preço atual no histórico do banco
            registrar_historico(id_prod, preco_atual)

            # Delega a inteligência de verificação ao banco de dados
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
