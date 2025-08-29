# TO-DO

## GUI Screen

- [x] Eno okno/screen, kjer se vse nastavlja. Vse izbire so kot **pull-down**, razen ure in ene kljukice.

### Series
- [x] Izbira serije 00–99.
- [x] Ob vsakem vnosu naj se pozicija nastavi na prejšnjo vrednost (manj premikanja in napak).

### Group
- [x] Izbira skupine A–D.
- [x] Ob vsakem vnosu naj se pozicija nastavi na prejšnjo vrednost.

### Open Time
- [x] Izbira ure, kdaj so vrata za štart odprta.
- [x] Ob vnosu se **Close** avtomatsko poveča za 15 minut.

### Close Time
- [x] Izbira ure, kdaj se vrata za štart zaprejo.
- [ ] Preverjanje: če je ura manjša od Open → pokaže opozorilo:
      `"Closing time must be later than opening time!"`.

### A = Right
- [x] Možnost označitve kljukice pri "A=Right".

### Period
- [x] Izbira perioda pošiljanja: 3, 5, 10, 20, 30 sekund.
- [x] Default vrednost: 5 sekund.

### COM Port
- [x] Izbira COM porta izmed vseh na voljo.
- [ ] Naknadno se določi baud rate.
- [ ] Prikaz samo dostopnih portov.

### Buttons

#### Connect / Disconnect
- [x] Gumb **Connect** vzpostavi povezavo.
- [x] Ko je povezava vzpostavljena:
  - Zelena LED "Connected".
  - Gumb se spremeni v **Disconnect**.
  - Ob prekinitvi pošlje prazen niz `"#______"` (6 presledkov).
  
#### Display / Finish
- [ ] Gumb **Display** začne pošiljanje in zaklene vse izbire.
- [ ] Ko pošiljanje aktivno, gumb se spremeni v **Finish**.
- [ ] Ob pritisku **Finish**:
- Pošlje prazen niz `"#______"` (6 presledkov).
- Gumb se vrne na **Display**.
- [ ] Gumb se aktivira takoj in ne po preteku periode.
- [ ] Če je potrebno čakanje, polling naj bo vsaj vsako sekundo.

---

## COM Port Communication (ASCII Format)

- [ ] Nizi se pošiljajo periodično na vsakih **Period** sekund.
- [x] Vsak niz se začne z `#`.

### Format

- [ ] Serija in skupina: `#ss__g_`  
      - `ss` → serija (00–99)  
      - `g` → skupina (A–D)
- [ ] Odpiranje: `#O_hh_mm`
- [ ] Zapiranje: `#C_hh_mm`
- [ ] Smer letenja:
  - Če "A=Right" je označeno:
    - Skupini A ali C → `#RIGHT_`
    - Skupini B ali D → `#LEFT__`
  - Če "A=Right" ni označeno:
    - Skupini A ali C → `#LEFT__`
    - Skupini B ali D → `#RIGHT_`

- [ ] BAUD_RATE hardcode 6900
