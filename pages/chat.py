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

# Caminho dos arquivos JSON
DATA_FILE = "pacientes.json"
BASE_CONHECIMENTO_FILE_1 = "knowledge_bases/base1.json"
BASE_CONHECIMENTO_FILE_2 = "knowledge_bases/base2.json"

st.set_page_config(layout="wide")


def carregar_pacientes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def carregar_historico(paciente_nome):
    pacientes = carregar_pacientes()
    if paciente_nome in pacientes and "interacao" in pacientes[paciente_nome]:
        return pacientes[paciente_nome]["interacao"]
    return []


def salvar_historico(paciente_nome, pergunta, resposta_analise):
    pacientes = carregar_pacientes()
    if paciente_nome in pacientes:
        pacientes[paciente_nome]["interacao"].append(
            {"pergunta": pergunta, "resposta": resposta_analise})
    else:
        pacientes[paciente_nome] = {"interacao": [
            {"pergunta": pergunta, "resposta": resposta_analise}]}  # Adiciona paciente com a interação
    with open(DATA_FILE, "w") as file:
        json.dump(pacientes, file, indent=4)

# Função para carregar a base de conhecimento


def carregar_base_conhecimento(base_file):
    try:
        with open(base_file, "r") as file:
            base_conhecimento = json.load(file)
        return base_conhecimento
    except FileNotFoundError:
        st.error(f"Base de conhecimento {base_file} não encontrada.")
        return {}

# Função para buscar resposta na base de conhecimento


def buscar_resposta_na_base(pergunta, base_conhecimento):
    if "hernia_de_disco" in base_conhecimento:
        hde_info = base_conhecimento["hernia_de_disco"]

        # Converte a pergunta para minúsculas para facilitar a busca
        pergunta = pergunta.lower()

        if "hernia de disco" in pergunta:
            return f"Definição: {hde_info['definicao']}\nCausas: {', '.join(hde_info['causas'])}\nSintomas: {', '.join(hde_info['sintomas'])}\nTratamentos: {', '.join(hde_info['tratamentos'])}\nPrevenção: {', '.join(hde_info['prevenção'])}\nDiagnóstico: {hde_info['diagnostico']}"

    return None


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


def agente_com_bot(sintomas, historico_medico, exames, mensagens_antigas, pergunta_usuario):
    # Carregar ambas as bases de conhecimento
    base_conhecimento_1 = carregar_base_conhecimento(BASE_CONHECIMENTO_FILE_1)
    base_conhecimento_2 = carregar_base_conhecimento(BASE_CONHECIMENTO_FILE_2)

    # Tentar buscar uma resposta nas duas bases de conhecimento
    resposta_base_1 = buscar_resposta_na_base(
        pergunta_usuario, base_conhecimento_1)
    resposta_base_2 = buscar_resposta_na_base(
        pergunta_usuario, base_conhecimento_2)

    if resposta_base_1:
        return resposta_base_1
    elif resposta_base_2:
        return resposta_base_2

    # Caso contrário, utiliza o modelo de IA
    entrada = f"Histórico Médico: {historico_medico}\nSintomas: {sintomas}\nExames: {exames}\nMensagens anteriores: {mensagens_antigas}\nPergunta do usuário: {pergunta_usuario}"
    resposta = chain.run(entrada=entrada)
    return resposta


# Interface com Streamlit
st.title("Chat com Assistente de Diagnóstico de Hérnia de Disco")

# Etapa 1: Selecionar paciente
nome_paciente = st.text_input("Digite seu nome:")

if nome_paciente:
    pacientes = carregar_pacientes()
    if nome_paciente in pacientes:
        st.success(f"Bem-vindo de volta, {nome_paciente}!")

        # Carregar histórico de mensagens do paciente
        historico_respostas = carregar_historico(nome_paciente)

        # Exibir o histórico de mensagens anteriores
        if historico_respostas:
            for item in historico_respostas:
                st.chat_message("user").markdown(item['pergunta'])
                st.chat_message("assistant").markdown(item['resposta'])
        else:
            st.chat_message("assistant").markdown(
                "Olá! Como posso ajudá-lo hoje?")

        # Campo para nova mensagem do usuário
        mensagem_usuario = st.chat_input("Digite sua mensagem:")

        if mensagem_usuario:
            # Concatenar nova mensagem com o histórico
            resposta_agente = agente_com_bot(
                sintomas=pacientes[nome_paciente]["sintomas"],
                historico_medico=pacientes[nome_paciente]["historico"],
                exames=pacientes[nome_paciente]["exames"],
                mensagens_antigas="\n".join(
                    [f"Usuário: {item['pergunta']}\nAssistente: {item['resposta']}" for item in historico_respostas]),
                pergunta_usuario=mensagem_usuario
            )

            # Mostrar mensagem do usuário
            st.chat_message("user").markdown(mensagem_usuario)
            # Mostrar resposta do agente
            st.chat_message("assistant").markdown(resposta_agente)

            # Salvar nova resposta no histórico
            salvar_historico(nome_paciente, mensagem_usuario, resposta_agente)

    else:
        st.warning("Paciente não encontrado. Digite um nome válido.")
else:
    st.warning("Por favor, digite seu nome para continuar.")
