
import sys

from pull_prompts import main as pull_prompts_from_langsmith
from utils import print_section_header
from push_prompts import main as push_optimized_prompt
from evaluate import main as evaluate
# from src.evaluate import run_evaluation           # Você criará depois

def run_workflow():

    print_section_header("Iniciando Workflow de Prompt Engineering")
    total_sucesso = 0
    total_falha = 0

    # if pull_prompts_from_langsmith():
    #     total_sucesso += 1
    # else:
    #     total_falha += 1

    # FASE 2: Aqui você edita o YAML manualmente...
    
    # FASE 3: Push
    print("\n--- Executando Fase 3: Push ---")
    if push_optimized_prompt():
        total_sucesso += 1
    else:
        total_falha += 1

    # FASE 4: Evaluate
    print("\n--- Executando Fase 4: Evaluate ---")
    if evaluate():
        total_sucesso += 1
    else:
        total_falha += 1

    print(f"\nWorkflow concluído: {total_sucesso} sucesso(s), {total_falha} falha(s).")

if __name__ == "__main__":
    try:
        run_workflow()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)