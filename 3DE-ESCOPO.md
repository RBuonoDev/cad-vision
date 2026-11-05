# 3DE — escopo de desenvolvimento

O 3DE é uma implementação independente de CAD paramétrico. Não é o SolidWorks, não usa seu código-fonte e não oferece equivalência integral de funcionalidades ou formatos. Permissões de acesso ao computador não tornam disponíveis os algoritmos e o código-fonte original.

## Referências pesquisadas

- [Série oficial de vídeos Beginner's Guide to SOLIDWORKS Design](https://3dswym.3dexperience.3ds.com/wiki/solidworks-news-info/beginner-s-guide-to-solidworks-design_r8Eo_R8GS2WjKABIAxxKaQ).
- [Sketch and Extrude: resumo e instruções oficiais que acompanham o vídeo](https://3dswym.3dexperience.3ds.com/wiki/solidworks-news-info/creating-a-sketch-and-extrude-beginner-s-guide-to-solidworks_EHChFkHMQ-2zBQSg9kFhaA). Referência de fluxo: plano, geometria, relações, cotas, operação e reconstrução. O resumo inclui conteúdo gerado por IA e não substitui validação funcional.
- [Vídeo oficial: esboços, relações, extrusão, corte, filete e casca](https://www.youtube.com/watch?v=dQMS8KuDGoM). Foram consultados seus dados e descrição; não foi realizada uma auditoria visual integral de todos os vídeos.
- [Capacidades oficiais de SOLIDWORKS Design](https://www.solidworks.com/product/solidworks-design).
- [FreeCAD: recursos oficiais](https://www.freecad.org/features). Uma base CAD aberta é uma alternativa para uma futura versão de desktop com maior cobertura. Nenhuma distribuição FreeCAD foi instalada ou apresentada como desenvolvimento próprio nesta atualização.

## Cobertura desta implementação

| Área | Estado do 3DE |
| --- | --- |
| Linhas formando um contorno simples fechado | Implementado, até 100 vértices sem relações; até 40 com relações |
| Retângulos e círculos | Implementado por desenho e cotas |
| Horizontal, vertical, fixação de vértice | Implementado em contornos por linhas |
| Cota de comprimento, distâncias U/V | Implementado em contornos por linhas |
| Paralelismo, perpendicularidade, igualdade | Implementado entre segmentos de linha |
| Estado de definição / conflito de relações | Implementado por solucionador numérico limitado; conflitos detectados preservam a última peça aplicada |
| Extrusão, corte, profundidade simétrica, atravessar tudo | Implementado |
| XY/XZ/YZ e referências aos limites do sólido | Implementado; não é seleção associativa de faces |
| Histórico, edição, supressão, reordenação, desfazer/refazer | Implementado |
| STEP/STL e projeto JSON com relações | Implementado |
| Arcos, splines, tangência, geometria de construção | Não implementado |
| Recortar/estender, múltiplos contornos por esboço, seleção de regiões | Não implementado |
| Revolução, varredura, loft, padrões, espelho, casca | Não implementado |
| Filetes/chanfros com seleção de arestas | Não implementado |
| Montagens, posicionamentos e detecção de interferência | Não implementado |
| Desenhos técnicos associativos, cortes, tolerâncias, lista de materiais | Não implementado |
| Chapa metálica, estruturas soldadas, moldes, superfícies avançadas | Não implementado |
| Simulação estrutural, movimento, térmica e fluidos | Não implementado |
| CAM, roteamento elétrico/tubulação, bibliotecas comerciais | Não implementado |
| PDM, colaboração multiusuário, gestão de revisões | Não implementado |
| Compatibilidade nativa SLDPRT/SLDASM/SLDDRW | Não implementado |

Esta é uma matriz de áreas principais, não uma enumeração de todos os comandos de todas as edições e complementos do SolidWorks.

## Critérios para ampliar o 3DE

Cada módulo precisa de implementação real e testes próprios. Recursos novos devem preservar os projetos existentes e informar erros sem substituir a última geometria válida. Uma lista de botões ou uma interface visual parecida não comprova equivalência funcional. Recursos de simulação requerem validação técnica independente; equivalência de resultados não pode ser presumida.

Ordem técnica proposta: ampliar geometria/relações do esboço; acrescentar operações e seleção topológica; modelos com múltiplos corpos; montagens; documentação associativa; ferramentas de fabricação; módulos de análise. Essa ordem é um plano de desenvolvimento, não uma promessa de cobertura completa ou prazo.
