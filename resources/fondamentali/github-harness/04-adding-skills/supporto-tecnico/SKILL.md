---
name: supporto-tecnico
description: >-
  Usa quando un dipendente segnala un problema tecnico con un dispositivo, un'applicazione o la
  rete aziendale. Classifica il problema in Hardware, Software o Rete, propone la checklist
  ufficiale di primo livello e, se il problema persiste, prepara il riepilogo per l'escalation.
license: MIT
metadata:
  version: 1.0.0
  scenario: Zava S.p.A. - Help Desk di primo livello
---
# Procedura di supporto tecnico di primo livello

Usa questa procedura quando un dipendente segnala un problema tecnico. Non usarla per reset di
password, sblocco di account o richieste di nuovi dispositivi.

## Passaggi

1. **Capisci il problema.** Se non è già chiaro dalla conversazione, chiedi con UNA sola domanda
   quale dispositivo o applicazione è coinvolto e quale messaggio di errore compare.
2. **Classifica** il problema in una sola categoria: Hardware, Software oppure Rete. Se non riesci
   a classificarlo, chiedi all'utente di scegliere tra le tre categorie.
3. **Proponi la checklist** della categoria, in una tabella con le colonne Passo e Azione, senza
   aggiungere passi non presenti nell'elenco:
   - Hardware: controlla cavi e collegamenti; riavvia il dispositivo; verifica surriscaldamento o
     rumori anomali; scollega e ricollega le periferiche; prova un altro cavo di alimentazione;
     esegui la diagnostica hardware se disponibile.
   - Software: chiudi e riapri l'applicazione; riavvia il computer; verifica gli aggiornamenti;
     controlla i requisiti di sistema; annota il messaggio di errore; reinstalla l'applicazione.
   - Rete: controlla il cavo di rete o il Wi-Fi; riavvia il dispositivo; verifica la configurazione
     IP con ipconfig; prova il comando ping; svuota la cache DNS; disattiva temporaneamente la VPN.
4. **Verifica l'esito.** Chiedi se il problema è risolto. Non considerarlo risolto finché l'utente
   non lo conferma.
5. **Escalation.** Se il problema persiste dopo due tentativi, consiglia di aprire un ticket e
   prepara un riepilogo con: categoria, dispositivo o applicazione, sintomi, messaggi di errore,
   passi già eseguiti e relativo esito.

## Regole

- Non chiedere mai password, codici OTP o altre credenziali.
- Non suggerire di aggirare controlli di sicurezza o policy aziendali.
- Rispondi in italiano, con tono professionale, calmo e neutro.

## Criteri di completamento

La procedura è completa quando l'utente conferma che il problema è risolto, oppure quando hai
fornito il riepilogo per l'escalation.
