# 🛒 Serverless Price Monitor Pipeline

Um pipeline de dados autônomo e de custo zero (Serverless) desenvolvido para extrair, armazenar e monitorar flutuações de preços em e-commerces, focado em alertas inteligentes de oportunidades para skincare e produtos de consumo.

Este projeto demonstra a aplicação prática de Engenharia de Dados, CI/CD, Web Scraping resiliente e análise de séries temporais em bancos relacionais leves.

## 🏗️ Arquitetura do Projeto

O sistema foi desenhado para rodar 100% na nuvem sem necessidade de infraestrutura dedicada (como instâncias EC2 ou bancos de dados gerenciados pagos).

* **Orquestração & CI/CD:** GitHub Actions (Cron Jobs)
* **Extração de Dados:** Python (`requests`, `BeautifulSoup`, JSON-LD)
* **Armazenamento:** SQLite3 local persistido com histórico de preços relacional
* **Mensageria:** API do Telegram para alertas em tempo real

## ⚙️ Fluxo de Execução (ETL) & Inteligência de Alerta

1. **Extract (Extração Resiliente):** O script lê uma lista de URLs curadas cadastradas no banco e faz requisições HTTP utilizando rotação de User-Agents para evitar bloqueios. O motor busca por tags de dados estruturados padronizadas (`Schema.org/Product` via `JSON-LD`) ou seletores de fallback.
2. **Transform (Limpeza):** Os valores brutos coletados são parseados e sanitizados com expressões regulares (RegEx) para garantir o formato numérico correto em reais (BRL).
3. **Load (Carga):** A nova medição é registrada na tabela de histórico de preços do banco `database.db`.
4. **Alert (Regras de Negócio Inteligentes):** O banco de dados avalia o comportamento histórico do produto. O alerta via Telegram só é disparado se o preço atual atender simultaneamente aos critérios de oportunidade:
   * Estar **abaixo da média de preço dos últimos 30 dias**;
   * Estar **mais barato do que o último registro salvo** (evitando falsos positivos e garantindo tendência de queda real).
5. **State Persistence:** Para manter o custo de nuvem zerado, o fluxo do GitHub Actions comita o arquivo do banco de dados atualizado de volta no repositório ao fim de cada ciclo.

## 🚀 Como Executar Localmente

### Pré-requisitos
* Python 3.11+
* Token de um Bot do Telegram e o Chat ID de destino.

### Passos
1. Clone o repositório:
```bash
git clone [https://github.com/BrunoMateus28/monitor-precos-ecommerce.git](https://github.com/BrunoMateus28/monitor-precos-ecommerce.git)
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
