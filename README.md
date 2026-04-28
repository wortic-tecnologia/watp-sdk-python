# WATP SDK for Python

SDK minimo em Python para o contrato real atual do WATP.

Escopo desta base:

- envelope de mensagem com dataclass
- tipos aceitos neste scaffold: `HASH_INTEREST`, `HASH_COUNTER`, `HASH_CONCLUDED`, `HASH_CANCELLED`
- helper de hash SHA-256 compativel com o runtime PHP atual
- builders para montar as quatro mensagens principais

Fora de escopo nesta base inicial:

- cliente HTTP
- assinatura criptografica por no
- registry/discovery
- `HASH_PROPOSAL` e `HASH_WAITING_HUMAN`

## Instalacao local

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/watp/sdk/python
python3 -m pip install -e .
```

## Uso rapido

```python
from watp_sdk import build_hash_interest

message = build_hash_interest(
    sku="ABC-1",
    item="Cafe em graos 1kg",
    qty=10,
    unit_price=12.50,
    currency="BRL",
    buyer="site-b",
    buyer_name="Marketplace Buyer",
    buyer_url="https://buyer.example.com",
    billing={
        "company_name": "ACME Compras",
        "email": "compras@acme.example",
    },
    sender="buyer-node-1",
)

print(message.hash)
print(message.to_json(include_nulls=True))
```

Exemplo de conclusao com link de pagamento:

```python
from watp_sdk import build_hash_concluded

message = build_hash_concluded(
    negotiation_id="neg-123",
    previous_hash="3d4279...",
    sku="ABC-1",
    qty=10,
    unit_price=11.90,
    currency="BRL",
    accepted_by="autonomous_agent",
    payment_url="https://supplier.example/checkout/order-pay/321/?pay_for_order=true&key=wc_order_abc",
    sender="supplier-node-1",
)
```

## Compatibilidade de hash

O runtime PHP atual do WATP calcula o hash sobre este objeto JSON, nesta ordem de chaves:

```json
{
  "type": "HASH_INTEREST",
  "payload": { "sku": "ABC-1", "qty": 10, "unit_price": 12.5 },
  "previousHash": null,
  "timestamp": "2026-04-22T00:00:00.000000Z"
}
```

Pontos importantes:

- o SDK preserva a ordem de chaves do payload ao serializar
- o hash nao usa `sort_keys=true`
- para manter compatibilidade, gere o hash e serialize usando o mesmo `MessageEnvelope`

## Estrutura

```text
sdk/python/
  pyproject.toml
  README.md
  watp_sdk/
    __init__.py
    builders.py
    envelope.py
    hashing.py
    types.py
```
