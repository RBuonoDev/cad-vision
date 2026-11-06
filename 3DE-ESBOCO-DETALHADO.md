# 3DE — comportamento detalhado do editor de esboços

## Referências consultadas

A pesquisa usou a documentação oficial de SolidWorks sobre [inferências](https://help.solidworks.com/2026/English/SolidWorks/acadhelp/c_Inferencing.htm), [grade e encaixes](https://help.solidworks.com/2024/English/SolidWorks/acadhelp/c_Grid_and_Snap.htm?format=P&value=) e [relações e estado de definição](https://help.solidworks.com/2021/english/SolidWorks/sldworks/HIDD_DVE_SKETCH_DEFAULT.htm). O comportamento do 3DE descrito abaixo foi implementado independentemente; não é uma reprodução integral nem tem todos os modos de interação do SolidWorks.

## Plano, peça e fundo

- XY usa U=X, V=Y, normal +Z; XZ usa U=X, V=Z, normal −Y; YZ usa U=Y, V=Z, normal +X.
- O esboço é visto perpendicularmente ao plano escolhido. Deslocamento e referência de posicionamento continuam no painel de propriedades.
- “Arestas da peça ao fundo” mostra a projeção ortográfica das arestas reais do sólido anterior à operação selecionada. Ao criar uma nova operação, usa o sólido atual inteiro. Ao editar a primeira operação, não há sólido anterior para mostrar.
- A referência tem cor discreta e não altera a geometria. Não implementa recorte do sólido pelo plano, remoção de linhas ocultas, seleção de faces nem vínculos topológicos associativos. Arestas sobrepostas na projeção podem coincidir visualmente.
- Enquadrar inclui o perfil e as arestas de referência visíveis. Ocultar a peça não apaga o sólido; só muda a exibição do esboço.
- Grade visual, encaixe na grade, origem, eixos, sombreado de região e nomes/relações possuem controles independentes. A grade pode aparecer sem impor arredondamento às coordenadas. O encaixe na grade começa desligado nesta versão.

## Desenhar linhas

1. Escolha Desenhar contorno. O editor abre no modo Linhas, vazio.
2. Clique para definir o primeiro vértice. Mova o cursor: a próxima linha aparece tracejada, com comprimento em mm e ângulo em relação a U.
3. Clique novamente para criar o segmento. Cada segmento seguinte compartilha seu vértice inicial com o anterior; não são linhas desconectadas.
4. A aproximação horizontal/vertical exibe uma indicação. Com inferência automática ligada, aceitar a linha alinhada acrescenta uma relação H ou V. Shift força alinhamento horizontal ou vertical para o próximo ponto.
5. Clique no primeiro vértice para fechar ou pressione Enter. O fechamento liga o último ponto ao primeiro.
6. Um contorno fechado pode ser sombreado. O fechamento não garante validade: interseções, contatos entre segmentos não adjacentes, pontos repetidos e área insuficiente bloqueiam o envio e a extrusão. O motor geométrico valida novamente ao reconstruir.
7. Um clique muito perto do último ponto não cria um segmento de comprimento quase zero.

## Encaixes e inferências

- Encaixes geométricos reconhecem origem, extremidades, pontos médios e vértices projetados da peça. A tolerância é em pixels, mantendo a experiência durante o zoom.
- Uma marca e um texto indicam o alvo reconhecido. O alvo geométrico tem prioridade sobre o encaixe na grade.
- Alt ignora os encaixes calculados pelo editor naquele movimento. A posição pode ser digitada no painel para precisão numérica.
- Encaixar em um ponto médio ou vértice da peça copia sua posição naquele momento. Não cria relação associativa com o modelo. Se o sólido anterior mudar, esse ponto não acompanha automaticamente o vértice de referência.
- Horizontal/vertical inferidos criam relações persistidas no projeto. As demais relações são adicionadas explicitamente pelos comandos oferecidos.

## Seleção, cores e edição

- No modo Selecionar/mover, passar sobre um segmento o destaca em laranja. Clicar seleciona em amarelo. Ctrl permite selecionar dois segmentos ou dois vértices para relações.
- Arrastar um vértice tenta preservar as relações existentes; um movimento incompatível é recusado.
- Azul indica liberdade restante no esboço; verde indica zero graus de liberdade calculados pelo solucionador local. O estado é do contorno completo, não uma classificação individual de cada segmento. Rosa identifica vértices fixados.
- Horizontal, Vertical, Comprimento, Fixo, Paralelos, Perpendiculares, Iguais e distâncias U/V continuam disponíveis. Alterar uma cota na lista tenta resolver o esboço; conflitos preservam a geometria anterior.
- Ocultar nomes/relações não remove as relações. Remover uma relação na lista altera o esboço e seus graus de liberdade.
- Retirar ponto reabre o contorno e limpa as relações para evitar referências a índices inexistentes. Desfazer desenho permite recuperar o estado anterior.

## Navegação e atalhos

- Roda: zoom centrado na posição do cursor.
- Botão direito ou botão do meio arrastado: deslocar a vista no plano.
- F: enquadrar perfil e referência. L: modo Linhas. S: selecionar/mover.
- Enter: fechar contorno com pelo menos três vértices.
- Esc: cancelar seleção e arraste. Ctrl+Z: desfazer desenho. Ctrl+Y: refazer desenho.
- Os atalhos são recebidos quando o canvas está em foco; não substituem a digitação nos campos numéricos.

## Do esboço ao sólido

Informe a profundidade no editor e use Extrudar em 3D ou Cortar em 3D. A extrusão direta segue a normal positiva; o corte direto segue a negativa, ambos com profundidade definida. Para profundidade simétrica, atravessar tudo ou outros ajustes, salve o esboço no painel e use as propriedades da operação.

Um erro preserva o histórico aplicado. Desfazer do projeto atua nas operações aplicadas; Desfazer desenho atua no rascunho antes do envio. Salvar JSON preserva as relações; STEP/STL exportam a geometria.

## Limites atuais

Um contorno simples por operação; até 40 vértices com relações no editor; sem arcos livres, tangência, splines, seleção de múltiplas regiões, geometria de construção, recorte/extensão de segmentos, montagem ou simulação. A projeção ao fundo não é um editor 3D de faces. Consulte também 3DE-ESCOPO.md. Esses limites impedem afirmar que o 3DE é exatamente igual ao SolidWorks.
