import json
import re
import requests
from bs4 import BeautifulSoup
from typing import Optional


def extrair_preco_generico(url: str) -> Optional[float]:
    """
    Extrai o preço de uma página de e-commerce utilizando dados estruturados (JSON-LD)
    com fallback para metadados Open Graph (og:price:amount).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, "lxml")

    # Estratégia 1: Busca em Tags de Dados Estruturados (JSON-LD)
    scripts_json_ld = soup.find_all("script", type="application/ld+json")
    for script in scripts_json_ld:
        if not script.string:
            continue
        try:
            dados = json.loads(script.string)
            preco = _processar_json_ld(dados)
            if preco is not None:
                return preco
        except json.JSONDecodeError:
            continue

    # Estratégia 2: Fallback para Metadados Open Graph (og:price)
    meta_og = soup.find("meta", property="og:price:amount") or soup.find(
        "meta", property="product:price:amount"
    )
    if meta_og and meta_og.get("content"):
        return _tratar_valor_numerico(meta_og["content"])

    return None


def _processar_json_ld(dados: dict | list) -> Optional[float]:
    """Navega recursivamente na estrutura JSON-LD para localizar a chave de preço."""
    if isinstance(dados, list):
        for item in dados:
            resultado = _processar_json_ld(item)
            if resultado is not None:
                return resultado
        return None

    if isinstance(dados, dict):
        # Verifica o padrão Schema.org/Product
        if dados.get("@type") == "Product" or "offers" in dados:
            offers = dados.get("offers")
            if isinstance(offers, dict):
                price = offers.get("price") or offers.get("lowPrice")
                if price is not None:
                    return _tratar_valor_numerico(str(price))
            elif isinstance(offers, list) and len(offers) > 0:
                price = offers[0].get("price") or offers[0].get("lowPrice")
                if price is not None:
                    return _tratar_valor_numerico(str(price))

        # Busca recursiva em dicionários aninhados
        for chave, valor in dados.items():
            if isinstance(valor, (dict, list)):
                resultado = _processar_json_ld(valor)
                if resultado is not None:
                    return resultado

    return None


def _tratar_valor_numerico(texto_valor: str) -> Optional[float]:
    """Limpa e converte strings de preço para float tratável."""
    try:
        # Remove caracteres que não sejam dígitos, vírgula ou ponto
        valor_limpo = re.sub(r"[^\d.,]", "", texto_valor)

        # Trata formatação brasileira (1.299,00 -> 1299.00)
        if "," in valor_limpo and "." in valor_limpo:
            valor_limpo = valor_limpo.replace(".", "").replace(",", ".")
        elif "," in valor_limpo:
            valor_limpo = valor_limpo.replace(",", ".")

        return float(valor_limpo)
    except (ValueError, TypeError):
        return None
