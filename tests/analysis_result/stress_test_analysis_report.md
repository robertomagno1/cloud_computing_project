# Report di Analisi - Stress Test

**Generato il:** 2025-07-18 15:14:34

## Riepilogo Esecutivo

Questo report analizza le prestazioni del servizio di trascrizione audio durante il test di tipo stress test.

## Tempi di Elaborazione End-to-End per Dimensione File

| Dimensione File | Conteggio | Tempo Medio (s) | Mediana (s) | 95° %ile (s) | 99° %ile (s) | Min (s) | Max (s) | Dev Std |
|----------------|-----------|-----------------|-------------|--------------|--------------|---------|---------|----------|
| Small | 1237 | 39.41 | 38.67 | 51.43 | 66.57 | 12.78 | 96.01 | 7.75 |
| Medium | 297 | 137.95 | 134.96 | 208.54 | 254.61 | 94.77 | 269.17 | 32.22 |

## Analisi delle Richieste Locust

- **Totale Richieste**: 54624
- **Richieste Fallite**: 11512
- **Tasso di Successo**: 78.93%
- **Tempo di Risposta Medio**: 24.83 ms
- **Tempo di Risposta Mediano**: 22.82 ms
- **Tempo di Risposta Massimo**: 1004.70 ms
- **Richieste per Secondo**: 65.00

## Analisi degli Errori

- **Totale Errori**: 5756
- **Tipi di Errore Unici**: 4
- **Errore Più Comune**: CatchResponseError('Status check failed: 500')

### Distribuzione Errori:

- CatchResponseError('Status check failed: 500'): 2080 occorrenze
- CatchResponseError('S3 upload failed: 503'): 1 occorrenze
- CatchResponseError('S3 upload failed: 500'): 1 occorrenze
- CatchResponseError('Upload request failed: {"message": "Internal server error"}'): 1 occorrenze

## Insight per Stress Test

### Analisi Stress Test:
- Questo test trova il punto di rottura del sistema (10→20→40→60→80→100→120 utenti)
- Distribuzione file: 80% small, 20% medium, 0% large
- Aumenta gradualmente il carico per identificare i limiti di capacità
- Durata test: 14 minuti


## Raccomandazioni

⚠️ **Basso Tasso di Successo**: Il tasso di successo è sotto il 95%. Considera:
- Implementazione di meccanismi di retry
- Aumento dei timeout
- Revisione della gestione degli errori nelle Lambda

⚠️ **Errori Rilevati**: Il sistema ha mostrato errori durante il test. Considera:
- Analisi dettagliata dei log di errore
- Implementazione di meccanismi di recupero
- Monitoraggio proattivo degli errori

