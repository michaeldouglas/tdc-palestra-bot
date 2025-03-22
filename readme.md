# Assistente de Diagnóstico de Hérnia de Disco

Este repositório contém um aplicativo interativo desenvolvido com Streamlit que auxilia no diagnóstico de hérnia de disco. Utilizando técnicas de processamento de linguagem natural e bases de conhecimento específicas, o assistente fornece informações detalhadas sobre sintomas, causas, tratamentos e tipos de hérnia de disco.

## Funcionalidades

- Interação Personalizada: O aplicativo permite que o usuário insira seu nome e forneça informações sobre sintomas, histórico médico e exames realizados. Com base nesses dados, o assistente oferece respostas personalizadas.

- Bases de Conhecimento: O sistema utiliza duas bases de conhecimento no formato JSON que contêm informações sobre hérnia de disco, incluindo definições, causas, sintomas, tratamentos, prevenção e diagnósticos.

- Memória de Conversa: O assistente mantém um histórico das interações com cada paciente, permitindo um acompanhamento contínuo e respostas mais precisas ao longo do tempo.

## Tecnologias Utilizadas

- Streamlit: Framework Python para criação de aplicativos web interativos de forma rápida e simples. Streamlit

- Langchain: Biblioteca que facilita a construção de aplicações com modelos de linguagem, integrando LLMs (Large Language Models) com outras fontes de dados. Langchain

- OpenAI GPT-3.5 Turbo: Modelo de linguagem avançado utilizado para gerar respostas contextuais e precisas.

## Como Executar o Aplicativo

Clone o Repositório:

```bash
git clone https://github.com/seu_usuario/assistente_hernia_disc.git
cd assistente_hernia_disc
```

Instale as dependências e ative:

```bash
poetry install
poetry shell
```

Configure as Variáveis de Ambiente:

Crie um arquivo .env na raiz do projeto e adicione sua chave de API da OpenAI:

```ini
OPENAI_API_KEY=sua_chave_api_aqui
```

Execute o Aplicativo:

```bash
streamlit run app.py
```
