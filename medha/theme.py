"""Built-in color tokens live here; both themes render the same workbench.qss."""
from pathlib import Path
from string import Template

DARK = dict(bg='#1f1f1f', panel='#181818', field='#313131', fg='#cccccc', muted='#9d9d9d',
            border='#2b2b2b', accent='#0078d4', selection='#264f78', line='#282828',
            keyword='#c586c0', string='#ce9178', comment='#6a9955', number='#b5cea8',
            type='#4ec9b0', function='#dcdcaa', execution='#514400')
LIGHT = dict(bg='#ffffff', panel='#f3f3f3', field='#ffffff', fg='#202020', muted='#606060',
             border='#dddddd', accent='#005fb8', selection='#cce8ff', line='#f1f1f1',
             keyword='#af00db', string='#a31515', comment='#008000', number='#098658',
             type='#267f99', function='#795e26', execution='#fff3b0')


def tokens(name='dark'):
    return dict(LIGHT if name == 'light' else DARK)


def stylesheet(name='dark'):
    return Template(Path(__file__).with_name('workbench.qss').read_text()).substitute(tokens(name))


DARK_QSS = stylesheet('dark')  # Existing imports continue to resolve.


def apply_editor(editor, name):
    from PySide6.QtGui import QFont, QFontDatabase
    colors = tokens(name)
    available = set(QFontDatabase.families())
    family = next((f for f in ['JetBrains Mono', 'Cascadia Code', 'DejaVu Sans Mono'] if f in available), 'monospace')
    editor.setFont(QFont(family, 11))
    editor.theme_tokens = colors
    editor.setStyleSheet('')
    editor.highlighter.set_theme_formats({key: {'foreground': colors[key]}
                                         for key in ['keyword', 'string', 'comment', 'number', 'type', 'function']})
    editor.highlight_current_line()
    editor.viewport().update()
    # Painters (gutter/minimap) and syntax formats use the same theme as Qt widgets.
