# Audio Concatenator

Uno script Python per concatenare file audio in gruppi specificati, generando file audio più lunghi a partire da una cartella di file più brevi.

## Requisiti

- Python 3.7+
- [ffmpeg](https://ffmpeg.org/) installato sul sistema (necessario per la compatibilità con molti formati audio)
- Dipendenze Python elencate in `requirements.txt`

## Installazione

### 1. Crea un ambiente virtuale

Su **Linux/macOS**:
```bash
python -m venv audio_env
source audio_env/bin/activate
```

Su **Windows**:
```bash
python -m venv audio_env
audio_env\Scripts\activate
```

### 2. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 3. Assicurati che ffmpeg sia installato

- **macOS:**  
  `brew install ffmpeg`
- **Ubuntu/Debian:**  
  `sudo apt install ffmpeg`
- **Windows:**  
  Scarica da [ffmpeg.org](https://ffmpeg.org/download.html) e aggiungi `ffmpeg` al PATH

## Utilizzo

### Script principale

Per concatenare i file audio di una cartella in gruppi da 3:
```bash
python audio_concatenator.py "/path/to/audio/folder" 3
```

Per specificare una cartella di output diversa:
```bash
python audio_concatenator.py "/path/to/audio/folder" 3 -o "/path/to/output/folder"
```

- Sostituisci `"/path/to/audio/folder"` con il percorso reale della cartella contenente i file audio.
- Sostituisci `3` con il numero di file da concatenare per ciascun gruppo.
- L'output verrà salvato nella cartella `concatenated` dentro la cartella di input, a meno che non venga specificata un'altra cartella con `-o`.

### Esempio di utilizzo da Python

Puoi anche usare la funzione direttamente in uno script Python:

```python
from audio_concatenator import concatenate_audio_groups

folder_path = "/percorso/alla/cartella/audio"
group_size = 3
output_folder = "/percorso/alla/cartella/output"  # opzionale

concatenate_audio_groups(folder_path, group_size, output_folder)
```

## Output

I file concatenati saranno nominati come:
```
concatenated_group_01.mp3
concatenated_group_02.mp3
...
```
e saranno salvati nella cartella di output scelta.

---

**Nota**: Il numero di file generati corrisponderà a `ceil(totale_file / group_size)`.  
Se hai 11 file e scegli `3` come dimensione gruppo, otterrai 4 file di output: 3+3+3+2.
