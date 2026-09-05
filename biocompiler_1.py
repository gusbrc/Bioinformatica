def validar_sequencia(RNA):
    tam = len(RNA)
    flag1 = True
    flag2 = False
    flag3 = False
    flag4 = (tam % 3 == 0) #Teste para o caso 5
    flag5 = True

    i = 0
    for base in RNA:
        #Teste para o CASO 2:
        if base not in ['A', 'T', 'C', 'G']:
            flag1 = False

        #Teste para o CASO 3:
        if not flag2:
            if i >= 2:
                if RNA[i - 2:i + 1] == 'ATG' and (i - 2) % 3 == 0:
                    flag2 = True
                    start = i - 2

        #Teste para o CASO 4 e 6:
        else:
            if RNA[i-2:i+1] in ['TAA', 'TAG', 'TGA'] and (i - 2) % 3 == 0:
                flag3 = True
                if i + 1 < tam:
                    flag5 = False
        i += 1

    if flag1 and flag2 and flag3 and flag4 and flag5:
        return 'CORRETO', RNA[start:tam].replace('T', 'U')
    elif not flag1:
        return 'BUG - base inválida', None
    elif not flag2:
        return 'BUG - START ausente', None
    elif not flag4:
        return 'BUG - frameshift', None
    elif not flag3:
        return 'BUG - STOP ausente', None
    elif not flag5:
        return 'BUG - nonsense / STOP prematuro', None
    