from src.database import (
    inicializar_banco,
    inserir_produto_teste,
    buscar_produtos_ativos,
    registrar_historico,
)
from src.extractor import extrair_preco_generico
from src.notifier import enviar_mensagem_telegram


def rodar_pipeline() -> None:
    print("=== Inicializando Pipeline de Monitoramento de Preços ===")
    inicializar_banco()

    # Inserindo um produto de teste
    url_teste = "https://alternazero.com/produtos/moletom-quinta-essencia/?"
    inserir_produto_teste(
        nome="Moletom Quinta Essência", url=url_teste, preco_alvo=500.0
    )

    produtos = buscar_produtos_ativos()
    print(f"Total de produtos ativos para monitoramento: {len(produtos)}\n")

    for id_prod, nome, url, preco_alvo in produtos:
        print(f"Processando: {nome}")

        preco_atual = extrair_preco_generico(url)

        if preco_atual is not None:
            print(
                f"Preço Coletado: R$ {preco_atual:.2f} | Preço Alvo: R$ {preco_alvo:.2f}"
            )
            registrar_historico(id_prod, preco_atual)

            if preco_atual <= preco_alvo:
                mensagem = (
                    f"🚨 <b>Queda de Preço Detectada!</b>\n\n"
                    f"📦 <b>Produto:</b> {nome}\n"
                    f"💰 <b>Preço Atual:</b> R$ {preco_atual:.2f}\n"
                    f"🎯 <b>Seu Alvo:</b> R$ {preco_alvo:.2f}\n\n"
                    f"🛒 <a href='{url}'>Clique aqui para comprar</a>"
                )
                enviar_mensagem_telegram(mensagem)
            else:
                print("-> Preço acima da meta. Nenhuma notificação enviada.")
        else:
            print("-> Falha na extração do preço.")
        print("-" * 50)


if __name__ == "__main__":
    rodar_pipeline()
