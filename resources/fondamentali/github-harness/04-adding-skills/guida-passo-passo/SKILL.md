---
name: guida-passo-passo
description: >-
  Usa quando un dipendente chiede aiuto per configurare o risolvere un problema tecnico
  (account, MFA, VPN, Outlook, Teams, OneDrive, stampanti, dispositivi) presso Zava S.p.A.
  Raccoglie il contesto, crea una guida passo passo personalizzata seguendo il template
  aziendale e, su richiesta, la invia via email all'utente corrente.
license: MIT
metadata:
  version: 1.0.0
  scenario: Zava S.p.A. - Supporto Tecnico IT
---

# Guida passo passo Zava

## Passaggi

1. **Raccogli gli input** (chiedi solo quelli mancanti, in un unico messaggio):
   - attivita o problema da risolvere, normalizzato in un titolo breve (esempio "Configurare la MFA con Microsoft Authenticator");
   - categoria: Account e accessi, Rete e VPN, Microsoft 365, Dispositivi, Stampa oppure Altro;
   - sistema operativo / dispositivo: Windows, macOS, iOS oppure Android;
   - livello di esperienza dell'utente: Base, Intermedio oppure Avanzato (se non indicato usa Base);
   - eventuale messaggio di errore visualizzato.
2. **Leggi i riferimenti** nella cartella riferimenti di questa skill:
   - contenuti-aziendali.md contiene i testi fissi da copiare parola per parola;
   - template-guida.md contiene la struttura della guida e le regole di compilazione.
3. **Consulta la knowledge base** dell'agente per recuperare la procedura ufficiale. Se la
   procedura non e presente, usa i passaggi standard Microsoft per il dispositivo indicato e
   aggiungi "(verificare con l'IT)" accanto ai passaggi di cui non sei sicuro.
4. **Compila la guida** seguendo il template. Le parti variabili (prerequisiti, passaggi,
   verifica, problemi comuni) vanno scritte in base ad attivita, dispositivo e livello di esperienza.
5. **Mostra la guida** in Markdown e chiedi se l'utente vuole riceverla via email.
6. **Invio via email** (solo se l'utente lo chiede):
   - recupera l'indirizzo dell'utente con lo strumento Get my profile (V2);
   - converti la guida in HTML semplice (titoli h1 e h2, paragrafi, elenchi numerati per i
     passaggi, elenchi puntati per il resto), senza modificarne il contenuto;
   - invia con lo strumento Invia guida via email: destinatario = email dell'utente,
     oggetto = "Guida: " seguito dal titolo breve (massimo 8 parole totali), corpo = HTML della guida;
   - conferma l'invio in una riga.

## Regole

- Non modificare mai i contenuti aziendali fissi.
- Rispetta l'ordine delle sezioni del template.
- Un solo passaggio per azione: ogni passaggio inizia con un verbo (Apri, Seleziona, Inserisci...).
- Indica i nomi esatti di menu e pulsanti in **grassetto**.
- Non chiedere e non inserire mai password, codici MFA o altri dati sensibili.
- Non suggerire passaggi che richiedono diritti di amministratore: in quel caso rimanda al Service Desk.
- Non inventare contatti, link o orari diversi da quelli dei riferimenti.
- Scrivi in italiano, con linguaggio chiaro e non tecnico per il livello Base.
