"""
MEDHA Extensions — Extensions Panel UI

Dock widget providing VS Code-like extensions marketplace experience.
Features: search, install/uninstall, theme application, snippet browsing.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Optional, Dict, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QListWidget, QListWidgetItem,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QSplitter,
    QTextBrowser, QMessageBox, QMenu, QStyle
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor, QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from medha.extensions.models import (
    ExtensionInfo,
    ExtensionDetail,
    ExtensionClassification,
    InstalledExtension,
)
from medha.extensions.ui.worker import (
    SearchWorker,
    DetailWorker,
    DownloadWorker,
    InstallWorker,
    UninstallWorker,
    ListInstalledWorker,
    ToggleEnabledWorker,
    LoadThemesWorker,
    LoadSnippetsWorker,
    ApplyThemeWorker,
)

logger = logging.getLogger(__name__)

# Classification badge colors
CLASSIFICATION_COLORS = {
    ExtensionClassification.SUPPORTED: "#3fb950",   # Green
    ExtensionClassification.PARTIAL: "#d29922",     # Yellow/Orange
    ExtensionClassification.UNSUPPORTED: "#f85149", # Red
}

CLASSIFICATION_TOOLTIPS = {
    ExtensionClassification.SUPPORTED: "Fully supported — themes, snippets, and/or grammars",
    ExtensionClassification.PARTIAL: "Partially supported — has declarative contributions but also JS code (JS not executed)",
    ExtensionClassification.UNSUPPORTED: "Unsupported — JavaScript-only extension (needs VS Code runtime)",
}


class ExtensionListItem(QListWidgetItem):
    """Custom list item for extension search results."""

    def __init__(self, ext: ExtensionInfo, is_installed: bool = False):
        super().__init__()
        self.ext = ext
        self.is_installed = is_installed
        self.setData(Qt.UserRole, ext)
        self.update_display()

    def update_display(self):
        """Update the item's display text."""
        status = " [Installed]" if self.is_installed else ""
        classification = self.ext.files.download is not None  # placeholder
        # Classification will be set from detail
        self.setText(
            f"{self.ext.display_name}{status}\n"
            f"  {self.ext.namespace}.{self.ext.name} v{self.ext.version} • {self.ext.download_count:,} downloads"
        )

    def set_classification(self, classification: ExtensionClassification):
        """Set classification badge."""
        self.classification = classification
        color = CLASSIFICATION_COLORS.get(classification, "#8b949e")
        tooltip = CLASSIFICATION_TOOLTIPS.get(classification, "")
        # We'll render the badge in the delegate


class ExtensionDetailWidget(QWidget):
    """Widget showing detailed extension information."""

    install_requested = Signal(object)  # ExtensionDetail
    uninstall_requested = Signal(object)  # InstalledExtension
    enable_requested = Signal(object, bool)  # InstalledExtension, enabled
    apply_theme_requested = Signal(object)  # (installed, theme_label)

    def __init__(self):
        super().__init__()
        self.current_detail: Optional[ExtensionDetail] = None
        self.current_installed: Optional[InstalledExtension] = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        self.header_layout = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet("border-radius: 4px; background: #161b22;")
        self.header_layout.addWidget(self.icon_label)

        info_layout = QVBoxLayout()
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #c9d1d9;")
        info_layout.addWidget(self.name_label)

        self.publisher_label = QLabel()
        self.publisher_label.setStyleSheet("font-size: 12px; color: #8b949e;")
        info_layout.addWidget(self.publisher_label)

        self.header_layout.addLayout(info_layout, 1)

        self.classification_label = QLabel()
        self.classification_label.setFixedHeight(24)
        self.classification_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.header_layout.addWidget(self.classification_label)

        layout.addLayout(self.header_layout)

        # Stats
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 11px; color: #6e7681;")
        layout.addWidget(self.stats_label)

        # Description
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #c9d1d9; margin-top: 8px;")
        layout.addWidget(self.desc_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #30363d;")
        layout.addWidget(sep)

        # Actions
        self.action_layout = QHBoxLayout()
        self.install_btn = QPushButton("Install")
        self.install_btn.setFixedHeight(32)
        self.install_btn.clicked.connect(self._on_install)
        self.action_layout.addWidget(self.install_btn)

        self.uninstall_btn = QPushButton("Uninstall")
        self.uninstall_btn.setFixedHeight(32)
        self.uninstall_btn.clicked.connect(self._on_uninstall)
        self.uninstall_btn.setVisible(False)
        self.action_layout.addWidget(self.uninstall_btn)

        self.enable_btn = QPushButton("Disable")
        self.enable_btn.setFixedHeight(32)
        self.enable_btn.clicked.connect(self._on_toggle_enable)
        self.enable_btn.setVisible(False)
        self.action_layout.addWidget(self.enable_btn)

        self.action_layout.addStretch()
        layout.addLayout(self.action_layout)

        # Themes section (for theme extensions)
        self.themes_label = QLabel("Themes:")
        self.themes_label.setStyleSheet("font-weight: bold; color: #c9d1d9; margin-top: 12px;")
        self.themes_label.setVisible(False)
        layout.addWidget(self.themes_label)

        self.themes_list = QListWidget()
        self.themes_list.setMaximumHeight(100)
        self.themes_list.setVisible(False)
        self.themes_list.itemClicked.connect(self._on_theme_clicked)
        layout.addWidget(self.themes_list)

        # Snippets section
        self.snippets_label = QLabel("Snippets:")
        self.snippets_label.setStyleSheet("font-weight: bold; color: #c9d1d9; margin-top: 12px;")
        self.snippets_label.setVisible(False)
        layout.addWidget(self.snippets_label)

        self.snippets_list = QListWidget()
        self.snippets_list.setMaximumHeight(100)
        self.snippets_list.setVisible(False)
        layout.addWidget(self.snippets_list)

        # README
        self.readme_label = QLabel("README:")
        self.readme_label.setStyleSheet("font-weight: bold; color: #c9d1d9; margin-top: 12px;")
        layout.addWidget(self.readme_label)

        self.readme_browser = QTextBrowser()
        self.readme_browser.setOpenExternalLinks(True)
        self.readme_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.readme_browser, 1)

        # Links
        self.links_layout = QHBoxLayout()
        self.repo_btn = QPushButton("Repository")
        self.repo_btn.clicked.connect(self._open_repository)
        self.links_layout.addWidget(self.repo_btn)

        self.license_btn = QPushButton("License")
        self.license_btn.clicked.connect(self._open_license)
        self.links_layout.addWidget(self.license_btn)

        self.links_layout.addStretch()
        layout.addLayout(self.links_layout)

    def show_detail(self, detail: ExtensionDetail, installed: InstalledExtension = None):
        """Show extension detail."""
        self.current_detail = detail
        self.current_installed = installed

        self.name_label.setText(detail.display_name)
        self.publisher_label.setText(f"{detail.namespace} • v{detail.version}")
        self.stats_label.setText(f"{detail.download_count:,} downloads • {detail.license} license")
        self.desc_label.setText(detail.description)

        # Classification badge
        classification = detail.classify() if hasattr(detail, 'classify') else ExtensionClassification.SUPPORTED
        if installed:
            classification = installed.classification

        color = CLASSIFICATION_COLORS.get(classification, "#8b949e")
        tooltip = CLASSIFICATION_TOOLTIPS.get(classification, "")
        self.classification_label.setText(f"  {classification.value.upper()}  ")
        self.classification_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        self.classification_label.setToolTip(tooltip)

        # Actions
        if installed:
            self.install_btn.setVisible(False)
            self.uninstall_btn.setVisible(True)
            self.enable_btn.setVisible(True)
            self.enable_btn.setText("Disable" if installed.enabled else "Enable")
        else:
            self.install_btn.setVisible(True)
            self.uninstall_btn.setVisible(False)
            self.enable_btn.setVisible(False)

        # Themes
        if detail.manifest and detail.manifest.themes:
            self.themes_label.setVisible(True)
            self.themes_list.setVisible(True)
            self.themes_list.clear()
            for theme in detail.manifest.themes:
                item = QListWidgetItem(f"🎨 {theme.label}")
                item.setData(Qt.UserRole, theme)
                self.themes_list.addItem(item)
        else:
            self.themes_label.setVisible(False)
            self.themes_list.setVisible(False)

        # Snippets
        if detail.manifest and detail.manifest.snippets:
            self.snippets_label.setVisible(True)
            self.snippets_list.setVisible(True)
            self.snippets_list.clear()
            for snippet in detail.manifest.snippets:
                item = QListWidgetItem(f"📝 {snippet.language}: {snippet.path}")
                item.setData(Qt.UserRole, snippet)
                self.snippets_list.addItem(item)
        else:
            self.snippets_label.setVisible(False)
            self.snippets_list.setVisible(False)

        # README
        if detail.readme_content:
            self.readme_browser.setMarkdown(detail.readme_content)
        else:
            self.readme_browser.setPlainText("No README available.")

        # Links
        self.repo_btn.setVisible(bool(detail.repository))
        self.license_btn.setVisible(bool(detail.license))

    def show_installed(self, installed: InstalledExtension):
        """Show installed extension detail."""
        self.current_installed = installed

        # Create a pseudo-detail from installed
        self.name_label.setText(installed.manifest.display_name)
        self.publisher_label.setText(f"{installed.namespace} • v{installed.version}")
        self.stats_label.setText(f"Installed • {installed.classification.value.title()}")
        self.desc_label.setText(installed.manifest.description)

        color = CLASSIFICATION_COLORS.get(installed.classification, "#8b949e")
        tooltip = CLASSIFICATION_TOOLTIPS.get(installed.classification, "")
        self.classification_label.setText(f"  {installed.classification.value.upper()}  ")
        self.classification_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        self.classification_label.setToolTip(tooltip)

        self.install_btn.setVisible(False)
        self.uninstall_btn.setVisible(True)
        self.enable_btn.setVisible(True)
        self.enable_btn.setText("Disable" if installed.enabled else "Enable")

        # Themes
        if installed.manifest.themes:
            self.themes_label.setVisible(True)
            self.themes_list.setVisible(True)
            self.themes_list.clear()
            for theme in installed.manifest.themes:
                item = QListWidgetItem(f"🎨 {theme.label}")
                item.setData(Qt.UserRole, theme)
                self.themes_list.addItem(item)
        else:
            self.themes_label.setVisible(False)
            self.themes_list.setVisible(False)

        # Snippets
        if installed.manifest.snippets:
            self.snippets_label.setVisible(True)
            self.snippets_list.setVisible(True)
            self.snippets_list.clear()
            for snippet in installed.manifest.snippets:
                item = QListWidgetItem(f"📝 {snippet.language}: {snippet.path}")
                item.setData(Qt.UserRole, snippet)
                self.snippets_list.addItem(item)
        else:
            self.snippets_label.setVisible(False)
            self.snippets_list.setVisible(False)

        self.readme_browser.setPlainText("Installed extension. No README cached.")
        self.repo_btn.setVisible(bool(installed.manifest.repository))
        self.license_btn.setVisible(bool(installed.manifest.license))

    def clear(self):
        """Clear the detail view."""
        self.current_detail = None
        self.current_installed = None
        self.name_label.setText("Select an extension")
        self.publisher_label.clear()
        self.stats_label.clear()
        self.desc_label.clear()
        self.classification_label.clear()
        self.install_btn.setVisible(False)
        self.uninstall_btn.setVisible(False)
        self.enable_btn.setVisible(False)
        self.themes_label.setVisible(False)
        self.themes_list.setVisible(False)
        self.themes_list.clear()
        self.snippets_label.setVisible(False)
        self.snippets_list.setVisible(False)
        self.snippets_list.clear()
        self.readme_browser.clear()
        self.repo_btn.setVisible(False)
        self.license_btn.setVisible(False)

    def _on_install(self):
        if self.current_detail:
            self.install_requested.emit(self.current_detail)

    def _on_uninstall(self):
        if self.current_installed:
            self.uninstall_requested.emit(self.current_installed)

    def _on_toggle_enable(self):
        if self.current_installed:
            self.enable_requested.emit(self.current_installed, not self.current_installed.enabled)

    def _on_theme_clicked(self, item):
        if self.current_installed:
            theme = item.data(Qt.UserRole)
            self.apply_theme_requested.emit((self.current_installed, theme.label))

    def _open_repository(self):
        if self.current_detail and self.current_detail.repository:
            QDesktopServices.openUrl(self.current_detail.repository)

    def _open_license(self):
        if self.current_detail and self.current_detail.license:
            QMessageBox.information(self, "License", self.current_detail.license)


class ExtensionsPanel(QWidget):
    """
    Main Extensions Panel widget.

    Provides:
    - Search box for Open VSX registry
    - Results list with classification badges
    - Detail view with install/uninstall/enable actions
    - Installed tab with management
    - Theme application
    - Offline indicator
    """

    theme_apply_requested = Signal(object)  # VSCodeTheme
    snippet_loaded = Signal(str, dict)  # language, snippets dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ExtensionsPanel")
        self._setup_ui()
        self._setup_workers()
        self._load_installed()

        # Offline state
        self._offline = False

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(48)
        toolbar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search extensions in Open VSX Registry...")
        self.search_box.setFixedHeight(32)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 0 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #58a6ff;
            }
        """)
        self.search_box.returnPressed.connect(self._on_search)
        toolbar_layout.addWidget(self.search_box, 1)

        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setFixedHeight(32)
        self.search_btn.clicked.connect(self._on_search)
        toolbar_layout.addWidget(self.search_btn)

        # Offline indicator
        self.offline_label = QLabel("⚠ Offline")
        self.offline_label.setStyleSheet("color: #d29922; font-size: 12px; font-weight: bold;")
        self.offline_label.setVisible(False)
        toolbar_layout.addWidget(self.offline_label)

        layout.addWidget(toolbar)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #30363d; }")

        # Left: Results list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0d1117;
            }
            QTabBar::tab {
                background-color: #161b22;
                color: #8b949e;
                padding: 8px 16px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #0d1117;
                color: #58a6ff;
                border-bottom: 2px solid #58a6ff;
            }
        """)

        # Marketplace tab
        self.marketplace_widget = QWidget()
        marketplace_layout = QVBoxLayout(self.marketplace_widget)
        marketplace_layout.setContentsMargins(0, 0, 0, 0)

        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #21262d;
            }
            QListWidget::item:hover {
                background-color: #161b22;
            }
            QListWidget::item:selected {
                background-color: #1f6feb;
                color: white;
            }
        """)
        self.results_list.setSpacing(2)
        self.results_list.currentItemChanged.connect(self._on_result_selected)
        marketplace_layout.addWidget(self.results_list)

        # Loading indicator
        self.loading_label = QLabel("Enter a search query...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: #6e7681; padding: 24px;")
        marketplace_layout.addWidget(self.loading_label)

        self.tabs.addTab(self.marketplace_widget, "Marketplace")

        # Installed tab
        self.installed_widget = QWidget()
        installed_layout = QVBoxLayout(self.installed_widget)
        installed_layout.setContentsMargins(0, 0, 0, 0)

        self.installed_list = QListWidget()
        self.installed_list.setStyleSheet("""
            QListWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #21262d;
            }
            QListWidget::item:hover {
                background-color: #161b22;
            }
            QListWidget::item:selected {
                background-color: #1f6feb;
                color: white;
            }
        """)
        self.installed_list.currentItemChanged.connect(self._on_installed_selected)
        installed_layout.addWidget(self.installed_list)

        self.installed_empty = QLabel("No extensions installed")
        self.installed_empty.setAlignment(Qt.AlignCenter)
        self.installed_empty.setStyleSheet("color: #6e7681; padding: 24px;")
        installed_layout.addWidget(self.installed_empty)

        self.tabs.addTab(self.installed_widget, "Installed")

        left_layout.addWidget(self.tabs)
        splitter.addWidget(left_widget)

        # Right: Detail view
        self.detail_widget = ExtensionDetailWidget()
        self.detail_widget.install_requested.connect(self._on_install_requested)
        self.detail_widget.uninstall_requested.connect(self._on_uninstall_requested)
        self.detail_widget.enable_requested.connect(self._on_enable_requested)
        self.detail_widget.apply_theme_requested.connect(self._on_apply_theme_requested)
        splitter.addWidget(self.detail_widget)

        # Set splitter sizes (70% left, 30% right)
        splitter.setSizes([700, 300])
        layout.addWidget(splitter, 1)

    def _setup_workers(self):
        self.search_worker: Optional[SearchWorker] = None
        self.detail_worker: Optional[DetailWorker] = None
        self.download_worker: Optional[DownloadWorker] = None
        self.install_worker: Optional[InstallWorker] = None
        self.uninstall_worker: Optional[UninstallWorker] = None
        self.list_installed_worker: Optional[ListInstalledWorker] = None
        self.toggle_enabled_worker: Optional[ToggleEnabledWorker] = None
        self.apply_theme_worker: Optional[ApplyThemeWorker] = None

    def _on_search(self):
        query = self.search_box.text().strip()
        if not query:
            return

        self.results_list.clear()
        self.loading_label.setText("Searching...")
        self.loading_label.setVisible(True)
        self.search_btn.setEnabled(False)
        self.search_box.setEnabled(False)

        self.search_worker = SearchWorker(query)
        self.search_worker.results_ready.connect(self._on_search_results)
        self.search_worker.error.connect(self._on_worker_error)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.start()

    def _on_search_results(self, result):
        self.loading_label.setVisible(False)
        if not result.extensions:
            self.loading_label.setText("No extensions found")
            self.loading_label.setVisible(True)
            return

        self.results_list.clear()
        for ext in result.extensions:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, ext)

            # Create custom widget for the item
            widget = QWidget()
            widget_layout = QHBoxLayout(widget)
            widget_layout.setContentsMargins(8, 8, 8, 8)
            widget_layout.setSpacing(12)

            # Icon placeholder
            icon_label = QLabel("📦")
            icon_label.setFixedSize(32, 32)
            widget_layout.addWidget(icon_label)

            # Info
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)

            name_label = QLabel(f"{ext.display_name} ")
            name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #c9d1d9;")
            info_layout.addWidget(name_label)

            meta_label = QLabel(f"{ext.namespace}.{ext.name} v{ext.version}  •  {ext.download_count:,} downloads")
            meta_label.setStyleSheet("font-size: 11px; color: #6e7681;")
            info_layout.addWidget(meta_label)

            desc_label = QLabel(ext.description[:100] + "..." if len(ext.description) > 100 else ext.description)
            desc_label.setStyleSheet("font-size: 11px; color: #8b949e;")
            info_layout.addWidget(desc_label)

            widget_layout.addLayout(info_layout, 1)

            # Classification badge
            badge = QLabel("?")
            badge.setFixedWidth(80)
            badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            badge.setStyleSheet("font-size: 10px; font-weight: bold;")
            widget_layout.addWidget(badge)

            item.setSizeHint(widget.sizeHint())
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, widget)

        # Fetch details for classification (in background)
        self._fetch_classifications(result.extensions)

    def _fetch_classifications(self, extensions: List[ExtensionInfo]):
        """Fetch details for first few extensions to get classification."""
        # For now, just use a simple heuristic
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            widget = self.results_list.itemWidget(item)
            ext = item.data(Qt.UserRole)
            if widget:
                badge = widget.findChild(QLabel, "")
                # Simple heuristic: if it has themes/snippets it's SUPPORTED
                # We'll fetch detail on selection instead

    def _on_search_finished(self):
        self.search_btn.setEnabled(True)
        self.search_box.setEnabled(True)
        if self.search_worker:
            self.search_worker.deleteLater()
            self.search_worker = None

    def _on_result_selected(self, current, previous):
        if not current:
            self.detail_widget.clear()
            return

        ext = current.data(Qt.UserRole)
        if not ext:
            return

        # Fetch full detail
        self.detail_widget.clear()
        self.detail_widget.name_label.setText("Loading...")
        self.detail_widget.publisher_label.setText(f"{ext.namespace}.{ext.name}")

        self.detail_worker = DetailWorker(ext.namespace, ext.name)
        self.detail_worker.detail_ready.connect(self._on_detail_ready)
        self.detail_worker.error.connect(self._on_worker_error)
        self.detail_worker.finished.connect(lambda: self.detail_worker.deleteLater() if self.detail_worker else None)
        self.detail_worker.start()

    def _on_detail_ready(self, detail: ExtensionDetail):
        self.detail_widget.show_detail(detail)

    def _on_installed_selected(self, current, previous):
        if not current:
            self.detail_widget.clear()
            return

        installed = current.data(Qt.UserRole)
        if not installed:
            return

        self.detail_widget.show_installed(installed)

    def _on_install_requested(self, detail: ExtensionDetail):
        """Handle install button click."""
        if not detail.files.download:
            QMessageBox.warning(self, "Install Error", "No download URL available")
            return

        # Show downloading state
        self.detail_widget.install_btn.setText("Downloading...")
        self.detail_widget.install_btn.setEnabled(False)

        self.download_worker = DownloadWorker(
            download_url=detail.files.download,
            expected_sha256=detail.files.sha256,
        )
        self.download_worker.download_finished.connect(lambda path: self._on_download_finished(path, detail))
        self.download_worker.error.connect(self._on_worker_error)
        self.download_worker.finished.connect(lambda: self.download_worker.deleteLater() if self.download_worker else None)
        self.download_worker.start()

    def _on_download_finished(self, vsix_path: str, detail: ExtensionDetail):
        """Handle download completion, start install."""
        self.detail_widget.install_btn.setText("Installing...")
        self.detail_widget.install_btn.setEnabled(False)

        self.install_worker = InstallWorker(vsix_path=vsix_path, expected_sha256=detail.files.sha256)
        self.install_worker.install_finished.connect(self._on_install_finished)
        self.install_worker.error.connect(self._on_worker_error)
        self.install_worker.finished.connect(lambda: self.install_worker.deleteLater() if self.install_worker else None)
        self.install_worker.start()

    def _on_install_finished(self, installed: InstalledExtension):
        """Handle install completion."""
        QMessageBox.information(self, "Success", f"Installed {installed.manifest.display_name}")
        self.detail_widget.show_installed(installed)
        self._load_installed()
        self.tabs.setCurrentIndex(1)  # Switch to Installed tab

    def _on_uninstall_requested(self, installed: InstalledExtension):
        """Handle uninstall button click."""
        reply = QMessageBox.question(
            self, "Uninstall",
            f"Uninstall {installed.manifest.display_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.uninstall_worker = UninstallWorker(installed.namespace, installed.name, installed.version)
        self.uninstall_worker.uninstall_finished.connect(self._on_uninstall_finished)
        self.uninstall_worker.error.connect(self._on_worker_error)
        self.uninstall_worker.finished.connect(lambda: self.uninstall_worker.deleteLater() if self.uninstall_worker else None)
        self.uninstall_worker.start()

    def _on_uninstall_finished(self, success: bool):
        if success:
            QMessageBox.information(self, "Success", "Extension uninstalled")
            self.detail_widget.clear()
            self._load_installed()
        else:
            QMessageBox.warning(self, "Error", "Uninstall failed")

    def _on_enable_requested(self, installed: InstalledExtension, enabled: bool):
        """Handle enable/disable button click."""
        self.toggle_enabled_worker = ToggleEnabledWorker(
            installed.namespace, installed.name, installed.version, enabled
        )
        self.toggle_enabled_worker.toggle_finished.connect(lambda s: self._on_toggle_finished(installed, enabled, s))
        self.toggle_enabled_worker.error.connect(self._on_worker_error)
        self.toggle_enabled_worker.finished.connect(lambda: self.toggle_enabled_worker.deleteLater() if self.toggle_enabled_worker else None)
        self.toggle_enabled_worker.start()

    def _on_toggle_finished(self, installed: InstalledExtension, enabled: bool, success: bool):
        if success:
            installed.enabled = enabled
            self.detail_widget.show_installed(installed)
            self._load_installed()
        else:
            QMessageBox.warning(self, "Error", "Failed to toggle extension")

    def _on_apply_theme_requested(self, data: tuple):
        """Handle theme apply request."""
        installed, theme_label = data
        # Find the theme
        themes = load_all_themes(installed)
        for label, theme in themes:
            if label == theme_label:
                self.apply_theme_worker = ApplyThemeWorker(theme)
                self.apply_theme_worker.theme_applied.connect(self._on_theme_applied)
                self.apply_theme_worker.error.connect(self._on_worker_error)
                self.apply_theme_worker.finished.connect(lambda: self.apply_theme_worker.deleteLater() if self.apply_theme_worker else None)
                self.apply_theme_worker.start()
                QMessageBox.information(self, "Theme Applied", f"Applied theme: {theme_label}")
                break

    def _on_theme_applied(self, colors: dict):
        """Emit theme apply signal for main window to handle."""
        self.theme_apply_requested.emit(colors)

    def _on_worker_error(self, error: str):
        QMessageBox.warning(self, "Error", error)
        self.detail_widget.install_btn.setText("Install")
        self.detail_widget.install_btn.setEnabled(True)
        self.detail_widget.uninstall_btn.setEnabled(True)
        self.detail_widget.enable_btn.setEnabled(True)

    def _load_installed(self):
        """Load installed extensions list."""
        self.installed_list.clear()
        self.installed_empty.setVisible(False)

        self.list_installed_worker = ListInstalledWorker()
        self.list_installed_worker.list_ready.connect(self._on_installed_list_ready)
        self.list_installed_worker.error.connect(self._on_worker_error)
        self.list_installed_worker.finished.connect(lambda: self.list_installed_worker.deleteLater() if self.list_installed_worker else None)
        self.list_installed_worker.start()

    def _on_installed_list_ready(self, installed: List[InstalledExtension]):
        if not installed:
            self.installed_empty.setVisible(True)
            return

        for ext in installed:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, ext)

            widget = QWidget()
            widget_layout = QHBoxLayout(widget)
            widget_layout.setContentsMargins(8, 8, 8, 8)
            widget_layout.setSpacing(12)

            icon_label = QLabel("📦")
            icon_label.setFixedSize(32, 32)
            widget_layout.addWidget(icon_label)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)

            name_label = QLabel(f"{ext.manifest.display_name} ")
            name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #c9d1d9;")
            info_layout.addWidget(name_label)

            meta_label = QLabel(f"{ext.namespace}.{ext.name} v{ext.version}")
            meta_label.setStyleSheet("font-size: 11px; color: #6e7681;")
            info_layout.addWidget(meta_label)

            widget_layout.addLayout(info_layout, 1)

            # Status badge
            status_badge = QLabel("Enabled" if ext.enabled else "Disabled")
            status_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {'#3fb950' if ext.enabled else '#8b949e'};
                    color: white;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: 10px;
                    font-weight: bold;
                }}
            """)
            widget_layout.addWidget(status_badge)

            item.setSizeHint(widget.sizeHint())
            self.installed_list.addItem(item)
            self.installed_list.setItemWidget(item, widget)

    def set_offline(self, offline: bool):
        """Set offline mode."""
        self._offline = offline
        self.offline_label.setVisible(offline)
        self.search_box.setEnabled(not offline)
        self.search_btn.setEnabled(not offline)
        if offline:
            self.loading_label.setText("Offline — showing installed extensions")
            self.loading_label.setVisible(True)
            self.results_list.clear()

    def refresh(self):
        """Refresh the panel."""
        self._load_installed()


# Import needed for load_all_themes
from medha.extensions.contributions import load_all_themes