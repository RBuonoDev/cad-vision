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
