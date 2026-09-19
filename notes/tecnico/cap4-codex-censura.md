Lendo o [capítulo 4 atual](C:/Users/yuri_taba/Desktop/recursos-campanha-local/tese/04-mecanismo-causal-coordenacao.qmd:43) e o código que produz os resultados, acho que falta construir melhor **o problema que a análise de sobrevivência resolve**. O texto passa da definição do evento diretamente às curvas e, depois, aos coeficientes. A censura deveria entrar antes do Kaplan–Meier, porque ajuda a esclarecer o significado substantivo de toda a análise.

Há uma questão central para o argumento: **as diferenças observadas combinam o momento do recebimento e a possibilidade de terminar a campanha sem receber recursos partidários**. Isso precisa aparecer na interpretação da prioridade financeira.

Eu reorganizaria essa parte em quatro movimentos:

1.  **Do volume recebido ao tempo até o financiamento.** Explicar a passagem da seção anterior: os fluxos mostram quanto dinheiro chegou a cada grupo ao longo da campanha; a sobrevivência acompanha cada candidatura até a ocorrência de um evento.
2.  **Evento, janela de observação e censura.** Definir a unidade de análise, o início da contagem, os eventos e o tratamento das candidaturas sem repasse.
3.  **Kaplan–Meier: diferenças na trajetória de recebimento.** Apresentar a comparação descritiva entre candidaturas com e sem credenciais eleitorais prévias.
4.  **Cox: associação entre credenciais e recebimento ao longo da campanha.** Explicar o que o ajuste pelas covariáveis acrescenta, interpretar os resultados e apresentar os pressupostos.

**A seção sobre censura tem conteúdo empírico relevante.** Na implementação atual, quem não registra repasse dentro da janela permanece em observação até a eleição e recebe indicador de evento igual a zero. Recalculando os números com as correções da harmonização, encontrei:

| Eleição | Sem repasse entre candidaturas com credenciais | Sem repasse entre candidaturas sem credenciais |
|--------------------|-------------------------:|-------------------------:|
| 2018 | 79 de 972 — **8,1%** | 1.993 de 6.654 — **30,0%** |
| 2022 | 39 de 1.351 — **2,9%** | 1.063 de 8.265 — **12,9%** |

São os denominadores da amostra analítica atual, após exclusões por covariáveis ausentes.

Isso mostra por que a censura merece mais do que uma nota metodológica: há uma diferença expressiva entre os grupos na proporção que chega ao fim da campanha sem financiamento partidário. Uma curva mais alta expressa a permanência sem repasse, que pode decorrer tanto de recebimento posterior quanto de ausência de recebimento durante toda a janela.

Um parágrafo de abertura possível seria:

> A análise acompanha as candidaturas desde o início da campanha até o recebimento do primeiro repasse partidário ou o encerramento da janela de observação, no dia da eleição. As candidaturas sem repasse registrado nesse intervalo são tratadas como observações censuradas à direita: sabe-se que permaneceram sem experimentar o evento durante todo o período acompanhado. Elas contribuem para o conjunto de candidaturas em risco de recebimento até o encerramento da observação. Sua inclusão permite analisar o acesso ao financiamento ao longo da campanha, preservando também a informação das candidaturas que não receberam recursos nesse período.

Depois, eu explicaria que **esse tratamento não pressupõe que todas acabariam recebendo dinheiro**. A inferência está limitada à campanha observada. Excluir as censuradas produziria outra pergunta: quando receberam aquelas que foram financiadas? A distinção entre tempo observado e ocorrência do evento é justamente a base do tratamento da censura. [Documentação do lifelines](https://lifelines.readthedocs.io/en/latest/Survival%20Analysis%20intro.html)

Também evitaria concluir que a censura é informativa apenas porque sua proporção difere entre os grupos. No código, o encerramento é comum às candidaturas de cada eleição; as proporções diferentes refletem a ocorrência desigual do evento até esse limite.

**No Kaplan–Meier, falta ensinar o leitor a ler o resultado antes de apresentar os percentuais.** Bastaria definir (S(t)) como a probabilidade de permanecer sem o repasse até o tempo (t), explicar que a curva cai quando ocorrem recebimentos e esclarecer quem ainda integra o conjunto em risco. Eu trocaria “teste Kaplan–Meier” por “estimador” ou “curvas de Kaplan–Meier”; um teste de diferença entre curvas seria um procedimento adicional.

A interpretação poderia se concentrar em três aspectos: quando a separação aparece, como evolui nas primeiras semanas e quanto permanece sem receber ao final. Uma tabela de candidaturas em risco sob as figuras e intervalos de confiança ajudariam a apresentação.

Aqui há uma particularidade do **maior repasse** que merece explicação própria: o código identifica o **maior total diário de receitas partidárias**, conhecido retrospectivamente ao observar toda a campanha. Ele informa quando ocorreu o pico diário de financiamento. Eu o apresentaria como análise complementar ao primeiro recebimento e moderaria a expressão “investimento principal do partido”: o maior valor em um dia não necessariamente representa a maior parte do financiamento total.

**No Cox, o ganho principal viria de tornar mais precisa a pergunta e a interpretação.** O modelo atual estima o tempo até o **primeiro repasse**, por eleição. Isso precisa estar explícito, pois a exposição anterior trabalha com dois eventos.

O trecho que define o modelo como uma “probabilidade condicional” também merece ajuste. O Cox modela uma taxa instantânea, e o HR compara essas taxas entre candidaturas que ainda não receberam. Assim, a interpretação do resultado de 2018 poderia ser:

> Mantidas constantes as demais covariáveis, cada vitória anterior para deputado federal está associada a uma taxa instantânea de primeiro recebimento aproximadamente 54% maior entre as candidaturas que ainda permanecem sem repasse.

Esse resultado não equivale a receber 54% mais cedo nem a uma probabilidade de recebimento 54% maior. A leitura do HR depende ainda da hipótese de proporcionalidade dos riscos. [Documentação do modelo de Cox](https://lifelines.readthedocs.io/en/latest/Survival%20Regression.html)

Por fim, eu incluiria o diagnóstico dessa hipótese e esclareceria uma diferença em relação ao capítulo 3: **erros-padrão agrupados por partido × UF não tornam a comparação intralista**. Um Cox estratificado por lista seria uma possibilidade a avaliar se você quiser aproximar os desenhos, mas isso seria uma decisão analítica adicional.

Minha prioridade seria desenvolver a seção de evento e censura e, a partir dela, revisar as interpretações. Ela dá sustentação à afirmação substantiva que o capítulo pode explorar: candidaturas com credenciais apresentam acesso mais precoce ao financiamento e menor frequência de encerramento da campanha sem repasse.