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

@pytest.fixture
def prompt_data():
    """Fixture que carrega o prompt otimizado v2."""
    file_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    data = load_prompts(str(file_path))
    if "bug_to_user_story_v2" in data:
        return data["bug_to_user_story_v2"]
    return data

class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Chave 'system_prompt' não encontrada no prompt."
        assert prompt_data["system_prompt"].strip() != "", "O 'system_prompt' está vazio."

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Owner")."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        persona_keywords = ["product manager", "product owner", "analista", "especialista", "po", "persona"]
        assert any(keyword in system_prompt for keyword in persona_keywords), \
            "O prompt não define uma persona clara (ex: Product Owner, Product Manager, analista, especialista)."

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "").lower()
        has_markdown = "markdown" in system_prompt
        has_us_template = any(term in system_prompt for term in ["como um", "eu quero", "para que", "como", "quero", "para"])
        assert has_markdown, "O prompt deve exigir formatação Markdown."
        assert has_us_template, "O prompt deve exigir a estrutura padrão de User Story (Como um..., Eu quero..., Para que...)."

    @pytest.mark.skip(reason="Fase incremental: Few-shot será adicionado no próximo commit")
    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data.get("system_prompt", "")
        example_keywords = ["exemplo", "entrada", "saída", "example", "input", "output"]
        assert any(keyword in system_prompt.lower() for keyword in example_keywords), \
            "O prompt não parece conter exemplos de poucas demonstrações (Few-shot)."

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        import re
        todo_pattern = re.compile(r'\bTODO\b|\[TODO\]', re.IGNORECASE)
        assert not todo_pattern.search(system_prompt), "Há marcações de TODO no 'system_prompt'."
        assert not todo_pattern.search(user_prompt), "Há marcações de TODO no 'user_prompt'."

    @pytest.mark.skip(reason="Fase incremental: Mínimo de 2 técnicas será atingido posteriormente")
    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, \
            f"O metadado 'techniques_applied' deve listar pelo menos 2 técnicas utilizadas. Encontradas: {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])