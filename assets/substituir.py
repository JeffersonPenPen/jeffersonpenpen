import os

# --- CONFIGURAÇÃO ---
# 1. Coloque aqui o caminho completo da pasta onde estão os arquivos que você quer modificar.
#    Exemplo para Windows: 'D:\\GitHub\\meu-projeto\\arquivos'
#    Exemplo para Mac/Linux: '/home/usuario/documentos/meu-projeto'
PASTA_ALVO ="D:\\GitHub\\JeffersonPenPen" 

# 2. Nome do arquivo que contém as regras de substituição.
ARQUIVO_REGRAS = 'regras.txt'
# --------------------


def carregar_regras(caminho_arquivo_regras):
    """Lê o arquivo de regras e o transforma em um dicionário."""
    regras = {}
    try:
        with open(caminho_arquivo_regras, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if '|' in linha:
                    partes = linha.split('|', 1)
                    if len(partes) == 2:
                        antes, depois = partes
                        regras[antes.strip()] = depois.strip()
        print(f"✅ {len(regras)} regras de substituição carregadas de '{caminho_arquivo_regras}'.")
        return regras
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de regras '{caminho_arquivo_regras}' não encontrado.")
        print("Crie este arquivo na mesma pasta do script com o formato 'texto_antigo|texto_novo'.")
        return None
    except Exception as e:
        print(f"❌ ERRO ao ler o arquivo de regras: {e}")
        return None

def processar_pasta(pasta, regras):
    """Percorre todos os arquivos na pasta alvo e aplica as regras."""
    if not os.path.isdir(pasta):
        print(f"❌ ERRO: A pasta alvo '{pasta}' não existe ou não é uma pasta.")
        return

    print(f"\n--- Iniciando processamento na pasta: {pasta} ---\n")
    
    arquivos_processados = 0
    arquivos_modificados = 0

    for nome_arquivo in os.listdir(pasta):
        caminho_completo = os.path.join(pasta, nome_arquivo)

        if os.path.isfile(caminho_completo):
            arquivos_processados += 1
            print(f"🔎 Processando arquivo: {nome_arquivo}")
            
            try:
                with open(caminho_completo, 'r', encoding='utf-8') as f:
                    conteudo_original = f.read()
                
                conteudo_modificado = conteudo_original
                
                # Aplica cada regra ao conteúdo do arquivo
                for antes, depois in regras.items():
                    conteudo_modificado = conteudo_modificado.replace(antes, depois)
                
                # Se o conteúdo mudou, salva o arquivo
                if conteudo_modificado != conteudo_original:
                    with open(caminho_completo, 'w', encoding='utf-8') as f:
                        f.write(conteudo_modificado)
                    print("  -> 💾 Modificações salvas.")
                    arquivos_modificados += 1
                else:
                    print("  -> Nenhuma modificação necessária.")

            except UnicodeDecodeError:
                print(f"  -> ⚠️ AVISO: Não foi possível ler o arquivo '{nome_arquivo}'. Ele pode não ser um arquivo de texto simples (ex: imagem, binário).")
            except Exception as e:
                print(f"  -> ❌ ERRO ao processar o arquivo '{nome_arquivo}': {e}")
    
    print(f"\n--- Processamento Concluído ---")
    print(f"Arquivos totais na pasta: {arquivos_processados}")
    print(f"Arquivos modificados: {arquivos_modificados}")


if __name__ == "__main__":
    print("--- Script de Substituição em Lote ---")
    
    # Adendo de segurança
    print("\n⚠️ AVISO: Este script modificará os arquivos permanentemente.")
    print("É altamente recomendável fazer um BACKUP da sua pasta antes de continuar.")
    
    confirmacao = input("Você fez um backup e deseja continuar? (s/n): ")
    
    if confirmacao.lower() == 's':
        regras_carregadas = carregar_regras(ARQUIVO_REGRAS)
        if regras_carregadas:
            processar_pasta(PASTA_ALVO, regras_carregadas)
    else:
        print("Operação cancelada pelo usuário.")