# 3DE · Oficina paramétrica

Aplicativo acadêmico independente em Python, CadQuery e Three.js. A inspeção estática com REA identificou interfaces de esboços e operações do SolidWorks; essas informações orientaram a organização funcional. Esta implementação não incorpora código nem recursos gráficos do SolidWorks.

## Usar o site

1. Selecione uma operação no histórico ou clique em **＋ Nova operação**.
2. Escolha adicionar/remover material e um perfil: retângulo, círculo ou contorno por linhas.
3. Escolha XY, XZ ou YZ. As coordenadas U/V pertencem ao plano; o deslocamento segue sua normal, indicada no painel.
4. Digite as cotas ou abra **Esboço 2D**. Retângulos são desenhados entre dois cantos; círculos, do centro à borda; contornos, por cliques nos vértices e fechamento no primeiro ponto. É possível mover os vértices. Shift alinha o novo segmento e a grade permite ajustar o passo em mm.
5. No desenho, **Usar este esboço** envia o perfil ao painel. **Aplicar operação** reconstrói a peça com os parâmetros do painel. Nenhuma alteração é aplicada só por desenhar.
6. Use as vistas frontal, superior, direita e isométrica, arestas reais, aramado e grade para inspecionar o sólido.
7. Salve o projeto JSON para continuar depois, ou exporte STEP/STL.

## Comportamento mecânico

- Extrusão ou corte com profundidade definida e sentido positivo/negativo.
- Operações simétricas: a profundidade total é dividida igualmente nos dois lados do esboço.
- Cortes **Atravessar tudo** calculam a profundidade necessária na direção selecionada ao reconstruir.
- O posicionamento pode usar a origem ou o limite positivo/negativo da caixa do sólido anterior. Referências aos limites acompanham mudanças nas operações anteriores. São referências à caixa, não a faces selecionadas.
- No plano XZ, a normal positiva é −Y; no YZ, é +X; no XY, é +Z.
- O histórico permite editar cotas, suprimir, reordenar e excluir. Operações inválidas preservam o último projeto válido.
- Desfazer/refazer preserva até 25 alterações aplicadas durante a sessão. Recarregar a página pode encerrar a sessão; salve o JSON.
- Novas peças podem começar vazias. É necessário adicionar material antes de cortar. A peça deve permanecer um único sólido conectado.
- Arquivos JSON da versão anterior continuam aceitos. Seus planos e posições explícitas mantêm o significado original.

O exemplo é uma placa de 100 × 60 × 20 mm com um furo passante de Ø16 mm. O furo acompanha o limite superior ao mudar a espessura da base.

## Executar e publicar

Python **3.12**, 64 bits. No terminal desta pasta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Para Streamlit Community Cloud, mantenha `app.py`, `engine.py`, `viewer.py`, `sketch/index.html`, `requirements.txt`, `packages.txt` e `.streamlit/config.toml` nas posições fornecidas. Selecione Python 3.12. O esboço 2D é servido pelo próprio aplicativo; o visualizador usa Three.js dos CDNs públicos cdnjs.cloudflare.com e cdn.jsdelivr.net, exige conexão e WebGL. Preserve Streamlit 1.50.0 e as demais versões fixadas.

## Limites

Sem solver geral de restrições, arcos livres, seleção de faces, planos inclinados, montagens, simulação, filetes ou leitura/gravação SLDPRT. O contorno é um polígono fechado simples com até 100 vértices. Até 50 operações por projeto. STEP exporta a geometria, sem o histórico paramétrico; STL contém a malha, com coordenadas em mm.

O visual tem identidade própria, com painel de cotas, histórico lateral e oficina em verde mineral e grafite. Não foram usados ícones, logotipos nem elementos gráficos extraídos do programa de referência.

## 3DE — editor com relações

O projeto agora se chama **3DE**. Na aba Esboço 2D, escolha Contorno por linhas, desenhe e feche o contorno. Clique em um segmento para selecionar; Ctrl permite escolher dois. Clique nos vértices para selecioná-los; arraste para mover respeitando as relações.

- Horizontal/Vertical: mantém a direção do segmento.
- Cotar: define o comprimento do segmento selecionado; o valor aparece na lista e pode ser alterado.
- Fixar vértice: ancora sua posição. Remova essa relação para voltar a movê-lo livremente.
- Paralelos, Perpendiculares e Iguais: exigem dois segmentos selecionados.
- ΔU/ΔV: distância assinada entre dois vértices, na ordem em que foram selecionados. São cotas nos eixos do esboço.
- Inferir horizontal/vertical: acrescenta relações ao desenhar segmentos alinhados. Vértices consecutivos compartilham o mesmo ponto, mantendo a ligação do contorno.
- Azul: esboço com liberdade restante. Verde e “Totalmente definido”: o solucionador encontrou zero graus de liberdade locais.
- Relações conflitantes: o desenho anterior é preservado; revise ou remova relações antes de prosseguir.
- Desfazer desenho/Refazer desenho: atua dentro do editor antes de enviar o esboço. Desfazer/Refazer do projeto atua nas operações aplicadas.

Use **Arquivo e exemplos → Exemplo com relações** para experimentar uma placa totalmente definida. Altere o comprimento de 80 para 100 mm na lista de relações ou no painel e aplique a operação. O sólido passa de 80.000 para 100.000 mm³, preservando altura, largura e relações.

O projeto JSON agora usa versão 3 e preserva relações; versões 1 e 2 continuam aceitas. Limites do solucionador: 40 vértices, 60 relações, comprimentos mínimos de 0,1 mm. O solucionador numérico tem escopo limitado a linhas e às relações oferecidas; não inclui arcos, tangência nem todas as relações de um CAD comercial. A detecção de definição é local e numérica, não uma prova simbólica de unicidade global.

Consulte **3DE-ESCOPO.md** para a cobertura real e os módulos que ainda não existem. Esta versão não é uma réplica integral do SolidWorks.

