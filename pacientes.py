import os
import json
import streamlit as st
from dotenv import load_dotenv
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da chave de API da OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")

# Caminho do arquivo JSON para armazenar pacientes
DATA_FILE = "pacientes.json"

st.set_page_config(layout="wide")


def carregar_pacientes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def salvar_paciente(nome, sintomas, historico, exames, resposta_analise):
    pacientes = carregar_pacientes()
    if nome not in pacientes:
        pacientes[nome] = {
            "sintomas": sintomas,
            "historico": historico,
            "exames": exames,
            "respostas": [resposta_analise] if resposta_analise else [],
            "interacao": []  # Inicializa o array de interações
        }
    else:
        pacientes[nome]["sintomas"] = sintomas
        pacientes[nome]["historico"] = historico
        pacientes[nome]["exames"] = exames
        if resposta_analise:
            pacientes[nome]["respostas"].append(resposta_analise)
        # Não é necessário reinicializar 'interacao', pois já existe
    with open(DATA_FILE, "w") as file:
        json.dump(pacientes, file, indent=4)


# Inicialização do modelo de linguagem com ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7,
                 openai_api_key=openai_api_key)

# Memória para armazenar a conversa
memoria = ConversationBufferMemory()

# Criando o PromptTemplate com uma única variável de entrada
prompt = PromptTemplate(
    input_variables=["entrada"],
    template="{entrada}\nBaseado nas informações acima, como devemos proceder?"
)

# Inicializando o LLMChain com o modelo e o prompt
chain = LLMChain(llm=llm, prompt=prompt, memory=memoria)


def agente_com_bot(sintomas, historico_medico, exames):
    # Concatenar histórico, sintomas e exames em uma única string
    entrada = f"Histórico Médico: {historico_medico}\nSintomas: {sintomas}\nExames: {exames}"
    # Obter a resposta do agente
    resposta = chain.run(entrada=entrada)
    return resposta


# Interface com Streamlit
st.title("Assistente de Diagnóstico de Hérnia de Disco")

# Etapa 1: Selecionar ou cadastrar paciente
pacientes = carregar_pacientes()
nome_paciente = st.text_input("Digite seu nome:")

if nome_paciente:
    if nome_paciente in pacientes:
        st.success(f"Bem-vindo de volta, {nome_paciente}!")
        dados_paciente = pacientes[nome_paciente]
        sintomas_usuario = dados_paciente["sintomas"]
        historico_usuario = dados_paciente["historico"]
        exames_usuario = dados_paciente["exames"]

        # Exibir campos dentro de um accordion fechado por padrão
        with st.expander("Informações do Paciente", expanded=False):
            sintomas_usuario = st.text_area("Sintomas", value=sintomas_usuario)
            historico_usuario = st.text_area(
                "Histórico Médico", value=historico_usuario)
            exames_usuario = st.text_area("Exames", value=exames_usuario)

        botao_label = "Analisar meu caso"
    else:
        st.info("Novo paciente detectado. Insira seus dados abaixo:")

        # Campos para novo paciente
        sintomas_usuario = st.text_area("Descreva seus sintomas:")
        historico_usuario = st.text_area(
            "Informe seu histórico médico relevante:")
        exames_usuario = st.text_area("Quais exames foram feitos (se houver):")

        botao_label = "Salvar Paciente"

    if st.button(botao_label):
        if nome_paciente and sintomas_usuario:
            resposta_agente = agente_com_bot(
                sintomas_usuario, historico_usuario, exames_usuario)
            salvar_paciente(nome_paciente, sintomas_usuario,
                            historico_usuario, exames_usuario, resposta_agente)
            st.success("Paciente salvo com sucesso!")
            st.subheader("Resultado da Análise:")
            st.write(resposta_agente)
            # Link para a página de chat
            st.markdown(
                f'<a href="/chat" target="_self" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; border-radius: 5px;">Falar sobre meu caso</a>',
                unsafe_allow_html=True
            )
        else:
            st.warning(
                "Por favor, preencha seu nome e sintomas para continuar.")
else:
    st.warning("Por favor, digite seu nome para continuar.")
