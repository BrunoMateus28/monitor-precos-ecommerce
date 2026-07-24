# 🛒 Serverless Price Monitor Pipeline

Um pipeline de dados autônomo e de custo zero (Serverless) desenvolvido para extrair, armazenar e alertar sobre flutuações de preços em e-commerces.

Este projeto demonstra a aplicação prática de Engenharia de Dados, CI/CD e Web Scraping resiliente, utilizando metadados estruturados para evitar quebras por mudanças de layout visual nos sites.

## 🏗️ Arquitetura do Projeto

O sistema foi desenhado para rodar 100% na nuvem sem necessidade de infraestrutura dedicada (como instâncias EC2 ou bancos de dados gerenciados pagos).

* **Orquestração & CI/CD:** GitHub Actions (Cron Jobs)
* **Extração de Dados:** Python (`requests`, `BeautifulSoup`, JSON-LD)
* **Armazenamento:** SQLite3 (Persistido via automação no próprio repositório)
* **Mensageria:** API do Telegram

## ⚙️ Fluxo de Execução (ETL)

1. **Extract (Extração Resiliente):** O script lê uma lista de URLs cadastradas no banco de dados e faz requisições HTTP. Em vez de depender de seletores CSS frágeis, o motor busca por tags de dados estruturados padronizadas pelo mercado (`Schema.org/Product` via `JSON-LD` ou metadados genéricos `Open Graph`). Isso torna o scraper universal para quase qualquer loja virtual.
2. **Transform (Limpeza):** Os dados retornados são parseados e sanitizados (remoção de caracteres não numéricos e padronização de casas decimais) usando expressões regulares (RegEx).
3. **Load (Carga):** O preço histórico e a data da coleta são inseridos de forma relacional no banco de dados `monitor_precos.db`.
4. **Alert (Regra de Negócio):** Se o preço coletado for menor ou igual ao preço alvo definido pelo usuário, um payload é enviado para o Bot do Telegram, notificando a queda de preço em tempo real com o link direto de compra.
5. **State Persistence:** Para manter o custo de nuvem zerado, o fluxo do GitHub Actions comita silenciosamente o arquivo `.db` atualizado de volta no repositório ao fim de cada execução.

## 🚀 Como Executar Localmente

### Pré-requisitos
* Python 3.11+
* Token de um Bot do Telegram e o Chat ID de destino.

### Passos
1. Clone o repositório:
```bash
git clone https://github.com/BrunoMateus28/monitor-precos-ecommerce.git
cd monitor-precos-ecommerce

```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

```

3. Instale as dependências:

```bash
pip install -r requirements.txt

```

4. Configure as chaves de ambiente:
Crie um arquivo `.env` na raiz do projeto baseado no `.env.template` e insira suas credenciais do Telegram.
5. Execute o pipeline:

```bash
python main.py

```

## 🔒 Segurança

As credenciais de produção não são versionadas. O projeto utiliza a biblioteca `python-dotenv` para desenvolvimento local e o gerenciamento de **GitHub Secrets** para a injeção segura de chaves de API durante a execução do workflow na nuvem. Um hook de `pre-commit` está configurado para impedir o vazamento acidental de chaves privadas no código-fonte.
