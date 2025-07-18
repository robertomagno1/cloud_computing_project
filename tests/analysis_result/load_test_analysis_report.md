# Report di Analisi - Load Test

**Generato il:** 2025-07-18 15:14:33

## Riepilogo Esecutivo

Questo report analizza le prestazioni del servizio di trascrizione audio durante il test di tipo load test.

## Tempi di Elaborazione End-to-End per Dimensione File

| Dimensione File | Conteggio | Tempo Medio (s) | Mediana (s) | 95° %ile (s) | 99° %ile (s) | Min (s) | Max (s) | Dev Std |
|----------------|-----------|-----------------|-------------|--------------|--------------|---------|---------|----------|
| Small | 160 | 39.06 | 42.72 | 62.04 | 71.07 | 12.60 | 76.05 | 14.65 |
| Medium | 67 | 145.21 | 135.72 | 221.45 | 255.07 | 92.46 | 261.05 | 36.27 |
| Large | 17 | 314.48 | 315.69 | 357.36 | 363.05 | 264.81 | 364.48 | 28.60 |

## Analisi delle Richieste Locust

- **Totale Richieste**: 2356
- **Richieste Fallite**: 0
- **Tasso di Successo**: 100.00%
- **Tempo di Risposta Medio**: 30.16 ms
- **Tempo di Risposta Mediano**: 27.51 ms
- **Tempo di Risposta Massimo**: 891.56 ms
- **Richieste per Secondo**: 1.58

## Insight per Load Test

### Analisi Load Test:
- Questo test simula un carico normale con scaling graduale (5→15→30→15→5 utenti)
- Distribuzione file: 60% small, 30% medium, 10% large
- Tempo di attesa adattivo basato sui job attivi
- Durata test: 25 minuti


## Raccomandazioni

