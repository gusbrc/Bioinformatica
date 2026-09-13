# BioCompiler 2.0 — RNA Processor

Simulador didático da maturação do RNA. O programa recebe sequências de pré-mRNA,
reconhece o íntron segundo a convenção didática da atividade (`GU … A … AG`), realiza o
splicing e, quando a sequência é válida, gera o mRNA maduro com CAP 5′ e cauda poli-A.
Quando a sequência não é válida, informa o diagnóstico do problema.

Trabalho da disciplina de Tópicos em Bioinformática.

Esta é a **Fase II** do projeto BioCompiler:

| Fase | Responsável | Transformação |
|------|-------------|---------------|
| I | BioCompiler 1.0 | DNA → pré-mRNA |
| II | **BioCompiler 2.0** | pré-mRNA → mRNA maduro |
| III | Sr. Ribossomo | mRNA → proteína |

---

## Estrutura do projeto

```
.
├── biocompiler_2.py   # motor do 2.0: validação, splicing, CAP 5′ e cauda poli-A
├── app_2.py           # interface web do 2.0 em Streamlit
├── inputs/
│   └── BioCompiler2_entrada_40_casos_modelo_oficial.txt
├── README_2.md        
```

O motor (`biocompiler_2.py`) contém **só a lógica**: não imprime nada, não lê nem grava
arquivos e **não depende de bibliotecas externas**. Nenhum código é executado no momento
do `import`. Toda a apresentação (tela, tabela, exportação) fica no `app_2.py`.

---

## Requisitos

| Uso | Requisitos |
|-----|-----------|
| Motor (`biocompiler_2.py`) | Python 3.8+ (nada além da biblioteca padrão) |
| Interface web (`app_2.py`) | Python 3.8+, `streamlit`, `pandas` |

```bash
pip install streamlit pandas
```

Testado com Python 3.13.14, Streamlit 1.63.0 e pandas 3.0.5. A interface usa parâmetros
recentes do Streamlit (`width="stretch"`, `on_click="ignore"`, `wrap_lines`); em versões
antigas, atualize com `pip install -U streamlit`.

---

## Formato de entrada

Arquivo texto (`.txt`) em UTF-8, com **uma sequência de pré-mRNA por linha**, sem
cabeçalho. As linhas são processadas na ordem em que aparecem.

```
CCUAUGGCUGUAACCUUUAACUAACAAGAUGGCCUAC
CCUAUGGCUCUAACCUUUAAACCUAACAGGAUGGCCUAC
CCUAUGGCUGUCCUUUCCUUCCUUCCAGGAUGGCCUAC
```

- Apenas as bases **A**, **U**, **C** e **G**, sem espaços ou separadores internos.
- Letras minúsculas são aceitas e convertidas para maiúsculas.
- Espaços e quebras de linha nas pontas são removidos.
- Linhas em branco são ignoradas pela interface.

---

## Como usar

### 1. Interface web (Streamlit)

```bash
streamlit run app_2.py
```

Execute o comando a partir da pasta onde estão os arquivos `.py` — o `app_2.py` precisa
encontrar o `biocompiler_2.py` ao lado dele.

No aplicativo:

1. Envie o arquivo `.txt` na aba **Upload de arquivo** ou cole as sequências na aba
   **Colar sequências**.
2. Clique em **Executar BioCompiler 2.0**.
3. Consulte as métricas (total, corretas, com erro, taxa de sucesso), a contagem por
   diagnóstico e a tabela com `linha`, `entrada`, `status`, `resultado` e `mRNA_maduro`.
4. Use **Baixar resultados.txt** para exportar o relatório.
5. Abra **Relatório no formato da especificação** para ver a saída de tela da seção 9.
6. Ative **Mostrar diagnóstico detalhado por entrada** para ver, em cada sequência, qual
   etapa passou (✅), qual falhou (❌) e quais não chegaram a ser verificadas (➖).

A barra lateral resume a convenção didática, os casos reconhecidos e o formato de
entrada.

> O 2.0 não tem modo de linha de comando: o motor é só lógica, e o `resultados.txt` é
> gerado pelo botão de download da interface.

**Saída de tela** (seção 9 da especificação), para as três sequências do exemplo acima:

```
========================================
BIOCOMPILER 2.0 - RNA PROCESSOR
========================================
ENTRADA: 1
STATUS: CORRETO
Sítio 5': OK
Branch point: OK
Sítio 3': OK
Splicing: OK
CAP 5': ADICIONADA
Cauda poli-A: 100 A
mRNA MADURO: m7GpppCCUAUGGCUAUGGCCUACAAAAAAAAAA…
----------------------------------------
ENTRADA: 2
STATUS: ERRO
DIAGNÓSTICO: BUG - sítio 5' ausente
Sítio 5': AUSENTE
Branch point: NÃO VERIFICADO
Sítio 3': NÃO VERIFICADO
Splicing: NÃO REALIZADO
CAP 5': NÃO ADICIONADA
Cauda poli-A: NÃO ADICIONADA
mRNA MADURO: NÃO GERADO
----------------------------------------
ENTRADA: 3
STATUS: ERRO
DIAGNÓSTICO: BUG - branch point
Sítio 5': OK
Branch point: AUSENTE
Sítio 3': OK
Splicing: NÃO REALIZADO
CAP 5': NÃO ADICIONADA
Cauda poli-A: NÃO ADICIONADA
mRNA MADURO: NÃO GERADO
----------------------------------------
```

**Arquivo `resultados.txt`** (seção 11 — UTF-8, campos separados por ponto e vírgula):

```
linha;status;resultado;mRNA_maduro
1;OK;CORRETO;m7GpppCCUAUGGCUAUGGCCUACAAAAAAAAAA…
2;ERRO;BUG - sítio 5' ausente;NÃO GERADO
3;ERRO;BUG - branch point;NÃO GERADO
```

Nos dois exemplos a cauda foi abreviada com `…`; na saída real ela aparece com as 100
adeninas por extenso.

### 2. Como biblioteca

```python
from biocompiler_2 import splicing, CORRETO

diagnostico, mRNA = splicing("CCUAUGGCUGUAACCUUUAACUAACAAGAUGGCCUAC")
print(diagnostico)  # CORRETO
print(mRNA)         # m7Gppp + CCUAUGGCUAUGGCCUAC + 100 × A

diagnostico, mRNA = splicing("CCUAUGGCUCUAACCUUUAAACCUAACAGGAUGGCCUAC")
print(diagnostico)  # BUG - sítio 5' ausente
print(mRNA)         # None
```

Funções públicas:

| Função | Descrição |
|--------|-----------|
| `splicing(RNA)` | Processa uma sequência completa. Devolve `(diagnostico, mRNA_maduro)`; `mRNA_maduro` é `None` em qualquer erro. |
| `validar_caracteres(RNA)` | `True` se a sequência não é vazia e só contém A, U, C e G. |

Constantes (use-as para comparar diagnósticos em vez de redigitar os textos):

| Constante | Valor |
|-----------|-------|
| `CORRETO` | `CORRETO` |
| `BUG_SITIO_5` | `BUG - sítio 5' ausente` |
| `BUG_SITIO_3` | `BUG - sítio 3' ausente` |
| `BUG_BRANCH` | `BUG - branch point` |
| `BUG_CARACTERE` | `BUG - caractere inválido` |
| `CAP_5` | `m7Gppp` |
| `TAMANHO_POLI_A` | `100` |
| `BASES_VALIDAS` | `{'A', 'U', 'C', 'G'}` |

---

## Casos reconhecidos

| Caso | Situação | Resultado |
|------|----------|-----------|
| 1 | `GU … A … AG` com branch point válido | `CORRETO` |
| 2 | `AG` sem `GU` anterior compatível | `BUG - sítio 5' ausente` |
| 3 | `GU` sem `AG` posterior compatível | `BUG - sítio 3' ausente` |
| 4 | `GU` e `AG` presentes, mas nenhum `A` entre 10 e 30 nt antes do `AG` | `BUG - branch point` |
| — | Caractere fora de A/U/C/G, ou sequência vazia | `BUG - caractere inválido` |

Os casos 1 a 4 são os da seção 8 da especificação. O último é uma extensão: a seção 13
manda validar os caracteres, mas a especificação não define o texto desse diagnóstico.

### Ordem de precedência

A classificação é uma cascata: a primeira condição satisfeita determina o resultado.

```
caractere inválido → sítio 5' ausente → sítio 3' ausente → branch point
```

Por isso, um `BUG - branch point` implica que os dois sítios foram encontrados, e um
`BUG - sítio 3' ausente` implica que o sítio 5′ foi encontrado. A interface usa essa
ordem para marcar as etapas como OK, AUSENTE ou NÃO VERIFICADO.

---

## Regras de análise adotadas

**Alfabeto.** A sequência deve conter exclusivamente A, U, C e G. Um único caractere fora
desse conjunto invalida a linha inteira — inclusive `T`, que indica DNA ainda não
transcrito. Sequências vazias também são classificadas como caractere inválido.

**Sítio 5′.** É o **primeiro `GU` da sequência**.

**Sítio 3′.** É o **primeiro `AG` depois do `GU`**. Parar no primeiro `AG` segue o modelo
de varredura do spliceossomo e evita que um `AG` do éxon 2 seja tomado como fim do
íntron.

**Branch point.** Algum `A` entre o `GU` e o `AG` cuja distância até o `AG` esteja entre
**10 e 30 nucleotídeos, inclusive**. A distância é a diferença de posição entre o `A`
candidato e o `A` do `AG`. O próprio `A` do `AG` não conta como candidato.

**Regra do GU falso.** Quando um `AG` aparece antes do primeiro `GU` e nenhum `AG` fecha
o íntron depois desse `GU`, o diagnóstico é `BUG - sítio 5' ausente`, e não
`sítio 3' ausente`. O motivo é que, em `…AGU…`, o `G` pertence ao `AG` e o `GU` formado
com a base seguinte é falso. Exemplo da linha 14 da entrada oficial:

```
UCUCCCCCCCCACCCCCCCCCCCCCCAGUCUCCC
                          ^^^
                          AG + U → o "GU" é falso; não há sítio 5′ real
```

Sem essa regra, as linhas 14, 17 e 40 da entrada oficial cairiam em `sítio 3' ausente`.
Efeito colateral conhecido: um éxon 1 terminado em `A` seguido de um `GU` real, sem `AG`
depois (ex.: `CCAGUCCCCACCCCCCCCCCCC`), também recebe `sítio 5' ausente`, porque `AGU` é
ambíguo. Nenhuma linha da entrada oficial tem essa forma. Se houver `AG` depois do `GU`,
a regra não se aplica e a sequência é analisada normalmente.

**Um íntron por sequência.** O motor reconhece e remove um único íntron (o primeiro `GU`
com o primeiro `AG` seguinte), como em todos os exemplos da especificação.

**Splicing.** Remove do `G` do `GU` até o `G` do `AG`, inclusive, e une os éxons:
`RNA[:sitio_5] + RNA[sitio_3 + 2:]`.

**CAP 5′ e cauda poli-A.** Depois do splicing, o motor acrescenta `m7Gppp` no início e
exatamente 100 `A` no final.

### Exemplo completo

Primeira linha do `entrada.txt` da especificação:

```
pré-mRNA:  CCUAUGGCU  GUAACCUUUAACUAACAAG  AUGGCCUAC
           éxon 1     íntron               éxon 2
                      GU  A (branch, 15 nt antes do AG)  AG

splicing:  CCUAUGGCU + AUGGCCUAC = CCUAUGGCUAUGGCCUAC

mRNA:      m7Gppp + CCUAUGGCUAUGGCCUAC + 100 × A   (124 caracteres)
```

---

## Validação

O motor foi testado contra:

- as três sequências do `entrada.txt` da seção 2 da especificação: `CORRETO`,
  `BUG - sítio 5' ausente` e `BUG - branch point`, com o relatório de tela e o
  `resultados.txt` mostrados acima;
- os quatro exemplos da seção 14 (sem os espaços; no caso 4, sem o `A`), cada um com o
  diagnóstico esperado;
- os limites do branch point: distâncias 10 e 30 aceitas, 9 e 31 rejeitadas;
- a entrada oficial `inputs/BioCompiler2_entrada_40_casos_modelo_oficial.txt`:

| Resultado | Qtd. | Linhas |
|-----------|------|--------|
| `CORRETO` | 10 | 5, 7, 9, 10, 15, 24, 25, 27, 34, 39 |
| `BUG - sítio 5' ausente` | 10 | 2, 4, 8, 14, 17, 18, 20, 30, 32, 40 |
| `BUG - sítio 3' ausente` | 10 | 1, 3, 6, 13, 22, 23, 33, 35, 37, 38 |
| `BUG - branch point` | 10 | 11, 12, 16, 19, 21, 26, 28, 29, 31, 36 |

A entrada oficial não tem gabarito. A distribuição exata de 10 linhas por caso é a
evidência de que as regras adotadas batem com a forma como os casos foram montados.

A interface foi executada de ponta a ponta — entrada colada, processamento, métricas,
relatório e diagnóstico detalhado — sem erros.

---


## Escopo

O BioCompiler 2.0 termina no mRNA maduro. 
