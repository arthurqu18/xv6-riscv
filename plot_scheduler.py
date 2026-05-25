#!/usr/bin/env python3
"""
Gera gráfico do escalonador loteria a partir da saída do testscheduler.

Uso:
    python3 plot_scheduler.py scheduler_output.txt
    cat scheduler_output.txt | python3 plot_scheduler.py
"""
import sys
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def parse(text):
    sections = []
    cur = None
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r'=== TEST tickets (\d+):(\d+):(\d+)', line)
        if m:
            if cur and cur['rows']:
                sections.append(cur)
            cur = {'tickets': tuple(int(x) for x in m.groups()), 'rows': []}
        elif cur and re.fullmatch(r'\d+,\d+,\d+,\d+', line):
            cur['rows'].append(list(map(int, line.split(','))))
    if cur and cur['rows']:
        sections.append(cur)
    return sections


def moving_avg(data, w=5):
    result = []
    for i in range(len(data)):
        start = max(0, i - w + 1)
        result.append(sum(data[start:i+1]) / (i - start + 1))
    return result


def plot(sections, outfile='scheduler_graph.png'):
    sec = sections[0]
    ta, tb, tc = sec['tickets']
    total_tickets = ta + tb + tc
    rows = sec['rows']

    times = [r[0] for r in rows]
    cumA  = [r[1] for r in rows]
    cumB  = [r[2] for r in rows]
    cumC  = [r[3] for r in rows]

    min_t = min(ta, tb, tc)
    ratio = f'{ta//min_t}:{tb//min_t}:{tc//min_t}'

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle(
        f'Escalonador Loteria — Tickets {ta}:{tb}:{tc}  (razão {ratio})',
        fontsize=14, fontweight='bold'
    )

    # --- subplot superior: ticks acumulados ---
    ax1.plot(times, cumA, 'b-o', ms=4, lw=2, label=f'Processo A — {ta} tickets')
    ax1.plot(times, cumB, 'r-s', ms=4, lw=2, label=f'Processo B — {tb} tickets')
    ax1.plot(times, cumC, 'g-^', ms=4, lw=2, label=f'Processo C — {tc} tickets')
    ax1.set_ylabel('Ticks acumulados')
    ax1.set_title('Ticks acumulados ao longo do tempo')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # --- subplot inferior: fatia de ticks por amostra ---
    n = len(rows)
    incA = [cumA[0]] + [cumA[i] - cumA[i-1] for i in range(1, n)]
    incB = [cumB[0]] + [cumB[i] - cumB[i-1] for i in range(1, n)]
    incC = [cumC[0]] + [cumC[i] - cumC[i-1] for i in range(1, n)]
    tot  = [incA[i] + incB[i] + incC[i] for i in range(n)]

    def pct(inc):
        return [inc[i] / tot[i] * 100 if tot[i] > 0 else 0 for i in range(n)]

    pA, pB, pC = pct(incA), pct(incB), pct(incC)
    expA = ta / total_tickets * 100
    expB = tb / total_tickets * 100
    expC = tc / total_tickets * 100

    # valores brutos (transparentes)
    ax2.plot(times, pA, 'b-o', ms=3, lw=1, alpha=0.3)
    ax2.plot(times, pB, 'r-s', ms=3, lw=1, alpha=0.3)
    ax2.plot(times, pC, 'g-^', ms=3, lw=1, alpha=0.3)

    # média móvel (sólida)
    ax2.plot(times, moving_avg(pA), 'b-', lw=2,
             label=f'A — {ta} tickets (esperado {expA:.0f}%)')
    ax2.plot(times, moving_avg(pB), 'r-', lw=2,
             label=f'B — {tb} tickets (esperado {expB:.0f}%)')
    ax2.plot(times, moving_avg(pC), 'g-', lw=2,
             label=f'C — {tc} tickets (esperado {expC:.0f}%)')

    # linhas de referência esperadas
    ax2.axhline(expA, color='b', ls='--', alpha=0.6, lw=1)
    ax2.axhline(expB, color='r', ls='--', alpha=0.6, lw=1)
    ax2.axhline(expC, color='g', ls='--', alpha=0.6, lw=1)

    ax2.set_xlabel('Amostra')
    ax2.set_ylabel('Fatia de ticks (%)')
    ax2.set_title('Fatia de ticks por amostra (tracejado = valor esperado, sólido = média móvel)')
    ax2.set_ylim(0, 100)
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    print(f'Gráfico salvo em {outfile}')


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            text = f.read()
    else:
        print('Lendo do stdin... (Ctrl+D para terminar)', file=sys.stderr)
        text = sys.stdin.read()

    sections = parse(text)
    if not sections:
        print('Nenhum dado encontrado. Verifique se o arquivo contém a saída do testscheduler.',
              file=sys.stderr)
        sys.exit(1)

    print(f'{len(sections)} seção(ões) encontrada(s). Usando a primeira ({sections[0]["tickets"]}).',
          file=sys.stderr)
    plot(sections)


if __name__ == '__main__':
    main()
