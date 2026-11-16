"""Analise reproduzivel de vendas ficticias; apenas biblioteca padrao."""
import csv
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent

def brl(cents):
    return f"R$ {cents / 100:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def analyze(rows):
    monthly, products = defaultdict(int), defaultdict(int)
    total = units = orders = canceled = 0
    for row in rows:
        if row['status'] == 'cancelado':
            canceled += 1
            continue
        if row['status'] != 'concluido':
            raise ValueError('Status desconhecido')
        qty, price, discount = (int(row[k]) for k in ('quantidade','preco_centavos','desconto_centavos'))
        if qty <= 0 or price < 0 or not 0 <= discount <= qty * price:
            raise ValueError('Valores de venda invalidos')
        revenue = qty * price - discount
        total += revenue
        orders += 1
        units += qty
        monthly[row['data'][:7]] += revenue
        products[row['produto']] += revenue
    return total, orders, units, canceled, dict(sorted(monthly.items())), dict(products)

def main():
    with (BASE / 'vendas.csv').open(encoding='utf-8-sig', newline='') as f:
        total, orders, units, canceled, monthly, products = analyze(csv.DictReader(f))
    best = max(products, key=products.get)
    peak = max(monthly, key=monthly.get)
    lines = ['# Resultados da analise', '', '| Indicador | Valor |', '|---|---:|',
             f'| Receita apos descontos | {brl(total)} |', f'| Pedidos concluidos | {orders} |',
             f'| Ticket medio por pedido | {brl(total / orders if orders else 0)} |',
             f'| Unidades vendidas | {units} |', f'| Pedidos cancelados | {canceled} |', '',
             '## Descobertas e acoes sugeridas', '',
             f'- **{best}** lidera a receita, com {brl(products[best])} ({products[best]/total:.1%} do total). Avaliar disponibilidade de estoque.',
             f'- **{peak}** e o mes de maior receita ({brl(monthly[peak])}). Investigar volume e composicao dos pedidos antes de atribuir uma causa.',
             f'- Cancelamentos representam {canceled/(orders+canceled):.1%} dos pedidos. Em uma base real, coletar motivos para orientar melhorias.', '',
             '## Receita por produto', '', '| Produto | Receita |', '|---|---:|']
    lines += [f'| {name} | {brl(value)} |' for name, value in sorted(products.items(), key=lambda x: -x[1])]
    lines += ['', 'Dados sinteticos: os padroes foram produzidos pelo gerador e nao representam um mercado real. Receita nao e lucro.']
    (BASE / 'RESULTADOS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="440" viewBox="0 0 920 440" role="img" aria-label="Receita mensal de vendas ficticias">',
           '<rect width="920" height="440" fill="#0f172a"/>',
           '<g font-family="Arial, sans-serif" fill="#e2e8f0">',
           '<text x="30" y="35" font-size="24">Receita mensal | Loja ficticia</text>',
           '<text x="30" y="62" font-size="14">2025 - BRL - pedidos concluidos, apos descontos</text>']
    scale = max(monthly.values())
    for i, (month, value) in enumerate(monthly.items()):
        x = 35 + i * 73
        height = value / scale * 250
        svg += [f'<rect x="{x}" y="{355-height:.1f}" width="48" height="{height:.1f}" rx="5" fill="#38bdf8"/>',
                f'<text x="{x}" y="{345-height:.1f}" font-size="11">{value/100:.0f}</text>',
                f'<text x="{x}" y="380" font-size="12">{month[5:]}/25</text>']
    svg += ['<text x="30" y="420" font-size="12">Fonte: vendas.csv | Dados sinteticos | Eixo das barras inicia em zero</text>', '</g></svg>']
    (BASE / 'receita-mensal.svg').write_text('\n'.join(svg), encoding='utf-8')
    print('Analise concluida: RESULTADOS.md e receita-mensal.svg')

if __name__ == '__main__':
    main()
