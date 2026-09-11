BASES_VALIDAS = {'A', 'U', 'C', 'G'}
CAP_5 = "m7Gppp"
TAMANHO_POLI_A = 100

CORRETO = "CORRETO"
BUG_SITIO_5 = "BUG - sítio 5' ausente"
BUG_SITIO_3 = "BUG - sítio 3' ausente"
BUG_BRANCH = "BUG - branch point"
BUG_CARACTERE = "BUG - caractere inválido"


def validar_caracteres(RNA):
    if RNA == "":
        return False
    for base in RNA:
        if base not in BASES_VALIDAS:
            return False
    return True


def splicing(RNA):
    RNA = RNA.strip().upper()

    if not validar_caracteres(RNA):
        return BUG_CARACTERE, None

    sitio_5 = -1
    sitio_3 = -1
    cont_A = []
    for i in range(len(RNA) - 1):
        if RNA[i] == 'G' and RNA[i + 1] == 'U' and sitio_5 == -1:
            sitio_5 = i

        if sitio_5 != -1:
            if RNA[i] == 'A':
                if RNA[i + 1] == 'G' and sitio_3 == -1:
                    sitio_3 = i
                else:
                    cont_A.append(i)

    if sitio_5 == -1:
        return BUG_SITIO_5, None

    if sitio_3 == -1:
        return BUG_SITIO_3, None

    branch = False
    for i in cont_A:
        if 10 <= (sitio_3 - i) <= 30:
            branch = True

    if not branch:
        return BUG_BRANCH, None

    exon_1 = RNA[:sitio_5]
    exon_2 = RNA[sitio_3 + 2:]
    poli_A = "A" * TAMANHO_POLI_A

    mRNA = CAP_5 + exon_1 + exon_2 + poli_A

    return CORRETO, mRNA
