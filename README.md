# 🛒 Serverless Price Monitor Pipeline

Um pipeline de dados autônomo e de custo zero (Serverless) desenvolvido para extrair, armazenar e monitorar flutuações de preços em e-commerces, focado em alertas inteligentes de oportunidades para skincare e produtos de consumo.

Este projeto demonstra a aplicação prática de Engenharia de Dados, CI/CD, Web Scraping resiliente e análise de séries temporais em bancos relacionais leves.

## 🏗️ Arquitetura do Projeto

O sistema foi desenhado para rodar 100% na nuvem sem necessidade de infraestrutura dedicada (como instâncias EC2 ou bancos de dados gerenciados pagos).

* **Orquestração & CI/CD:** GitHub Actions (Cron Jobs)
* **Ingestão Dinâmica:** Google Sheets API (Exportação pública via CSV)
* **Extração de Dados:** Python (`requests`, `BeautifulSoup`, JSON-LD)
* **Armazenamento:** SQLite3 local persistido com histórico de preços relacional
* **Mensageria:** API do Telegram para alertas em tempo real

## ⚙️ Fluxo de Execução (ETL) & Inteligência de Alerta

1. **Sincronização de Itens:** O pipeline inicia fazendo o download dinâmico de um arquivo CSV gerado via Google Sheets público. Os novos produtos (nomes e URLs) são inseridos ou ignorados (se já existentes) diretamente no banco relacional `database.db`. Isso elimina a necessidade de alterar o código para modificar os itens monitorados.
2. **Extract (Extração Resiliente):** O script varre as URLs ativas usando rotação de User-Agents para contornar bloqueios de WAF. O motor prioriza dados estruturados padronizados (`Schema.org/Product` via `JSON-LD`) para capturar o preço sem quebrar por mudanças visuais no HTML do e-commerce.
3. **Transform (Limpeza):** Os valores brutos coletados são higienizados usando expressões regulares (RegEx), tratando formatações regionais e garantindo a tipagem flutuante em reais (BRL).
4. **Load (Carga):** O preço capturado é gravado na tabela `historico_precos`.
5. **Alert (Regras Inteligentes baseadas em Séries Temporais):** A regra de negócio analisa o comportamento do preço ignorando o registro atual que acabou de entrar (usando `OFFSET 1` na query). O alerta via Telegram só é disparado se o valor atual for menor que:
   * O **menor preço histórico** já registrado; ou
   * A **média de preço dos últimos 30 dias** simultaneamente com o **último preço coletado** anterior (garantindo uma curva real de queda).
6. **State Persistence:** O GitHub Actions realiza o commit silencioso do arquivo `database.db` atualizado de volta para o repositório, mantendo o estado do histórico vivo sem custos.

## 🚀 Como Executar Localmente

### Pré-requisitos
* Python 3.11+
* Token de um Bot do Telegram e o Chat ID de destino.
* URL de publicação em CSV de uma planilha do Google Sheets.

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
Crie um arquivo `.env` na raiz do projeto baseado no `.env.template` e insira suas credenciais:

```env
TELEGRAM_TOKEN="seu_token_aqui"
TELEGRAM_CHAT_ID="seu_chat_id_aqui"
GOOGLE_SHEETS_CSV_URL="[https://docs.google.com/spreadsheets/d/e/.../pub?output=csv](https://docs.google.com/spreadsheets/d/e/.../pub?output=csv)"

```

5. Execute o pipeline:

```bash
python main.py

```

## 🔒 Segurança

As credenciais de produção não são versionadas. O projeto utiliza a biblioteca `python-dotenv` para desenvolvimento local e o gerenciamento de **GitHub Secrets** para a injeção segura de chaves de API durante a execução do workflow na nuvem. Um hook de `pre-commit` está configurado para impedir o vazamento acidental de chaves privadas no código-fonte.
