# Deck List Column Headers

**Install:** in Anki go to Tools → Add-ons → Get Add-ons… and enter the code **`834513701`** ([AnkiWeb page](https://ankiweb.net/shared/info/834513701)).
**Установка:** Инструменты → Дополнения → Скачать дополнения… → код **`834513701`**.

A small Anki add-on: your own names and widths for the deck list columns on the main screen. For example `Learn.` / `Due`, or `Изуч.` / `Повтор` instead of the long Russian `Изучаемые` / `К повторению`.

- Settings (Tools → Add-ons → Config): Deck / New / Learn / Due headers, plus the minimum width and side padding of the New / Learn / Due columns, to make them narrower or wider. Empty = Anki's own value (shown in grey in the field). Changes apply immediately.
- It only changes the header text and finds the columns by Anki's own classes, not by position. Columns from other add-ons are skipped, so it works with [Deck Size Column](https://github.com/yndarra/anki-deck-size-column), [Wrap Long Deck Names](https://github.com/yndarra/anki-wrap-deck-names) and others.

Build: `build.bat` → `dist/deck_list_headers.ankiaddon`. Requires Anki 23.10+. Tested with 26.09.

---

# Заголовки списка колод (RU)

Свои названия столбцов в списке колод, например «Изуч.» и «Повт.» вместо «Изучаемые» и «К повторению», и ширина (мин. ширина и поля) столбцов Новые / Изучаемые / К повторению. Настройки: Инструменты → Дополнения → Config. Пусто — как в самой Anki. Меняются только заголовки и ширина столбцов Anki, поэтому дополнение не конфликтует с другими.

## License
MIT
