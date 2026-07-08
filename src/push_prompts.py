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
from pathlib import Path

# Configurar encoding do console para evitar erros no Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


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
        # Extrair dados do prompt
        system_prompt = prompt_data.get("system_prompt", "").strip()
        user_prompt = prompt_data.get("user_prompt", "").strip()
        description = prompt_data.get("description", "Prompt otimizado para mapeamento de bugs em User Stories")
        tags = prompt_data.get("tags", [])
        techniques = prompt_data.get("techniques_applied", [])
        
        # Combinar as tags com as técnicas aplicadas nos metadados
        combined_tags = list(set(tags + techniques))

        # Criar o template de prompt do LangChain
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        print(f"Fazendo push do prompt '{prompt_name}'...")
        # Executar push público no LangSmith Hub
        hub.push(
            repo_full_name=prompt_name,
            object=prompt_template,
            new_repo_description=description,
            new_repo_is_public=True,
            tags=combined_tags
        )
        print(f"[OK] Prompt publicado com sucesso no LangSmith Hub em: https://smith.langchain.com/hub/{prompt_name}")
        return True

    except Exception as e:
        print(f"[ERRO] Erro ao fazer push do prompt: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPT OTIMIZADO PARA O LANGSMITH HUB")

    # Verificar variáveis de ambiente
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_file = "prompts/bug_to_user_story_v2.yml"
    
    # Carregar o prompt do arquivo local
    print(f"Carregando prompt de '{prompt_file}'...")
    data = load_yaml(prompt_file)
    if not data:
        print(f"[ERRO] Não foi possível ler o arquivo: {prompt_file}")
        return 1

    prompt_key = "bug_to_user_story_v2"
    if prompt_key not in data:
        print(f"[ERRO] Chave '{prompt_key}' não encontrada no arquivo {prompt_file}")
        return 1

    prompt_data = data[prompt_key]

    # Validar o prompt
    print("Validando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("[ERRO] Erros de validação encontrados no prompt:")
        for error in errors:
            print(f"   - {error}")
        return 1
    print("[OK] Validação concluída com sucesso.")

    # Fazer o push
    full_prompt_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(full_prompt_name, prompt_data)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
