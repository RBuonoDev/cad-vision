# Verificação da oficina paramétrica

Verificado em 05/11/2026 com Python 3.12, Streamlit 1.50.0 e CadQuery 2.6.1.

- Volumes exatos para extrusões, furos passantes e bolsões.
- Planos XY/XZ/YZ, sentidos positivo/negativo e extrusão simétrica.
- Furo passante após alterar a base de 20 para 37 mm.
- Polígono côncavo válido; rejeição de contorno cruzado/repetido e sólidos desconectados.
- Compatibilidade com projeto JSON anterior; STEP exportado e reimportado com volume preservado; STL e malha com arestas geométricas.
- Interface: inicialização, árvore de operações, edição de cotas, reconstrução, desfazer/refazer, peça vazia e preservação da peça após erro.
- No navegador: desenho de retângulo com o mouse e envio de cotas; contorno triangular desenhado, fechado e extrudado, com volume de 12.000 mm³ e dimensões de 60 × 40 × 10 mm.
- No navegador: alteração da placa para 30 mm de espessura manteve o furo passante; volume de 173.968,14 mm³.
- Visualizador Three.js carregado e renderizado no navegador.

Esses testes verificam este protótipo e não demonstram equivalência completa com SolidWorks. A verificação da publicação é registrada na resposta de entrega.

## Testes do 3DE com relações

- Solucionadores no navegador e servidor: estado totalmente definido, cota de comprimento, paralelismo, perpendicularidade, igualdade e distância U/V.
- Conflito entre comprimentos incompatíveis rejeitado; movimento que viola fixação rejeitado no solucionador do navegador.
- Alteração de comprimento de 80 para 100 mm preservou sete relações e regenerou um sólido de 100.000 mm³.
- Relações preservadas ao salvar/reabrir o JSON.
- Testes anteriores de geometria, planos, cortes, exportação, compatibilidade, histórico e recuperação após erro continuam passando.

## Filete e chanfro

- Validação local de raio/distância e seleção de arestas: aprovada.
- Projetos JSON versões 1, 2 e 3 continuam sendo lidos; novos projetos usam a versão 4.
- Sintaxe Python de app.py e engine.py: verificada.
- O teste de geometria com CadQuery (volume após filete/chanfro e falha de raio excessivo) está incluído em `tests/test_edge_features.py`; precisa ser executado em um ambiente com CadQuery instalado. Esta verificação local não certifica o resultado geométrico.
