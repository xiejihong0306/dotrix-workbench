from PyQt5.QtWidgets import QLabel, QFrame, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropArea(QLabel):
    """可接受拖放操作的标签区域"""
    def __init__(self, parent=None, accept_func=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setAcceptDrops(True)
        self.accept_func = accept_func
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        if self.accept_func and event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.accept_func(file_paths)
            event.acceptProposedAction()

class DropListWidget(QListWidget):
    """支持拖放操作的列表控件"""
    def __init__(self, parent=None, accept_func=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.accept_func = accept_func
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # 调试信息
            print("文件拖入列表区域")
            for url in event.mimeData().urls():
                print(f"  - {url.toLocalFile()}")
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        # 必须重写此方法以允许拖动移动
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        if self.accept_func and event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            print(f"拖放接收: {len(file_paths)} 个文件")
            self.accept_func(file_paths)
            event.acceptProposedAction() 