"""Deck List Column Headers — свои названия и ширина столбцов в списке колод.

  • Свои названия: например «Изуч.» вместо «Изучаемые» и «Повт.» вместо
    «К повторению». Пустое поле — текст самой Anki.
  • Ширина числовых столбцов Новые / Изучаемые / К повторению: минимальная
    ширина и поля по бокам. Пустое поле — как в Anki (4em и 12px).

Как устроено: перед отрисовкой списка (хук deck_browser_will_render_content)
в блок под таблицей добавляются стиль и маленький скрипт. Ячейки ищутся по
разметке самой Anki, а не по общему номеру столбца:
  • «Колода» — первый <th> строки заголовков;
  • Новые / Изучаемые / К повторению — <th> ровно с классом "count"
    (столбцы других дополнений помечены своими классами и пропускаются,
    например th.dsc-size из Deck Size Column) и ячейки 2–4 в строках колод
    (первая — название, свои столбцы дополнения добавляют после них).
Поэтому дополнение не конфликтует с другими правками списка колод.
"""

from __future__ import annotations

import json
import re

import anki.lang
from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from aqt.qt import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QWidget

ADDON = __name__.split(".")[0]
NAME_KEYS = ("deck", "new", "learn", "due")
SIZE_KEYS = ("count_width", "count_padding")
DEFAULTS = {key: "" for key in NAME_KEYS + SIZE_KEYS}

# Только «число + единица CSS», чтобы в стиль не попало ничего лишнего.
_LENGTH_RE = re.compile(r"^\d+(\.\d+)?(px|em|rem|ch)$")

_TEXTS = {
    "ru": {
        "deck": "Колода",
        "new": "Новые",
        "learn": "Изучаемые",
        "due": "К повторению",
        "count_width": "Мин. ширина столбцов чисел",
        "count_padding": "Поля по бокам ячеек",
        "dlg_title": "Столбцы списка колод",
        "hint": "Пустое поле — как в самой Anki (показано серым).",
        "size_hint": "Ширина и поля — для столбцов Новые / Изучаемые / К повторению. "
        "Например 3em, 40px; поля — 6px.",
        "defaults": "По умолчанию",
    },
    "en": {
        "deck": "Deck",
        "new": "New",
        "learn": "Learn",
        "due": "Due",
        "count_width": "Min width of count columns",
        "count_padding": "Cell side padding",
        "dlg_title": "Deck list columns",
        "hint": "Empty field — Anki's own value (shown in grey).",
        "size_hint": "Width and padding apply to the New / Learn / Due columns. "
        "E.g. 3em, 40px; padding 6px.",
        "defaults": "Defaults",
    },
}

# Значения Anki по умолчанию — подсказки в пустых полях.
_ANKI_SIZE = {"count_width": "4em", "count_padding": "12px"}

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
    cfg = {key: str(stored.get(key, "") or "").strip() for key in DEFAULTS}
    for key in SIZE_KEYS:
        if cfg[key] and not _LENGTH_RE.match(cfg[key]):
            cfg[key] = ""  # недопустимое значение — как в Anki
    return cfg


def _css(cfg: dict) -> str:
    rules = []
    if cfg["count_width"]:
        # th[class="count"] — только столбцы Anki, не столбцы других дополнений.
        rules.append(f'th[class="count"] {{ min-width: {cfg["count_width"]}; }}')
    if cfg["count_padding"]:
        pad = cfg["count_padding"]
        rules.append(
            "tr.deck > td:nth-child(2), tr.deck > td:nth-child(3), tr.deck > td:nth-child(4),"
            ' th[class="count"]'
            f" {{ padding-left: {pad}; padding-right: {pad}; }}"
        )
    return "<style>" + "".join(rules) + "</style>" if rules else ""


def on_will_render(deck_browser: DeckBrowser, content: DeckBrowserContent) -> None:
    cfg = get_config()
    names = {k: cfg[k] for k in NAME_KEYS if cfg[k]}
    extra = _css(cfg)
    if names:
        extra += f"<script>window.DLH_HEADERS = {json.dumps(names)};" + _SCRIPT + "</script>"
    content.stats += extra


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_t("dlg_title"))
        self.setMinimumWidth(420)
        form = QFormLayout(self)
        form.addRow(QLabel(_t("hint")))
        cfg = get_config()
        self.edits: dict[str, QLineEdit] = {}
        for key in NAME_KEYS:
            edit = QLineEdit(cfg[key])
            edit.setPlaceholderText(_t(key))
            form.addRow(_t(key), edit)
            self.edits[key] = edit
        size_hint = QLabel(_t("size_hint"))
        size_hint.setWordWrap(True)
        form.addRow(size_hint)
        for key in SIZE_KEYS:
            edit = QLineEdit(cfg[key])
            edit.setPlaceholderText(_ANKI_SIZE[key])
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
        cfg = {k: e.text().strip().replace(" ", "") if k in SIZE_KEYS else e.text().strip()
               for k, e in self.edits.items()}
        for key in SIZE_KEYS:
            if cfg[key] and not _LENGTH_RE.match(cfg[key]):
                cfg[key] = ""
        mw.addonManager.writeConfig(ADDON, cfg)
        if mw.state == "deckBrowser":
            mw.deckBrowser.refresh()
        self.accept()


def open_settings() -> None:
    SettingsDialog(mw).exec()


gui_hooks.deck_browser_will_render_content.append(on_will_render)
mw.addonManager.setConfigAction(ADDON, open_settings)
