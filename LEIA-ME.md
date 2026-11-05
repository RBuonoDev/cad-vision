# CAD Acadêmico — primeiro protótipo de modelagem de peças

Esta é uma implementação própria em Python, com CadQuery para geometria e Three.js para visualização. Não contém código extraído do SolidWorks e não é uma reprodução completa dele.

## Executar no Windows

É necessário Python 3.12 de 64 bits. Abra um terminal nesta pasta e execute:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

O navegador abrirá o aplicativo local. A primeira instalação baixa um motor CAD e pode demorar. A modelagem funciona localmente; o visualizador precisa de WebGL e conexão com os servidores públicos das bibliotecas Three.js (`cdnjs.cloudflare.com` e `cdn.jsdelivr.net`).

## Experimentar

O projeto inicial é uma placa de 100 × 60 × 20 mm com um furo central de 16 mm.

1. Selecione **Editar operação** e escolha **Base**.
2. Altere **Comprimento X** e clique em **Reconstruir peça**.
3. Selecione **Furo central** para alterar o diâmetro, a posição ou a profundidade do corte.
4. Para adicionar um ressalto, escolha **Nova operação**, perfil circular, operação **Extrusão (+Z)** e plano **Z = 20**. Desloque o centro para não coincidir com o furo, ou faça o ressalto sobre uma placa sem furo.
5. Exporte **Projeto editável** para preservar o histórico, **STEP** para intercâmbio CAD ou **STL** para obter uma malha.

Todas as medidas estão em milímetros. O retângulo é centrado nas coordenadas X/Y informadas. A extrusão cresce em +Z a partir do plano Z; o corte avança em −Z. As posições Z são valores explícitos, não referências associativas às faces: se mudar a altura da base, ajuste também o plano dos recursos seguintes.

As alterações do formulário só chegam ao sólido ao clicar em **Reconstruir peça**. A prévia 2D mostra o perfil do formulário. Operações que falham preservam o último projeto válido. Desmarcar **Operação ativa** suprime o recurso; toda a sequência será reconstruída e precisa continuar válida.

## Escopo

- Esboços fechados retangulares e circulares definidos por cotas.
- Extrusão aditiva e corte extrudado, incluindo bolsões e furos.
- Histórico ordenado, edição de parâmetros e supressão.
- Validação de um único sólido conectado, volume e dimensões totais.
- Projeto JSON próprio e exportação STEP/STL.

Esta versão não inclui desenho livre com mouse, linhas/arcos arbitrários, solver de restrições, seleção de faces, planos inclinados, referências associativas, montagem, simulação, filetes ou leitura/gravação de SLDPRT. STEP transporta o sólido, sem recriar o histórico do SolidWorks; STL transporta apenas a malha.

## Relação com a observação do SolidWorks

Foi aberto o SolidWorks Design Standard 2026 SP3.2 instalado no computador e criado um documento novo de peça. Foram observados os planos frontal/superior/direito, a origem, a árvore de projeto e os comandos de esboço, ressalto/base extrudado e corte extrudado. Essa foi uma inspeção inicial da interface, não uma análise do código interno, nem um teste de equivalência completa entre os programas.

A estrutura e os algoritmos deste protótipo foram escritos independentemente usando APIs documentadas de uma biblioteca CAD pública. Não foram copiados binários, recursos gráficos, ícones ou código proprietário do SolidWorks.

## Arquivos

- `app.py`: interface e editor de operações.
- `engine.py`: validação, reconstrução, malha e exportação.
- `viewer.py`: visualizador Three.js.
- `requirements.txt`: dependências diretas.
- `.streamlit/config.toml`: tema escuro.

## Verificação realizada

Testes locais em Python 3.12 com CadQuery 2.6.1 passaram para:

- Volume analítico da placa com furo comparado ao sólido gerado.
- Edição de comprimento com reconstrução do histórico.
- Bolsão retangular cego, ressalto circular e supressão de recurso.
- Rejeição de corte sem interseção, sólido desconectado, números inválidos e corte sem base.
- Geração da malha e exportação STEP/STL.
- Reimportação do STEP com preservação do volume.
- Abertura da interface e alteração de cota pelo formulário usando Streamlit AppTest.
- Sintaxe JavaScript do visualizador.

A renderização WebGL e a navegação 3D no navegador não foram verificadas nesta execução. Os arquivos `exemplo.json`, `exemplo.step` e `exemplo.stl` acompanham a entrega para inspeção e intercâmbio.

## Referências técnicas

- [CadQuery: modelagem paramétrica](https://cadquery.readthedocs.io/en/latest/quickstart.html)
- [CadQuery: importação e exportação](https://cadquery.readthedocs.io/en/latest/importexport.html)

As dependências mantêm suas próprias licenças. Consulte os respectivos projetos ao distribuir o trabalho acadêmico. Confira dimensões e tolerâncias antes de usar qualquer resultado para fabricação.

