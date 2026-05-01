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
        # 1. Extrai os dados do prompt
        prompt_config = prompt_data.get("bug_to_user_story_v2", {})
        system_prompt = prompt_config.get("system_prompt", "")
        user_prompt = prompt_config.get("user_prompt", "")

        formatted_messages = [
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template(user_prompt)
        ]
            

        # 2. Cria o objeto ChatPromptTemplate
        prompt_template = ChatPromptTemplate.from_messages(formatted_messages)

        print(f"Enviando para o repositório: {prompt_name}...")
        
        # 3. Push para o Hub com metadados obrigatórios do desafio
        commit_url = hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True, # Torna público conforme exigido
            new_repo_description=prompt_config.get("description", "Prompt otimizado para converter bugs em User Stories.")
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

    # Extrai o nó raiz
    prompt_config = prompt_data.get("bug_to_user_story_v2")
    if not prompt_config:
        errors.append("A chave raiz 'bug_to_user_story_v2' não foi encontrada.")
        return False, errors

    if "system_prompt" not in prompt_config or not prompt_config["system_prompt"]:
        errors.append("O campo 'system_prompt' é obrigatório.")
        
    if "user_prompt" not in prompt_config or not prompt_config["user_prompt"]:
        errors.append("O campo 'user_prompt' é obrigatório.")

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
        if not prompt_data:
            return False
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado. Complete a Fase 2 primeiro.")
        return False
    except Exception as e:
        print(f"Erro ao ler o YAML: {e}")
        return False

    # 3. Validação do Prompt
    print("Validando a estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    
    if not is_valid:
        print("Validação falhou! Corrija os erros no YAML:")
        for erro in errors:
            print(f"  - {erro}")
        return False
    
    print("Estrutura validada com sucesso.")

    # 4. Formata o nome e faz o Push
    username = os.environ.get("USERNAME_LANGSMITH_HUB")
    prompt_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
