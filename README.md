# Crimi Gang

Il sito di **Cristian e Noemi**: app, giochi e piccoli mondi creati insieme per passione.

**Sito:** https://crimi-gang.github.io/

**Contatti:** crimisupport@gmail.com

## Pagine

- Home: `/`
- Progetti: `/progetti.html`
- Crimi Love: `/crimi-love.html`
- Tiny Cozy Town: `/tiny-cozy-town.html`
- Sbrokk!: `/sbrokk.html`
- Chi siamo: `/chi-siamo.html`
- Contatti: `/contatti.html`
- Privacy del sito: `/privacy.html`
- Privacy di Tiny Cozy Town: `/privacy-tiny-cozy-town.html`
- Privacy di SBROKKO!: `/privacy-sbrokko.html`
- Venditore pubblicitario autorizzato: `/app-ads.txt`
- Pagina di errore: `/404.html`

Il sito è statico, in italiano e responsive. Non richiede un servizio backend, pacchetti JavaScript, analytics o font esterni. Il contatto apre il programma di posta; il sito non invia email da solo. I progetti sono indicati come in sviluppo, senza link a download non ancora disponibili.

## Modificare e verificare

Le pagine HTML sono generate da `build.py`, che contiene testi e componenti comuni. `styles-source.css` definisce l'aspetto; il builder genera `styles.css` compresso e `site.js` gestisce menu mobile, copia dell'email e gallerie con dialog accessibile. Non modificare soltanto gli HTML se vuoi conservare le modifiche alla prossima generazione.

L'informativa del gioco ha una sorgente dedicata in `privacy-tiny-cozy-town.md`, aggiornata dal documento `docs/PRIVACY_POLICY.it.md` del progetto Tiny Cozy Town. Il builder la converte in HTML, con indice e ancore. Dopo una modifica ai trattamenti, aggiornare la sorgente e rigenerare le pagine. Il footer di tutte le pagine rimanda alla privacy del sito; Contatti e la pagina del gioco rimandano anche alla privacy specifica dell'app. SBROKKO! ha una sorgente separata in `privacy-sbrokko.md`, verificata rispetto al progetto Sbrokko-Game e alla configurazione del 22 ottobre 2026: salvataggio locale con backup, indizi tramite rewarded, interstitial, UMP e annunci di test. Le informative dei giochi sono distinte da quella di Crimi Love.

`app-ads.txt` deve restare alla radice del sito e contiene soltanto il publisher AdMob comunicato dal titolare. Per la scheda App Store di Tiny Cozy Town usare URL marketing `https://crimi-gang.github.io/tiny-cozy-town.html`, URL assistenza `https://crimi-gang.github.io/contatti.html` e URL privacy `https://crimi-gang.github.io/privacy-tiny-cozy-town.html`. La pubblicazione del file non sostituisce la verifica di idoneità Google.

URL pubblico della privacy di SBROKKO!, utilizzabile nei campi privacy di AdMob e App Store Connect: `https://crimi-gang.github.io/privacy-sbrokko.html`. La pubblicazione della pagina non attiva messaggi UMP o pubblicità nell’account.

Richiede Python 3.9 o successivo. Dalla cartella del sito:

```sh
python3 build.py
python3 check.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Apri http://127.0.0.1:8765/. Non aprire direttamente gli HTML con `file://`.

La galleria supporta tastiera, Escape e ritorno del focus al pulsante di apertura. Il menu espone lo stato di apertura e supporta Escape. Le animazioni rispettano la preferenza per il movimento ridotto. Navigazione e immagini delle pagine restano disponibili senza JavaScript; l'ingrandimento e la copia richiedono JavaScript.

## Immagini e prestazioni

Le immagini pubblicate usano WebP con `srcset` e `sizes`: il browser sceglie la risoluzione adatta al riquadro e alla densità dello schermo. Gli originali PNG restano conservati. Le gallerie aprono la variante più grande; le immagini fuori dalla prima schermata si caricano in modo differito. Ogni immagine dichiara larghezza e altezza e CSS/JavaScript hanno un URL legato al contenuto per aggiornare correttamente le cache.

`image-manifest.json` collega ogni PNG alle sue varianti. Dopo aver aggiunto o aggiornato immagini, eseguire `python3 build.py`, `python3 optimize_images.py` e di nuovo `python3 build.py`. La conversione richiede `cwebp` da libwebp; per ricostruire il sito con le varianti già presenti basta Python. Se un PNG cambia senza rigenerare le varianti, il builder usa il nuovo originale anziché mostrare una versione precedente.

La revisione del 21 ottobre 2026 riduce il peso delle 30 immagini attive da 3.526 MB di PNG a 0.655 MB di WebP alla risoluzione massima (circa 81% in meno). Il risparmio effettivo di una visita varia in base a schermo, immagini raggiunte e cache. Il CSS generato passa da circa 39.8 KB a 26.0 KB. Non vengono caricati framework, tracker o font remoti. La navigazione rimane disponibile anche senza JavaScript.

## Pubblicazione

Repository ufficiale: `crimi-gang/crimi-gang.github.io`. In GitHub, **Settings → Pages → Deploy from a branch → main → /(root)**. Tutti i file del sito sono nella radice del repository. I file statici generati sono inclusi nel repository e `.nojekyll` disattiva l'elaborazione Jekyll. Ogni aggiornamento pubblicato su `main` aggiorna il sito tramite GitHub Pages. Non è necessario configurare Actions personalizzate.

Per aggiornare i contenuti: modifica i sorgenti, rigenera le pagine, verifica e pubblica il commit. Il dominio è definito da `ORIGIN` in `build.py`; aggiornarlo richiede rigenerare le pagine e verificare anche il `base` della pagina 404.

## Risorse visive

- **Crimi Love:** icona e anteprime dimostrative chiara/scura dal progetto originale; i dati delle schermate sono inventati. Palette `#C7517A`, `#593052`, `#FFDBCC`, `#F4B6C9` da `LoveTheme.swift`.
- **Tiny Cozy Town:** risorse aggiornate il 20 ottobre 2026, esportate dal `TextureFactory.swift` attuale con `scripts/preview-artwork.sh`: cinque edifici, Mochi e Pip, sei decorazioni, due alberi e 25 combinazioni di colore. Le copertine usano la casetta originale; le panoramiche che mostravano il cartello pubblicitario sono state rimosse dalla presentazione. `town-expansion.png` proviene dall’anteprima SwiftUI della scheda di espansione. La presentazione include quattro attività fino al livello 30 e sei espansioni fino a 19 × 19. Palette `#AC98CE`, `#EFB5C7`, `#FFFBF3`, `#DFECDA` da `CozyTheme.swift`. Le immagini ottimizzate hanno un URL basato sul contenuto, per aggiornare le risorse anche nei browser che avevano memorizzato le precedenti.
- **Sbrokk!:** icona dal progetto Sbrokko-Game. Sei espressioni esportate senza animazioni da `SbrokkoView.swift`; due tavole illustrative dei livelli 001 e 031 composte con `NodeView`, `BoardScenery` e il catalogo originale. Non sono screenshot di una release pubblicata. Nel sito si usa il nome Sbrokk! indicato dal titolare; il progetto sorgente usa ancora Sbrokko. Palette `#F7E8CC`, `#E96A42`, `#F8B843`, `#302934` da `DesignSystem.swift`. Il gioco contiene 100 livelli, 10 capitoli, 12 espressioni, fino a tre indizi per livello tramite video con ricompensa e un Ufficio Reclami bonus. Target iOS/iPadOS 17+, italiano e inglese.
- **Font:** Nunito variable, ospitato in `fonts-nunito-latin.woff2`; licenza SIL Open Font License inclusa in `fonts-OFL.txt`. La scelta arrotondata riprende i font di sistema delle app.
- Icone e favicon: SVG presenti nei sorgenti del sito.

Questo repository contiene solo il sito e le risorse necessarie alla presentazione, senza sorgenti delle app, dati personali degli utenti o configurazioni Firebase.
