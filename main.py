from src.database import (
    inicializar_banco,
    inserir_produto_teste,
    buscar_produtos_ativos,
    registrar_historico,
)
from src.extractor import extrair_preco_generico


def rodar_pipeline() -> None:
    print("=== Inicializando Pipeline de Monitoramento de Preços ===")
    inicializar_banco()

    # Inserindo um produto de teste
    url_teste = "https://alternazero.com/produtos/moletom-quinta-essencia/?"
    inserir_produto_teste(
        nome="Moletom Quinta Essência", url=url_teste, preco_alvo=350.0
    )

    produtos = buscar_produtos_ativos()
    print(f"Total de produtos ativos para monitoramento: {len(produtos)}\n")

    for id_prod, nome, url, preco_alvo in produtos:
        print(f"Processando: {nome}")
        print(f"URL: {url}")

        preco_atual = extrair_preco_generico(url)

        if preco_atual is not None:
            print(
                f"Preço Coletado: R$ {preco_atual:.2f} | Preço Alvo: R$ {preco_alvo:.2f}"
            )
            registrar_historico(id_prod, preco_atual)

            if preco_atual <= preco_alvo:
                print("-> ALERTA: O produto atingiu o preço desejado!")
            else:
                print("-> Preço acima da meta. Nenhuma notificação enviada.")
        else:
            print("-> Falha na extração do preço.")
        print("-" * 50)


if __name__ == "__main__":
    rodar_pipeline()
