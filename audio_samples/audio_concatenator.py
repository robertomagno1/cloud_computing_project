import os
import argparse
from pydub import AudioSegment
from pathlib import Path
import math

def get_audio_files(folder_path, supported_formats=None):
    """
    Ottiene tutti i file audio dalla cartella specificata.
    
    Args:
        folder_path (str): Percorso della cartella contenente i file audio
        supported_formats (list): Lista di formati audio supportati
    
    Returns:
        list: Lista ordinata dei percorsi dei file audio
    """
    if supported_formats is None:
        supported_formats = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'] 
    
    audio_files = []
    folder = Path(folder_path)
    
    if not folder.exists():
        raise FileNotFoundError(f"La cartella {folder_path} non esiste")
    
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in supported_formats:
            audio_files.append(str(file))
    
    # Ordina i file per nome
    audio_files.sort()
    return audio_files

def concatenate_audio_files(file_list, output_path):
    """
    Concatena una lista di file audio in un singolo file.
    
    Args:
        file_list (list): Lista dei percorsi dei file audio da concatenare
        output_path (str): Percorso del file di output
    """
    if not file_list:
        print("Nessun file da concatenare")
        return
    
    print(f"Concatenando {len(file_list)} file:")
    for file in file_list:
        print(f"  - {os.path.basename(file)}")
    
    # Carica il primo file audio
    combined = AudioSegment.from_file(file_list[0])
    
    # Concatena i file rimanenti
    for audio_file in file_list[1:]:
        try:
            audio = AudioSegment.from_file(audio_file)
            combined += audio
        except Exception as e:
            print(f"Errore nel caricare {audio_file}: {e}")
            continue
    
    # Esporta il file combinato
    try:
        combined.export(output_path, format="mp3")
        print(f"File salvato: {output_path}")
    except Exception as e:
        print(f"Errore nel salvare {output_path}: {e}")

def concatenate_audio_groups(folder_path, group_size, output_folder=None):
    """
    Concatena i file audio in gruppi della dimensione specificata.
    
    Args:
        folder_path (str): Percorso della cartella contenente i file audio
        group_size (int): Numero di file da concatenare per gruppo
        output_folder (str): Cartella di output (opzionale)
    """
    # Ottieni tutti i file audio
    audio_files = get_audio_files(folder_path)
    
    if not audio_files:
        print("Nessun file audio trovato nella cartella specificata")
        return
    
    print(f"Trovati {len(audio_files)} file audio")
    print(f"Creando gruppi di {group_size} file")
    
    # Calcola il numero di gruppi
    num_groups = math.ceil(len(audio_files) / group_size)
    print(f"Verranno creati {num_groups} file concatenati")
    
    # Imposta la cartella di output
    if output_folder is None:
        output_folder = os.path.join(folder_path, "concatenated")
    
    # Crea la cartella di output se non esiste
    os.makedirs(output_folder, exist_ok=True)
    
    # Concatena i file in gruppi
    for i in range(num_groups):
        start_idx = i * group_size
        end_idx = min(start_idx + group_size, len(audio_files))
        
        # Ottieni i file per questo gruppo
        group_files = audio_files[start_idx:end_idx]
        
        # Nome del file di output
        output_filename = f"concatenated_group_{i+1:02d}.mp3"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"\n--- Gruppo {i+1}/{num_groups} ---")
        concatenate_audio_files(group_files, output_path)

def main():
    parser = argparse.ArgumentParser(
        description="Concatena file audio in gruppi della dimensione specificata"
    )
    parser.add_argument(
        "folder_path",
        help="Percorso della cartella contenente i file audio"
    )
    parser.add_argument(
        "group_size",
        type=int,
        help="Numero di file audio da concatenare per gruppo"
    )
    parser.add_argument(
        "-o", "--output",
        help="Cartella di output (default: cartella 'concatenated' nella cartella di input)"
    )
    
    args = parser.parse_args()
    
    try:
        concatenate_audio_groups(args.folder_path, args.group_size, args.output)
        print("\nConcatenazione completata!")
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
