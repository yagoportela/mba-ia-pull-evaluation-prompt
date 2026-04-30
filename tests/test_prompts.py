"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        self.prompt_data = load_prompts(str(prompt_path))
        self.system_prompt = ""
        
        if "messages" in self.prompt_data:
            for msg in self.prompt_data["messages"]:
                if msg.get("role") == "system":
                    self.system_prompt = msg.get("content", "")
                    break

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert self.system_prompt != "", "O prompt de sistema não foi encontrado ou está vazio."

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        lower_prompt = self.system_prompt.lower()
        assert "você é" in lower_prompt or "você atua como" in lower_prompt or "aja como" in lower_prompt, \
            "O prompt não define claramente uma persona (ex: 'Você é um...')."

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        lower_prompt = self.system_prompt.lower()
        assert "markdown" in lower_prompt or "user story" in lower_prompt or "formato" in lower_prompt or "padrão" in lower_prompt, \
            "O prompt não menciona uma exigência de formato (ex: Markdown, User Story)."

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        lower_prompt = self.system_prompt.lower()
        has_examples = "exemplo" in lower_prompt and "entrada" in lower_prompt and "saída" in lower_prompt
        assert has_examples, "O prompt não parece conter exemplos de entrada/saída (Few-shot)."

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "[TODO]" not in self.system_prompt and "TODO" not in self.system_prompt, \
            "Foram encontradas marcações 'TODO' no prompt."

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list) and len(techniques) >= 2, \
            f"O prompt deve listar pelo menos 2 técnicas em 'techniques_applied'. Encontradas: {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])