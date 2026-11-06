# 3DE · CAD paramétrico no navegador

O 3DE é um projeto independente de modelagem mecânica. O editor cria um sólido em milímetros por meio de um histórico de operações. A interface atual prioriza o fluxo de modelagem; o visual pode evoluir depois.

## Funcionalidades atuais

- Esboços de retângulos, círculos e contornos fechados por linhas, com cotas e relações geométricas.
- Adição de material por extrusão e corte com profundidade definida, simétrica ou atravessando a peça.
- Filete e chanfro em grupos de arestas: todas, paralelas a X/Y/Z ou pertencentes à face superior/inferior.
- Histórico editável com supressão, reordenação e desfazer/refazer durante a sessão.
- Salvar e abrir projeto JSON, exportar geometria STEP e malha STL.
- Visualizador 3D com vistas isométrica, frontal, superior e direita.

A seleção de uma aresta individual no visualizador, montagens, desenhos técnicos associativos, simulação e arquivos nativos do SOLIDWORKS ainda exigem módulos próprios. Consulte [3DE-ESCOPO.md](3DE-ESCOPO.md) para a matriz de cobertura.

## Executar

Com Python 3.12 e as dependências de `requirements.txt` instaladas:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra o endereço mostrado pelo Streamlit. O visualizador Three.js utiliza bibliotecas públicas carregadas no navegador. O projeto JSON preserva a árvore paramétrica; STEP e STL contêm a geometria exportada.

## Verificar

```powershell
python -m unittest discover -s tests -v
```

Os testes de geometria requerem CadQuery. O 3DE não contém código do SOLIDWORKS nem pretende abrir seus formatos proprietários nesta etapa.
