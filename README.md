# Glum Chatbot

Glum je chatbot založený na OpenAI, který komunikuje s uživateli přes rozhraní Facebook Messenger. Chatbot je navržen tak, aby poskytoval uživatelům možnost interagovat s postavami v příběhu pomocí textových zpráv.

## Funkce

- Komunikace s uživateli přes Facebook Messenger.
- Generování textových odpovědí na základě uživatelského vstupu.
- Ukládání konverzací pro budoucí reference.
- Interakce s OpenAI pro generování odpovědí.
- Možnost ořezání dlouhých konverzací, pokud překročí limit tokenů stanovený OpenAI.

## Instalace

1. **Nainstalujte závislosti projektu**:
    ```bash
    make install
    ```

2. **Získání cookies pro přihlášení na Facebook**:
   - Použijte rozšíření prohlížeče, jako je [ExportThisCookie](https://chrome.google.com/webstore/detail/exportthiscookie/dannllckdimllhkiplchkcaoheibealk), k exportu cookies z vašeho prohlížeče.
   - Uložte soubor cookies jako `session.json` ve stejném adresáři, kde je umístěn váš skript.

3. **Spustit Aplikaci**:
    ```bash
    make start
    ```

## Řešení problémů

1. **Problémy s přihlášením**:
    - Ujistěte se, že máte správné cookies a že vaše přihlašovací údaje jsou správné.
    - Zkontrolujte, zda nebyly cookies změněny nebo zda nevypršely. Pokud je to nutné, znovu exportujte a uložte cookies.

2. **Problémy s odesíláním zpráv**:
    - Zkontrolujte, zda je ID vlákna správné a zda máte oprávnění odesílat zprávy do tohoto vlákna.

## Budoucí rozvoj

- **Zabezpečení účtu**: Načítání hesla z konzole při startu aplikace, šifrování souboru cookies, aby bylo možné zamezit přístupu k účtu.
- **Zpracování multimediálního obsahu**: Možnost zpracování multimediálního obsahu, jako jsou obrázky, videa a zvuky, aby byla konverzace více interaktivní a zajímavá.
- **Rozpoznávání příkazů**: Rozpoznávání specifických příkazů a dotazů, aby bylo možné s Glumem interagovat na pokročilejší úrovni.

Pro více informací o možnostech a nastavení knihovny `fbchat`, navštivte [dokumentaci knihovny fbchat](https://fbchat.readthedocs.io/).