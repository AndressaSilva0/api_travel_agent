
# Travel Agent

## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura do Código](#estrutura-do-codigo)
- [Contribuição](#contribui%C3%A7%C3%A3o)
- [Licença](#licen%C3%A7a)

## Sobre o Projeto

O **Travel Agent** é um sistema inteligente que auxilia no planejamento de viagens, fornecendo roteiros detalhados com base em eventos locais e preços de passagens aéreas. Ele combina modelos de IA generativa e pesquisa na web para gerar recomendações personalizadas para os usuários.

## Tecnologias Utilizadas

O projeto utiliza diversas bibliotecas para IA, pesquisa na web e processamento de texto:

- `langchain-google-genai` - Integração com o modelo Gemini da Google
- `langchain` - Framework para cadeias de execução de modelos de IA
- `langchain-community` - Ferramentas adicionais da comunidade LangChain
- `langchainhub` - Modelos e prompts prontos para uso
- `bs4` - Biblioteca para extração de dados de páginas web
- `langchain-text-splitters` - Utilitários para fragmentação de textos
- `langchain-core` - Componentes principais do LangChain
- `duckduckgo-search` - Pesquisa na web sem rastreamento
- `wikipedia` - Consulta e extração de dados da Wikipedia
- `chromadb` - Banco de dados vetorial para busca semântica

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/AndressaSilva0/travel-agent.git
   cd travel-agent
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):

   ```bash
   python -m venv venv
   python3 -m venv venv # Linux/macOS
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   pip3 install -r requirements.txt # Linux/macOS
   ```

4. Defina as variáveis de ambiente para as chaves de API:

   ```bash
   export GOOGLE_API_KEY="sua_chave_aqui"
   export LANGCHAIN_API_KEY="sua_chave_aqui"
   ```

## Uso

O projeto recebe uma consulta do usuário e retorna um roteiro de viagem detalhado. Para executar o serviço:

```bash
python travelAgent.py
python3 travelAgent.py # Linux/macOS
```

Para interagir com o agente diretamente:

```python
from main import getResponse
query = "Vou viajar para Londres em agosto de 2024. Quais eventos ocorrerão?"
response = getResponse(query, llm)
print(response)
```

## Estrutura do Código

O código principal está dividido nas seguintes funções:

- **`researchAgent(query, llm)`**: Realiza pesquisas na web usando DuckDuckGo e Wikipedia.
- **`loadData()`**: Obtém informações de um site de viagens e armazena em um banco de dados vetorial (ChromaDB).
- **`getRelevantDocs(query)`**: Recupera documentos relevantes armazenados no banco de dados vetorial.
- **`supervisorAgent(query, llm, webContext, relevant_documents)`**: Gera um roteiro detalhado combinando os dados coletados.
- **`getResponse(query, llm)`**: Integra todas as etapas e retorna a resposta final ao usuário.
- **`lambda_handler(event, context)`**: Handler para execução em ambiente serverless (AWS Lambda).

## Contribuição

Sinta-se à vontade para contribuir com melhorias no projeto! Para isso:

1. Faça um fork do repositório
2. Crie uma branch com sua funcionalidade (`git checkout -b minha-feature`)
3. Faça o commit (`git commit -m 'Minha nova funcionalidade'`)
4. Envie para o repositório (`git push origin minha-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.
