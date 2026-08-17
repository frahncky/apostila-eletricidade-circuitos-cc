#!/usr/bin/env python3
"""Revisão linguística conservadora dos fontes LaTeX da apostila.

O script aplica apenas substituições editoriais de alta confiança. Ele não altera
fórmulas, valores numéricos, circuitos, níveis de dificuldade nem a estrutura dos
ambientes LaTeX. É idempotente: executá-lo novamente não produz novas mudanças.
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXCLUIR = {"gerado-questoes.tex", "gerado-resolucoes.tex"}

# Substituições globais seguras e de padronização técnico-didática.
SUBSTITUICOES = [
    ("Circuitos série", "Circuitos em série"),
    ("Circuitos paralelo", "Circuitos em paralelo"),
    ("circuitos série", "circuitos em série"),
    ("circuitos paralelo", "circuitos em paralelo"),
    ("RLC série", "RLC em série"),
    ("RLC paralelo", "RLC em paralelo"),
    ("resistor série", "resistor em série"),
    ("resistores série", "resistores em série"),
    ("resistência série", "resistência em série"),
    ("resistências série", "resistências em série"),
    ("estágio série RLC", "estágio RLC em série"),
    ("No série,", "No circuito RLC em série,"),
    ("No paralelo,", "No circuito RLC em paralelo,"),
    ("Para achar ", "Para determinar "),
    ("para achar ", "para determinar "),
    ("uma vez achado", "uma vez obtido"),
    ("refazer as contas", "refazer os cálculos"),
    ("Confere.", "Resultado consistente."),
    ("\\gabarito[11.", "\\gabarito[12."),
]

# Correções contextuais. Mantidas como correspondências exatas para evitar
# reescritas indiscriminadas em trechos com significado técnico diferente.
SUBSTITUICOES_EXATAS = [
    (
        "a carga \"puxa\" a tensão para baixo. Divisores resistivos só",
        "a conexão da carga reduz a tensão de saída. Divisores resistivos só",
    ),
    (
        "Direto pela fórmula do divisor:",
        "Aplicando diretamente a fórmula do divisor:",
    ),
    (
        "Ele deixa de conduzir e some do circuito.",
        "Ele deixa de conduzir e pode ser desconsiderado no circuito equivalente.",
    ),
    (
        "Aqui, $25 \\ge 24$ --- passou\nraspando!",
        "Aqui, $25 \\ge 24$ --- a condição é satisfeita por pequena margem.",
    ),
    (
        "um elétron leva quase meia hora para andar um metro!",
        "um elétron leva aproximadamente 23 minutos para percorrer um metro.",
    ),
    (
        "Qual essa potência máxima?",
        "Qual é o valor dessa potência máxima?",
    ),
    (
        "A carga de \\SI{4}{\\ohm}\nentrega \\SI{16}{\\watt}, um pouco abaixo do máximo",
        "A carga de \\SI{4}{\\ohm}\ndissipa \\SI{16}{\\watt}, um pouco abaixo do máximo",
    ),
    (
        "Com $R_L = R_{\\text{Th}}$, a corrente se divide igualmente e a mesma\npotência dissipada na carga é dissipada \\emph{internamente} em $R_{\\text{Th}}$.",
        "Com $R_L = R_{\\text{Th}}$, a mesma corrente percorre as duas resistências e,\ncomo elas têm o mesmo valor, a potência dissipada na carga é igual à potência\ndissipada \\emph{internamente} em $R_{\\text{Th}}$.",
    ),
    (
        "o capacitor mede a tensão do divisor:",
        "a tensão no capacitor corresponde à tensão do divisor:",
    ),
    (
        "O capacitor foi medido e está\npróximo do nominal.",
        "A capacitância medida está\npróxima do valor nominal.",
    ),
    (
        "Como o resistor nominal é \\SI{5}{\\kilo\\ohm}, existe aproximadamente\n\\SI{3}{\\kilo\\ohm} adicional.",
        "Como o resistor nominal é de \\SI{5}{\\kilo\\ohm}, há uma resistência\nadicional de aproximadamente \\SI{3}{\\kilo\\ohm}.",
    ),
    (
        "Isso pode vir de resistência de saída da fonte,\nrede de polarização esquecida, resistor em série, chave/sensor ou uma topologia",
        "Essa diferença pode decorrer da resistência de saída da fonte, de uma\nrede de polarização não considerada, de um resistor em série, de uma chave ou\nsensor, ou de uma topologia",
    ),
    (
        "Com diodo ideal, a descarga vê\naproximadamente o cobre da bobina:",
        "Com o diodo ideal, a resistência no caminho de descarga é aproximadamente\na resistência do enrolamento da bobina:",
    ),
    (
        "ringing/sobressinal",
        "oscilações amortecidas (ringing) e sobressinal",
    ),
    (
        "Resolucoes comentadas",
        "Resoluções comentadas",
    ),
    (
        "\\addcontentsline{toc}{subsection}{Resolucoes",
        "\\addcontentsline{toc}{subsection}{Resoluções",
    ),
    (
        "Selecione questoes ou resolucoes",
        "Selecione questões ou resoluções",
    ),
    (
        "corrente que a fonte de tensão empurraria",
        "corrente que a fonte de tensão forneceria",
    ),
    (
        "a nodal resolveu com \\emph{uma} equação.",
        "a análise nodal exigiu apenas \\emph{uma} equação.",
    ),
    (
        "nao partir um ímã, cada pedaço volta a ter polos norte e sul.",
        "ao partir um ímã, cada pedaço volta a ter polos norte e sul.",
    ),
    (
        "a corrente de magnetização dispara (aquecendo o enrolamento)",
        "a corrente de magnetização aumenta acentuadamente (aquecendo o enrolamento)",
    ),
    (
        "Mede a \"teimosia\" do material em\nmanter seu estado magnético.",
        "Quantifica a resistência do material à desmagnetização.",
    ),
    (
        "Ciclo desejado & \\textbf{estreito} (fino) & \\textbf{largo} (gordo)",
        "Ciclo desejado & \\textbf{estreito} (fino) & \\textbf{largo} (amplo)",
    ),
    (
        "quanto mais larga a área, mais estável ele é.",
        "quanto maior a área do ciclo, maior é sua resistência à desmagnetização.",
    ),
]

# Trechos específicos do capítulo de transitórios que exigem reescrita sintática.
SUBSTITUICOES_CAP11 = [
    (
        "Um indutor de $\\SI{40}{\\milli\\henry}$ vê $R_{\\mathrm{eq}}=\\SI{4}{\\ohm}$ após\numa comutação.",
        "Um indutor de $\\SI{40}{\\milli\\henry}$ está conectado, após uma\ncomutação, a uma rede cuja resistência equivalente vista em seus terminais é\n$R_{\\mathrm{eq}}=\\SI{4}{\\ohm}$.",
    ),
    (
        "Após a supressão das fontes independentes, um capacitor de\n$C=\\SI{20}{\\micro\\farad}$ enxerga $R_3=\\SI{1}{\\kilo\\ohm}$ em série com o\nparalelo de $R_1=\\SI{6}{\\kilo\\ohm}$ e $R_2=\\SI{3}{\\kilo\\ohm}$.",
        "Após a supressão das fontes independentes, a resistência vista por um\ncapacitor de $C=\\SI{20}{\\micro\\farad}$ é composta por\n$R_3=\\SI{1}{\\kilo\\ohm}$ em série com o paralelo de\n$R_1=\\SI{6}{\\kilo\\ohm}$ e $R_2=\\SI{3}{\\kilo\\ohm}$.",
    ),
    (
        "Um circuito LC ideal possui $C=\\SI{100}{\\micro\\farad}$ inicialmente a\n$\\SI{10}{\\volt}$ e $L=\\SI{50}{\\milli\\henry}$ com corrente inicial nula.",
        "Um circuito LC ideal possui um capacitor de $C=\\SI{100}{\\micro\\farad}$\ncom tensão inicial de $\\SI{10}{\\volt}$ e um indutor de\n$L=\\SI{50}{\\milli\\henry}$ com corrente inicial nula.",
    ),
    (
        "Em certo instante de um RLC, $C=\\SI{100}{\\micro\\farad}$ está a\n$\\SI{10}{\\volt}$ e $L=\\SI{50}{\\milli\\henry}$ conduz\n$\\SI{0.2}{\\ampere}$.",
        "Em certo instante, o capacitor de $C=\\SI{100}{\\micro\\farad}$ apresenta\ntensão de $\\SI{10}{\\volt}$, enquanto o indutor de\n$L=\\SI{50}{\\milli\\henry}$ conduz corrente de $\\SI{0.2}{\\ampere}$.",
    ),
]


def revisar_texto(texto: str) -> tuple[str, int]:
    alteracoes = 0
    for antigo, novo in SUBSTITUICOES + SUBSTITUICOES_EXATAS + SUBSTITUICOES_CAP11:
        n = texto.count(antigo)
        if n:
            texto = texto.replace(antigo, novo)
            alteracoes += n
    return texto, alteracoes


def arquivos_alvo():
    for padrao in ("*.tex", "*.sty"):
        for caminho in BASE.rglob(padrao):
            if caminho.name in EXCLUIR:
                continue
            yield caminho


def main() -> None:
    total = 0
    arquivos = 0
    for caminho in sorted(set(arquivos_alvo())):
        original = caminho.read_text(encoding="utf-8")
        revisado, n = revisar_texto(original)
        if revisado != original:
            caminho.write_text(revisado, encoding="utf-8")
            arquivos += 1
            total += n
            print(f"{caminho.relative_to(BASE)}: {n} ajuste(s)")
    print(f"Revisão concluída: {total} ajuste(s) em {arquivos} arquivo(s).")


if __name__ == "__main__":
    main()
