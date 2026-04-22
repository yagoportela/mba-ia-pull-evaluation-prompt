"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

def pull_prompts_from_langsmith():
    """
    Faz o pull do prompt específico e o estrutura para salvamento local.
    """
    try:
        prompt_handle = "leonanluppi/bug_to_user_story_v1"
        print(f"Baixando prompt: {prompt_handle}...")

        prompt_obj = hub.pull(prompt_handle)
        prompt_dict = tratar_dados(prompt_obj)
        dest_path = salvar_arquivo(prompt_dict)

        print(f"Prompt salvo com sucesso em: {dest_path}")
        return True

    except Exception as e:
        print(f"Erro ao fazer pull do prompt: {e}")
        return False

def tratar_dados(prompt_obj):
    messages_data = []
    role = ""
    for message in prompt_obj.messages:
        type_str = str(type(message)).lower()
            
        if "system" in type_str:
            role = "system"
        elif "human" in type_str:
            role = "user"
        elif "ai" in type_str:
            role = "assistant"
        else:
            role = "user" # Fallback padrão para prompts de chat
            
        messages_data.append({
                "role": role,
                "content": message.prompt.template
            })

    prompt_dict = {"name": getattr(prompt_obj, "metadata", {}).get("lc_hub_repo", "empty"),
        "author": getattr(prompt_obj, "metadata", {}).get("lc_hub_owner", "empty"),
        "version": getattr(prompt_obj, "metadata", {}).get("lc_hub_commit_hash", "latest"),
        "input_variables": prompt_obj.input_variables ,
        "messages": messages_data,
    }
    
    return prompt_dict

def salvar_arquivo(prompt_dict):
    dest_path = Path("prompts/bug_to_user_story_v1.yml")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
        
    save_yaml(prompt_dict, dest_path)
    return dest_path

def main():
    """Função principal"""
    print_section_header("\nDesafio 1: Iniciando Pull do LangSmith Prompt Hub")
    if not check_env_vars(["LANGSMITH_API_KEY", "LANGSMITH_ENDPOINT", "LANGSMITH_PROJECT", "LANGSMITH_TRACING"]):
        print("falha: Variáveis de ambiente faltando.")
        return False

    success = pull_prompts_from_langsmith()

    if success:
        print("Desafio 1 concluído!")
        return True
    else:
        print("Falha no desafio 1. Verifique os logs.")
        return False

if __name__ == "__main__":
    sys.exit(main())
