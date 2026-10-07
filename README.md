# Deck List Column Headers

A tiny Anki add-on: your own names for the deck list columns on the main screen. For example `Learn.` / `Due`, or `Изуч.` / `Повтор` instead of the long Russian `Изучаемые` / `К повторению`.

- Settings (Tools → Add-ons → Config): Deck / New / Learn / Due. Empty = Anki's own text (shown in grey in the field). Changes apply immediately.
- It only changes the header text and finds the columns by Anki's own classes, not by position. Columns from other add-ons are skipped, so it works with [Deck Size Column](https://github.com/yndarra/anki-deck-size-column), [Wrap Long Deck Names](https://github.com/yndarra/anki-wrap-deck-names) and others.

Build: `build.bat` → `dist/deck_list_headers.ankiaddon`. Requires Anki 23.10+. Tested with 26.09.

---

# Заголовки списка колод (RU)

Свои названия столбцов в списке колод, например «Изуч.» и «Повтор» вместо «Изучаемые» и «К повторению». Настройки: Инструменты → Дополнения → Config. Пусто — текст самой Anki. Меняется только текст заголовков, поэтому дополнение не конфликтует с другими.

## License
MIT
