from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.core import QgsMessageLog, Qgis

# initialize Qt resources from file resources.py
from . import resources


# TODO
# Add event filter to newly created dock widgets in the main window
# Deal with QStatckedWidget and QTabWidget
# Improve dragdetection when an floating widget is picked up

class DualDocker:

    def __init__(self, iface):
        # save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        # create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/dual_docker/icon.png"),
                            "Dual Docker",
                            self.iface.mainWindow())
        self.action.setObjectName("testAction")
        self.action.setWhatsThis("Configuration for test plugin")
        self.action.setStatusTip("Open a Dual Docker window")
        self.action.setToolTip("Open a Dual Docker window")
        self.action.triggered.connect(self.run)

        # add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        #self.iface.addPluginToMenu("&Test plugins", self.action)

        # connect to signal renderComplete which is emitted when canvas
        # rendering is done
        self.iface.mapCanvas().renderComplete.connect(self.renderTest)

    def unload(self):
        # Remove event filters
        if hasattr(self, 'dd_window') and self.dd_window:
            self.dd_window.remove_event_filters()

        # remove the plugin menu item and icon
        self.iface.removePluginMenu("&Test plugins", self.action)
        self.iface.removeToolBarIcon(self.action)

        # disconnect form signal of the canvas
        self.iface.mapCanvas().renderComplete.disconnect(self.renderTest)

    def run(self):
        # create and show a configuration dialog or something similar
        self.create_dd_window()

    def renderTest(self, painter):
        # use painter for drawing to map canvas
        print("TestPlugin: renderTest called!")

    def create_dd_window(self):
        self.dd_window = DualDockerWindow(self.iface)
        self.dd_window.show()
    
class DualDockerWindow(QMainWindow):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Dual Docker")
        self.setGeometry(100, 100, 800, 600)  # Adjust size for a main window

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Set up a layout for the central widget
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Variable to store the currently dragged dock widget
        self.current_dragged_dock = None     
        self.current_dragged_over = None
        self.handling_event = False   

        self.apply_event_filters()


    def remove_event_filters(self):
        # Remove event filter from all dock widgets in this window
        for dock_widget in self.findChildren(QDockWidget):
            dock_widget.removeEventFilter(self)

        # Remove event filter from all dock widgets in the iface.mainWindow()
        for dock_widget in self.iface.mainWindow().findChildren(QDockWidget):
            dock_widget.removeEventFilter(self)

        # Remove event filter from the main windows
        self.iface.mainWindow().removeEventFilter(self)
        self.removeEventFilter(self)


    def apply_event_filters(self):
        # Apply event filter to all dock widgets in this window
        for dock_widget in self.findChildren(QDockWidget):
            dock_widget.installEventFilter(self)

        # Apply event filter to all dock widgets in the iface.mainWindow()
        for dock_widget in self.iface.mainWindow().findChildren(QDockWidget):
            dock_widget.installEventFilter(self)

        # Apply event filter to the main windows
        self.iface.mainWindow().installEventFilter(self)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if self.handling_event:
            # Skip handling events while simulating mouse events
            return super().eventFilter(source, event)

        # Handle dock widget drag events
        if isinstance(source, QDockWidget):
            if event.type() == QEvent.Type.MouseButtonPress:
                # Start tracking the dragged dock widget
                self.current_dragged_dock = source
                self.current_dragged_over = source.parentWidget()
                QgsMessageLog.logMessage(
                    f"Started dragging {source.windowTitle()}",
                    "DualDocker",
                    Qgis.Info
                )
            elif event.type() == QEvent.Type.MouseButtonRelease:
                # Stop tracking the dragged dock widget
                QgsMessageLog.logMessage(
                    f"Stopped dragging {source.windowTitle()}",
                    "DualDocker",
                    Qgis.Info
                )
                self.current_dragged_dock = None

            if self.current_dragged_dock:
                if event.type() == QEvent.Type.Move:
                    mouse_pos = QCursor.pos()

                    # Check if the mouse is within the geometry of iface.mainWindow()
                    iface_window = self.iface.mainWindow()
                    iface_contains = iface_window.geometry().contains(mouse_pos)

                    # Check if the mouse is within the geometry of this DualDockerWindow
                    dual_docker_contains = self.geometry().contains(mouse_pos)

                    if iface_contains:
                        if self.current_dragged_over != iface_window:
                            # Log the change in hovered window
                            QgsMessageLog.logMessage(
                                f"{self.current_dragged_dock.windowTitle()} is dragged to the main QGIS window.",
                                "DualDocker",
                                Qgis.Info
                            )
                            self.current_dragged_over = iface_window
                            self.reparent_dock_widget(iface_window)

                    elif dual_docker_contains:
                        if self.current_dragged_over != self:
                            # Log the change in hovered window
                            QgsMessageLog.logMessage(
                                f"{self.current_dragged_dock.windowTitle()} is dragged to the DualDockerWindow.",
                                "DualDocker",
                                Qgis.Info
                            )
                            self.current_dragged_over = self
                            self.reparent_dock_widget(self)

        return super().eventFilter(source, event)
    

    def reparent_dock_widget(self, window):
        if not isinstance(window, QMainWindow):
            QgsMessageLog.logMessage(
                "Target window is not a QMainWindow. Cannot reparent dock widget.",
                "DualDocker",
                Qgis.Warning
            )
            return

        if self.current_dragged_dock:
            QgsMessageLog.logMessage(
                f"Reparenting {self.current_dragged_dock.windowTitle()} to {window.windowTitle()}",
                "DualDocker",
                Qgis.Info
            )

            mouse_pos = QCursor.pos()

            # # Convert the local position to QPointF
            local_pos = QPointF(self.current_dragged_dock.mapFromGlobal(mouse_pos))

            # Simulate a mouse release event to end the current drag
            QTimer.singleShot(0, lambda: self._simulate_mouse_release(local_pos, mouse_pos))

            # # # Process all pending events to stabilize the widget
            QApplication.processEvents()

            # Reparent
            # first, remove the dock widget from its current parent
            current_parent = self.current_dragged_dock.parentWidget()
            if isinstance(current_parent, QMainWindow):
                current_parent.removeDockWidget(self.current_dragged_dock)

            # Add the dock widget to the new parent
            window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.current_dragged_dock)
            self.current_dragged_dock.setFloating(True)
            self.current_dragged_dock.show()

            # Defer the mouse press event using QTimer
            #QTimer.singleShot(100, lambda: self._simulate_mouse_press(local_pos, mouse_pos))
            #QApplication.processEvents()


    def _simulate_mouse_release(self, local_pos, global_pos):
        # Temporarily disable event handling
        self.handling_event = True

        # Simulate a mouse release event to stop dragging
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            local_pos,
            QPointF(global_pos),  # Global position as QPointF
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        QApplication.sendEvent(self.current_dragged_dock, press_event)

        QgsMessageLog.logMessage(
            f"Mouse release event simulated for {self.current_dragged_dock.windowTitle()}",
            "DualDocker",
            Qgis.Info
        )

        # Re-enable event handling
        self.handling_event = False

    def _simulate_mouse_press(self, local_pos, global_pos):
        # Temporarily disable event handling
        self.handling_event = True

        # Simulate a mouse press event to start dragging again
        press_event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            local_pos,
            QPointF(global_pos),  # Global position as QPointF
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        QApplication.sendEvent(self.current_dragged_dock, press_event)

        QgsMessageLog.logMessage(
            f"Mouse press event simulated for {self.current_dragged_dock.windowTitle()}",
            "DualDocker",
            Qgis.Info
        )

        # Re-enable event handling
        self.handling_event = False





            # # Remove the dock widget from its current parent
            # current_parent = self.current_dragged_dock.parentWidget()
            # if isinstance(current_parent, QMainWindow):
            #     try:
            #         current_parent.removeDockWidget(self.current_dragged_dock)
            #     except RuntimeError as e:
            #         QgsMessageLog.logMessage(
            #             f"Error removing dock widget from current parent: {e}",
            #             "DualDocker",
            #             Qgis.Critical
            #         )
            #         return

            # # Add the dock widget to the new parent
            # try:
            #     window.addDockWidget(Qt.LeftDockWidgetArea, self.current_dragged_dock)
            # except RuntimeError as e:
            #     QgsMessageLog.logMessage(
            #         f"Error adding dock widget to new parent: {e}",
            #         "DualDocker",
            #         Qgis.Critical
            #     )
            #     return

            # # Ensure the dock widget is visible and floating
            # self.current_dragged_dock.setFloating(True)
            # self.current_dragged_dock.show()

            # # Reset the current dragged dock reference
            # self.current_dragged_dock = None