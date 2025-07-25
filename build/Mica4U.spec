# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['../main.py'],
    pathex=['../'],
    binaries=[],
    datas=[
        ('../icon.ico', '.'),
        ('../assets/icons/*', 'assets/icons')
    ],
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'argparse',
        'asyncio',
        'bdb',
        'calendar',
        'cmd',
        'copy',
        'csv',
        'decimal',
        'difflib',
        'dis',
        'doctest',
        'fractions',
        'ftplib',
        'getopt',
        'heapq',
        'inspect',
        'itertools',
        'logging',
        'math',
        'multiprocessing',
        'pathlib.Path',
        'pickle',
        'pprint',
        'queue',
        'random'
        'statistics',
        'struct',
        'traceback'
        'typing',
        'uuid',
        "tkinter",
        "sqlite3",

        # PyQt6.QtWidgets (unused)
        'QAbstractButton',
        'QAbstractItemView',
        'QAbstractScrollArea',
        'QAbstractSlider',
        'QAbstractSpinBox',
        'QAction',
        'QActionGroup',
        'QApplication',
        'QBoxLayout',
        'QCalendarWidget',
        'QCommandLinkButton',
        'QCommonStyle',
        'QCompleter',
        'QDataWidgetMapper',
        'QDateEdit',
        'QDateTimeEdit',
        'QDial',
        'QDockWidget',
        'QDoubleSpinBox',
        'QErrorMessage',
        'QFileDialog',
        'QFontComboBox',
        'QFontDialog',
        'QFrame',
        'QGesture',
        'QGraphicsAnchor',
        'QGraphicsAnchorLayout',
        'QGraphicsBlurEffect',
        'QGraphicsColorizeEffect',
        'QGraphicsDropShadowEffect',
        'QGraphicsEffect',
        'QGraphicsEllipseItem',
        'QGraphicsGridLayout',
        'QGraphicsItem',
        'QGraphicsItemGroup',
        'QGraphicsLineItem',
        'QGraphicsObject',
        'QGraphicsOpacityEffect',
        'QGraphicsPathItem',
        'QGraphicsPixmapItem',
        'QGraphicsPolygonItem',
        'QGraphicsProxyWidget',
        'QGraphicsRectItem',
        'QGraphicsScene',
        'QGraphicsSceneContextMenuEvent',
        'QGraphicsSceneDragDropEvent',
        'QGraphicsSceneEvent',
        'QGraphicsSceneHoverEvent',
        'QGraphicsSceneMouseEvent',
        'QGraphicsSceneMoveEvent',
        'QGraphicsSceneResizeEvent',
        'QGraphicsSceneWheelEvent',
        'QGraphicsSimpleTextItem',
        'QGraphicsTextItem',
        'QGraphicsView',
        'QGraphicsWidget',
        'QGroupBox',
        'QHeaderView',
        'QItemDelegate',
        'QKeySequenceEdit',
        'QLabelFrame',
        'QLineEdit',
        'QListView',
        'QListWidget',
        'QListWidgetItem',
        'QMainWindow',
        'QMdiArea',
        'QMdiSubWindow',
        'QMenu',
        'QMenuBar',
        'QMessageBox',
        'QPlainTextEdit',
        'QProgressBar',
        'QProgressDialog',
        'QPushButton',
        'QRadioButton',
        'QScrollArea',
        'QScrollBar',
        'QSlider',
        'QSpinBox',
        'QSplashScreen',
        'QSplitter',
        'QStackedLayout',
        'QStackedWidget',
        'QStatusBar',
        'QStyle',
        'QStyleFactory',
        'QStyleOption',
        'QStyleOptionButton',
        'QStyleOptionComboBox',
        'QStyleOptionComplex',
        'QStyleOptionDockWidget',
        'QStyleOptionFocusRect',
        'QStyleOptionFrame',
        'QStyleOptionGraphicsItem',
        'QStyleOptionGroupBox',
        'QStyleOptionHeader',
        'QStyleOptionMenuItem',
        'QStyleOptionProgressBar',
        'QStyleOptionRubberBand',
        'QStyleOptionSlider',
        'QStyleOptionSpinBox',
        'QStyleOptionTab',
        'QStyleOptionTabBarBase',
        'QStyleOptionTabWidgetFrame',
        'QStyleOptionTitleBar',
        'QStyleOptionToolBar',
        'QStyleOptionToolButton',
        'QStyleOptionViewItem',
        'QStyledItemDelegate',
        'QSystemTrayIcon',
        'QTabBar',
        'QTabWidget',
        'QTableView',
        'QTableWidget',
        'QTableWidgetItem',
        'QTextBrowser',
        'QTextEdit',
        'QTimeEdit',
        'QToolBar',
        'QToolBox',
        'QToolButton',
        'QTreeView',
        'QTreeWidget',
        'QTreeWidgetItem',
        'QUndoCommand',
        'QUndoStack',
        'QUndoView',
        'QWhatsThis',

        # PyQt6.QtCore (unused)
        'QAbstractAnimation',
        'QAbstractEventDispatcher',
        'QAbstractItemModel',
        'QAbstractListModel',
        'QAbstractNativeEventFilter',
        'QAbstractProxyModel',
        'QAbstractState',
        'QAbstractTableModel',
        'QAbstractTransition',
        'QAnimationGroup',
        'QBasicTimer',
        'QBitArray',
        'QBuffer',
        'QByteArray',
        'QByteArrayMatcher',
        'QCalendar',
        'QChildEvent',
        'QCoreApplication',
        'QCryptographicHash',
        'QDataStream',
        'QDate',
        'QDateTime',
        'QDeadlineTimer',
        'QDir',
        'QDirIterator',
        'QEasingCurve',
        'QElapsedTimer',
        'QEvent',
        'QEventLoop',
        'QFile',
        'QFileDevice',
        'QFileInfo',
        'QFileSelector',
        'QFileSystemWatcher',
        'QFinalState',
        'QHistoryState',
        'QIODevice',
        'QItemSelection',
        'QItemSelectionModel',
        'QJsonDocument',
        'QJsonParseError',
        'QJsonValue',
        'QLibraryInfo',
        'QLine',
        'QLineF',
        'QLocale',
        'QMarginsF',
        'QMimeData',
        'QMimeDatabase',
        'QMimeType',
        'QModelIndex',
        'QMutex',
        'QObjectCleanupHandler',
        'QParallelAnimationGroup',
        'QPersistentModelIndex',
        'QPoint',
        'QPointF',
        'QProcess',
        'QProcessEnvironment',
        'QPropertyAnimation',
        'QRect',
        'QRectF',
        'QRegExp',
        'QRegularExpression',
        'QRegularExpressionMatch',
        'QRegularExpressionMatchIterator',
        'QResource',
        'QRunnable',
        'QSemaphore',
        'QSequentialAnimationGroup',
        'QSettings',
        'QSignalMapper',
        'QSize',
        'QSizeF',
        'QSocketNotifier',
        'QSortFilterProxyModel',
        'QStandardPaths',
        'QState',
        'QStateMachine',
        'QStringListModel',
        'QSysInfo',
        'QSystemSemaphore',
        'QTemporaryDir',
        'QTemporaryFile',
        'QTextBoundaryFinder',
        'QTextCodec',
        'QTextDecoder',
        'QTextEncoder',
        'QTextStream',
        'QThreadPool',
        'QTime',
        'QTimeLine',
        'QTimeZone',
        'QTranslator',
        'QVariantAnimation',
        'QWaitCondition',
        'QXmlStreamAttribute',
        'QXmlStreamAttributes',
        'QXmlStreamEntityDeclaration',
        'QXmlStreamEntityResolver',
        'QXmlStreamNamespaceDeclaration',
        'QXmlStreamNotationDeclaration',
        'QXmlStreamReader',
        'QXmlStreamWriter',

        # PyQt6.QtGui (unused)
        'QAbstractTextDocumentLayout',
        'QActionEvent',
        'QBitmap',
        'QBrush',
        'QClipboard',
        'QCloseEvent',
        'QConicalGradient',
        'QContextMenuEvent',
        'QCursor',
        'QDrag',
        'QDragEnterEvent',
        'QDragLeaveEvent',
        'QDragMoveEvent',
        'QDropEvent',
        'QEnterEvent',
        'QExposeEvent',
        'QFocusEvent',
        'QFont',
        'QFontDatabase',
        'QFontInfo',
        'QFontMetrics',
        'QGradient',
        'QGuiApplication',
        'QHideEvent',
        'QHoverEvent',
        'QImage',
        'QImageIOHandler',
        'QImageReader',
        'QImageWriter',
        'QInputEvent',
        'QInputMethod',
        'QInputMethodEvent',
        'QKeyEvent',
        'QKeySequence',
        'QLinearGradient',
        'QMouseEvent',
        'QMoveEvent',
        'QPaintDevice',
        'QPaintEngine',
        'QPaintEvent',
        'QPainter',
        'QPainterPath',
        'QPen',
        'QPicture',
        'QPixelFormat',
        'QRadialGradient',
        'QRegion',
        'QResizeEvent',
        'QScreen',
        'QSessionManager',
        'QShortcut',
        'QShortcutEvent',
        'QShowEvent',
        'QStandardItem',
        'QStandardItemModel',
        'QSurface',
        'QSurfaceFormat',
        'QTabletEvent',
        'QTextBlock',
        'QTextCharFormat',
        'QTextCursor',
        'QTextDocument',
        'QTextFormat',
        'QTextLayout',
        'QTextList',
        'QTextObject',
        'QTextTable',
        'QTouchEvent',
        'QValidator',
        'QWheelEvent',
        'QWindow',
        'QWindowStateChangeEvent',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Mica4U',
    debug=False,
    bootloader_ignore_signals=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    codesign_identity=None,
    entitlements_file=None,
    icon='../icon.ico',
    onefile=True,
    uac_admin=True
)