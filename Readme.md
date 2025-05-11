## Projekat simulacije saobraćaja

### 1. Metodologija

1. **Učitavanje mreže**
   - Preuzimanje grafova drumskih puteva pomoću OSMnx.
2. **Kreiranje hiper-grafa (ClusterGraph)**
   - Klasterovanje čvorova na osnovu fizičke udaljenosti (100 m).
   - Svaki klaster postaje novi čvor u ClusterGraph-u.
3. **Simulacija saobraćaja**
   - Generišu se nasumične parove čvorova.
   - Na svakom grafu (regularnom i klasterskom) se pokreće Dijkstra za najkraći put.
   - Prate se čvorovi koji se najviše koriste u putanjama.
4. **Ubrzanje preko ClusterGraph-a**
   - Dijkstra na manjem grafu (ClusterGraph).
   - Ekspanzija pronađenog puta: uzimaju se svi originalni čvorovi iz klastera i njihove međuveze.
   - Na tom manjem grafu se simulacija pokreće znatno brže.

### 2. Rezultati

| Lokacija | Graf          | Čvorovi | Vreme kreiranja (s) | Vreme simulacije (s) | Ubrzanje |
|----------|---------------|---------|---------------------|-----------------------|----------|
| Prijedor | Regular       | 5 249   | 0.12                | 2 145.28              | –        |
| Prijedor | ClusterGraph  |   863   | 1.33                | 1 028.21              | ~2×      |
| Beograd  | Regular       | 106 089 | 1.37                | 41 868.48             | –        |
| Beograd  | ClusterGraph  |  18 351 | 29.34               | 5 123.69              | ~8×      |

*Simulacije:* Prijedor – 15 simulacija po 10 000 putanja; Beograd – 5 simulacija po 10 000 putanja.

