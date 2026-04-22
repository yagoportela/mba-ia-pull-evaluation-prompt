"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """ 
    try:
        # 1. Reconstrói as mensagens usando Tuplas
        formatted_messages = []
        for msg in prompt_data.get("messages", []):
            role = msg.get("role", "").lower()
            content = msg.get("content", "")

            if role == "system":
                formatted_messages.append(SystemMessagePromptTemplate.from_template(content))

            if role == "user":
                formatted_messages.append(HumanMessagePromptTemplate.from_template(content))
            

        # 2. Cria o objeto ChatPromptTemplate
        prompt_template = ChatPromptTemplate.from_messages(formatted_messages)

        print(f"Enviando para o repositório: {prompt_name}...")
        
        # 3. Push para o Hub com metadados obrigatórios do desafio
        commit_url = hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True, # Torna público conforme exigido
            new_repo_description="Prompt otimizado usando Role Prompting, Few-Shot, Chain of Thought e Skeleton of Thought para converter bugs em User Stories."
        )
        
        print(f"Push realizado com sucesso!")
        print(f"Link público: {commit_url}")
        return True

    except Exception as e:
        print(f"Erro ao fazer push: {e}")
        return False




def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    # Verifica se os dados foram carregados
    if not prompt_data:
        return False, ["Os dados do prompt estão vazios."]

    # Verifica existencia da lista de mensagens
    if "messages" not in prompt_data or not isinstance(prompt_data["messages"], list):
        errors.append("O campo 'messages' é obrigatório e deve ser uma lista.")
        return False, errors

    messages = prompt_data["messages"]
    if len(messages) == 0:
        errors.append("A lista 'messages' não pode estar vazia.")
    
    # Verifica a integridade de cada mensagem e se existe um System Prompt
    has_system = False
    for i, msg in enumerate(messages):
        if "role" not in msg or "content" not in msg:
            errors.append(f"A mensagem no índice {i} deve conter as chaves 'role' e 'content'.")
        elif msg.get("role") == "system":
            has_system = True
            
    if not has_system:
        errors.append("O prompt otimizado precisa obrigatoriamente de uma mensagem com role 'system'.")

    # Retorna True se não houver erros
    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    """Função principal"""
    print_section_header("Fase 3: Validação e Push do Prompt Otimizado")
    
    # 1. Checagem de Ambiente
    if not check_env_vars(["LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "LANGSMITH_PROJECT", "LANGSMITH_TRACING", "USERNAME_LANGSMITH_HUB"]):
        print("falha: Variáveis de ambiente faltando.")
        return False

    # 2. Carrega o YAML
    file_path = "prompts/bug_to_user_story_v2.yml"
    print(f"Carregando arquivo: {file_path}")
    try:
        prompt_data = load_yaml(file_path) 
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado. Complete a Fase 2 primeiro.")
        return 1
    except Exception as e:
        print(f"Erro ao ler o YAML: {e}")
        return 1

    # 3. Validação do Prompt
    print("Validando a estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    
    if not is_valid:
        print("Validação falhou! Corrija os erros no YAML:")
        for erro in errors:
            print(f"  - {erro}")
        return 1
    
    print("Estrutura validada com sucesso.")

    # 4. Formata o nome e faz o Push
    username = os.environ.get("USERNAME_LANGSMITH_HUB")
    prompt_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
