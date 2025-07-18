# Report di Analisi - Spike Test

**Generato il:** 2025-07-18 15:14:33

## Riepilogo Esecutivo

Questo report analizza le prestazioni del servizio di trascrizione audio durante il test di tipo spike test.

## Tempi di Elaborazione End-to-End per Dimensione File

| Dimensione File | Conteggio | Tempo Medio (s) | Mediana (s) | 95° %ile (s) | 99° %ile (s) | Min (s) | Max (s) | Dev Std |
|----------------|-----------|-----------------|-------------|--------------|--------------|---------|---------|----------|
| Small | 598 | 37.77 | 36.98 | 49.53 | 67.02 | 11.86 | 94.55 | 8.07 |
| Medium | 70 | 138.42 | 133.04 | 203.89 | 247.46 | 99.35 | 250.75 | 31.50 |

## Analisi delle Richieste Locust

- **Totale Richieste**: 10218
- **Richieste Fallite**: 2256
- **Tasso di Successo**: 77.92%
- **Tempo di Risposta Medio**: 25.94 ms
- **Tempo di Risposta Mediano**: 23.20 ms
- **Tempo di Risposta Massimo**: 824.90 ms
- **Richieste per Secondo**: 8.51

## Analisi degli Errori

- **Totale Errori**: 1128
- **Tipi di Errore Unici**: 4
- **Errore Più Comune**: CatchResponseError('Status check failed: 500')

### Distribuzione Errori:

- CatchResponseError('Status check failed: 500'): 387 occorrenze
- CatchResponseError('S3 upload failed: 503'): 1 occorrenze
- CatchResponseError('S3 upload failed: 500'): 1 occorrenze
- CatchResponseError('Upload request failed: {"message": "Internal server error"}'): 1 occorrenze

## Insight per Spike Test

### Analisi Spike Test:
- Questo test simula picchi improvvisi di traffico (5→50→5→75→5→100→5 utenti)
- Distribuzione file: 80% small, 20% medium, 0% large
- Verifica la capacità del sistema di gestire aumenti improvvisi di carico
- Durata test: 20 minuti


## Raccomandazioni

⚠️ **Basso Tasso di Successo**: Il tasso di successo è sotto il 95%. Considera:
- Implementazione di meccanismi di retry
- Aumento dei timeout
- Revisione della gestione degli errori nelle Lambda

⚠️ **Errori Rilevati**: Il sistema ha mostrato errori durante il test. Considera:
- Analisi dettagliata dei log di errore
- Implementazione di meccanismi di recupero
- Monitoraggio proattivo degli errori

