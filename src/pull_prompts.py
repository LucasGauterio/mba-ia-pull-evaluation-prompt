"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path

# Configurar encoding do console para evitar erros no Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt leonanluppi/bug_to_user_story_v1 do LangSmith Prompt Hub
    e salva localmente em prompts/bug_to_user_story_v1.yml.
    """
    print_section_header("PULL DE PROMPT DO LANGSMITH HUB")
    
    # Verificar variáveis necessárias
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print(f"Buscando prompt '{prompt_name}' no LangSmith Hub...")
    
    try:
        # Fazer o pull do prompt
        prompt = hub.pull(prompt_name)
        print("[OK] Prompt recuperado com sucesso do Hub.")
        
        system_prompt = ""
        user_prompt = ""
        
        # Processar mensagens do ChatPromptTemplate
        if hasattr(prompt, 'messages'):
            for msg in prompt.messages:
                cls_name = msg.__class__.__name__.lower()
                
                # Extrair o conteúdo do template
                content = ""
                if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                    content = msg.prompt.template
                elif hasattr(msg, 'content'):
                    content = msg.content
                
                # Identificar se é System ou User/Human
                if 'system' in cls_name:
                    system_prompt = content
                elif 'human' in cls_name or 'user' in cls_name:
                    user_prompt = content
        else:
            # Caso não seja chat template
            if hasattr(prompt, 'template'):
                system_prompt = prompt.template
        
        # Estruturar o YAML
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories (v1)",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }
        
        # Salvar no arquivo local
        dest_path = "prompts/bug_to_user_story_v1.yml"
        if save_yaml(prompt_data, dest_path):
            print(f"[OK] Prompt salvo localmente em: {dest_path}")
            return True
        else:
            print("[ERRO] Erro ao salvar o arquivo YAML localmente.")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao conectar ou fazer pull do LangSmith Hub: {e}")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
