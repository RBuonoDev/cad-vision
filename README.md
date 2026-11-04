# CAD Vision — interface web de desenho 2D para 3D

Site em Streamlit com interface escura, upload de foto, extração opcional de cotas pelo Gemini, edição de dimensões e visualização 3D com Three.js.

## Executar no Windows

1. Instale Python 3.10 ou mais recente.
2. Abra o terminal na pasta do projeto.
3. Execute:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

4. Abra `http://localhost:8501` no navegador (normalmente abre automaticamente).
5. Para analisar uma foto, informe sua API Key do Gemini no painel lateral. Para testar sem API Key, altere as cotas manualmente.

## Escopo

Esta versão representa somente **um prisma retangular com zero ou um furo circular passante vertical**. Não reconstrói automaticamente peças mecânicas complexas, roscas, rasgos, múltiplos furos, tolerâncias, cortes, desenhos multivistas nem exporta STEP/STL. A IA não inventa cotas ausentes: valores não confirmados precisam ser revisados manualmente.

O modelo 3D requer conexão à internet para carregar as bibliotecas Three.js do CDN. A análise de imagens requer internet e uma chave válida da API Gemini. Não publique uma chave da API no código ou em repositórios.
