# BioCompiler 1.0 — DNA Transcriber

Analisador didático de sequências de DNA. O programa recebe sequências, valida sua
estrutura segundo a convenção didática da atividade e, quando a sequência é válida,
gera o pré-mRNA correspondente.

Trabalho da disciplina de Tópicos em Bioinformática.

Este é o **Fase I** do projeto BioCompiler:

| Fase | Responsável | Transformação |
|------|-------------|---------------|
| I | **BioCompiler 1.0** (este software) | DNA → pré-mRNA |
| II | BioCompiler 2.0 | pré-mRNA → mRNA maduro |
| III | Sr. Ribossomo | mRNA → proteína |

---

## Estrutura do projeto

```
.
├── biocompiler_1.py   # motor de análise + interface de linha de comando
├── app.py             # interface web em Streamlit
└── README.md
```

O motor (`biocompiler_1.py`) **não depende de bibliotecas externas** e pode ser
importado com segurança: nenhum código é executado no momento do `import`. O `app.py`
importa dele apenas a função `validar_sequencia`.

---

## Requisitos

| Uso | Requisitos |
|-----|-----------|
| Linha de comando | Python 3.8+ (nada além da biblioteca padrão) |
| Interface web | Python 3.8+, `pandas`, `streamlit` |

```bash
pip install pandas streamlit
```

---

## Formato de entrada

As sequências devem usar apenas as bases **A**, **T**, **C** e **G**, em maiúsculas,
sem espaços ou separadores internos.

### Arquivo texto (`.txt`)

Uma sequência por linha, sem cabeçalho. Linhas em branco são ignoradas.

```
ATGGCTAAACCGTAA
GGGATGCCCGGGTAG
TTTATGAAACCCGGGTGA
```

### Arquivo CSV (`.csv`) — apenas na interface web

Deve conter uma coluna chamada `entrada`:

```csv
entrada
ATGGCTAAACCGTAA
GGGATGCCCGGGTAG
```

---

## Como usar

### 1. Linha de comando

```bash
python biocompiler_1.py entrada.txt
```

Exibe o relatório detalhado na tela e grava `resultados.txt` no formato da
especificação.

Opções:

```bash
python biocompiler_1.py entrada.txt -o saida.txt   # define o arquivo de saída
python biocompiler_1.py entrada.txt --apenas-orf   # transcreve só a região codificante
```

Saída na tela:

```
========================================
BIOCOMPILER 1.0 - DNA TRANSCRIBER
========================================
ENTRADA: 1
STATUS: CORRETO
Bases: OK
START: ATG - OK
Quadro de leitura: OK
STOP: TAA - OK
Transcrição: OK
pré-mRNA: AUGGCUAAACCGUAA
----------------------------------------
ENTRADA: 2
STATUS: ERRO
TIPO: BUG - base inválida
pré-mRNA: NÃO GERADO
----------------------------------------
```

Arquivo `resultados.txt` gerado (UTF-8, campos separados por ponto e vírgula, conforme
a seção 11 da especificação):

```
linha;status;resultado;pre_mRNA
1;OK;CORRETO;AUGGCUAAACCGUAA
2;ERRO;BUG - base inválida;NÃO GERADO
3;ERRO;BUG - START ausente;NÃO GERADO
```

### 2. Interface web (Streamlit)

```bash
streamlit run app.py
```

Execute o comando a partir da pasta onde estão os dois arquivos `.py` — o Streamlit
adiciona ao `sys.path` a pasta do script, e o `app.py` precisa encontrar o
`biocompiler_1.py` ao lado dele.

No aplicativo:

1. Escolha o formato do arquivo (**CSV** ou **TXT**).
2. Envie o arquivo pelo campo de upload.
3. Clique em **Executar validação**.
4. Consulte a tabela de resultados e o resumo com a contagem por diagnóstico.
5. Use **Baixar resultados em CSV** para exportar o relatório.

A tabela traz três colunas: `entrada` (a sequência original), `status` (o diagnóstico:
`CORRETO` ou `BUG - ...`) e `pre_mRNA` (preenchido apenas nas sequências válidas).

### 3. Como biblioteca

```python
from biocompiler_1 import validar_sequencia

resultado, pre_mRNA = validar_sequencia("ATGGCTAAACCGTAA")
print(resultado)  # CORRETO
print(pre_mRNA)   # AUGGCUAAACCGUAA
```

Funções públicas:

| Função | Descrição |
|--------|-----------|
| `validar_sequencia(dna, apenas_orf=False)` | Devolve `(resultado, pre_mRNA)`. `pre_mRNA` é `None` em caso de erro. |
| `analisar_linha(dna, numero, apenas_orf=False)` | Devolve um dicionário com `linha`, `entrada`, `status`, `resultado`, `pre_mRNA`, `start`, `stop`. |
| `processar_arquivo(caminho, apenas_orf=False)` | Lê um `.txt` e devolve a lista de registros. |
| `exportar_resultados(registros, caminho)` | Grava o relatório no formato `linha;status;resultado;pre_mRNA`. |
| `formatar_saida_tela(registro)` | Monta o relatório detalhado de uma entrada. |
| `encontrar_start(dna)` / `encontrar_stop(dna, start)` | Localizam os códons START e STOP. |
| `transcrever(dna)` | Substitui T por U. |

---

## Casos reconhecidos

| Caso | Situação | Resultado |
|------|----------|-----------|
| 1 | Sequência válida | `CORRETO` |
| 2 | Caractere fora do alfabeto A/T/C/G | `BUG - base inválida` |
| 3 | Códon de início ATG ausente | `BUG - START ausente` |
| 4 | Nenhum STOP em fase após o START | `BUG - STOP ausente` |
| 5 | Quadro de leitura incompatível com trincas | `BUG - frameshift` |
| 6 | STOP em fase antes do término esperado | `BUG - nonsense / STOP prematuro` |

### Ordem de precedência

A classificação é uma cascata: a primeira condição satisfeita determina o resultado.
Quando uma sequência apresenta mais de um problema, prevalece o de maior precedência.

```
base inválida → START ausente → frameshift → STOP ausente → nonsense / STOP prematuro
```

A posição do *frameshift* nessa ordem é o que separa os casos 4 e 5. Compare os dois
exemplos da especificação:

- `ATGGCTAAACCGGGC` — 15 bases, trincas fecham (`ATG GCT AAA CCG GGC`), mas não há STOP
  → **STOP ausente**.
- `ATGGCTAAAACCGTAA` — 16 bases; a inserção de um `A` empurra o `TAA` final para fora do
  quadro → **frameshift**.

---

## Regras de análise adotadas

**Alfabeto.** A sequência deve conter exclusivamente A, T, C e G maiúsculos. Um único
caractere fora desse conjunto invalida a linha inteira. Sequências vazias também são
classificadas como base inválida.

**START.** É localizado o **primeiro `ATG` da sequência**, em qualquer posição. Bases
antes do START são permitidas e não precisam formar trincas completas.

**Quadro de leitura.** A região que vai do START até o fim da linha deve ter número de
bases múltiplo de 3, ou seja, `(len(dna) - start) % 3 == 0`. Caso contrário, a região
não pode ser organizada integralmente em trincas e a sequência é classificada como
*frameshift*.

**STOP.** A partir do START, a sequência é lida em trincas até o primeiro códon `TAA`,
`TAG` ou `TGA` em fase.

**STOP prematuro.** Se houver qualquer base após o STOP em fase encontrado, a sequência
é classificada como *nonsense / STOP prematuro*. Um STOP válido precisa encerrar a
sequência.

**Transcrição.** Sendo a sequência válida, cada timina (T) é substituída por uracila (U),
preservando a ordem das demais bases.

```
DNA:      ATGGCTAAACCGTAA
pré-mRNA: AUGGCUAAACCGUAA
```

---


## Validação

O motor foi testado contra todos os exemplos da especificação:

- os seis casos da seção 14 (14.1 a 14.6), com saída de tela e registro exportado
  idênticos aos do documento;
- as três sequências do `entrada.txt` da seção 2, todas com prefixo antes do ATG.

---


## Escopo

O BioCompiler 1.0 termina no pré-mRNA. Ele **não** realiza maturação do RNA (splicing,
CAP 5', cauda poli-A) nem tradução em proteína — essas etapas pertencem ao BioCompiler
2.0 e ao Sr. Ribossomo.
