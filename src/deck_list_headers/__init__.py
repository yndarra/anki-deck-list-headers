"""Deck List Column Headers — свои названия столбцов в списке колод.

Например «Изуч.» вместо «Изучаемые» и «Повтор» вместо «К повторению».
Пустое поле — оставить текст самой Anki.

Как устроено: перед отрисовкой списка (хук deck_browser_will_render_content)
в блок под таблицей добавляется маленький скрипт, который меняет только
текст заголовков. Ячейки ищутся по классам Anki, а не по номеру столбца:
  • «Колода» — первый <th> строки заголовков;
  • Новые / Изучаемые / К повторению — первые три <th class="count">,
    которые добавила сама Anki (столбцы других дополнений помечены своими
    классами и пропускаются, например th.dsc-size из Deck Size Column).
Поэтому дополнение не конфликтует с другими правками списка колод.
"""

from __future__ import annotations

import json

import anki.lang
from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from aqt.qt import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QWidget

ADDON = __name__.split(".")[0]
KEYS = ("deck", "new", "learn", "due")
DEFAULTS = {key: "" for key in KEYS}

_TEXTS = {
    "ru": {
        "deck": "Колода",
        "new": "Новые",
        "learn": "Изучаемые",
        "due": "К повторению",
        "dlg_title": "Заголовки списка колод",
        "hint": "Пустое поле — текст самой Anki (он показан серым).",
        "defaults": "По умолчанию",
    },
    "en": {
        "deck": "Deck",
        "new": "New",
        "learn": "Learn",
        "due": "Due",
        "dlg_title": "Deck list column headers",
        "hint": "Empty field — Anki's own text (shown in grey).",
        "defaults": "Defaults",
    },
}

# Скрипт для страницы. Только переименование, никакой перестройки таблицы.
_SCRIPT = """
(function () {
    "use strict";
    const names = window.DLH_HEADERS || {};
    const first = document.querySelector("table th");
    const row = first ? first.parentElement : null;
    if (!row) return;
    // Столбцы самой Anki: у них ровно класс "count" без дополнительных классов.
    const counts = [...row.querySelectorAll("th.count")].filter(
        (th) => th.classList.length === 1
    );
    const cells = { deck: row.querySelector("th"), new: counts[0], learn: counts[1], due: counts[2] };
    for (const key of Object.keys(cells)) {
        if (names[key] && cells[key]) cells[key].textContent = names[key];
    }
})();
"""


def _t(text_id: str) -> str:
    lang = "ru" if (anki.lang.current_lang or "").lower().startswith("ru") else "en"
    return _TEXTS[lang][text_id]


def get_config() -> dict:
    stored = mw.addonManager.getConfig(ADDON) or {}
    return {key: str(stored.get(key, "") or "") for key in KEYS}


def on_will_render(deck_browser: DeckBrowser, content: DeckBrowserContent) -> None:
    names = {k: v for k, v in get_config().items() if v.strip()}
    if not names:
        return
    content.stats += (
        f"<script>window.DLH_HEADERS = {json.dumps(names)};" + _SCRIPT + "</script>"
    )


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_t("dlg_title"))
        self.setMinimumWidth(380)
        form = QFormLayout(self)
        form.addRow(QLabel(_t("hint")))
        cfg = get_config()
        self.edits: dict[str, QLineEdit] = {}
        for key in KEYS:
            edit = QLineEdit(cfg[key])
            edit.setPlaceholderText(_t(key))
            form.addRow(_t(key), edit)
            self.edits[key] = edit
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        reset = buttons.addButton(_t("defaults"), QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(lambda: [e.clear() for e in self.edits.values()])
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _save(self) -> None:
        mw.addonManager.writeConfig(ADDON, {k: e.text().strip() for k, e in self.edits.items()})
        if mw.state == "deckBrowser":
            mw.deckBrowser.refresh()
        self.accept()


def open_settings() -> None:
    SettingsDialog(mw).exec()


gui_hooks.deck_browser_will_render_content.append(on_will_render)
mw.addonManager.setConfigAction(ADDON, open_settings)
