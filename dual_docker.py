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

        self.event_filters = {}
        self.apply_event_filters()


    def remove_event_filters(self):

        for dock_widget, event_filter in self.event_filters.items():
            dock_widget.removeEventFilter(event_filter)
        self.event_filters.clear()


    def apply_event_filters(self):
        # Apply event filter to all dock widgets in the iface.mainWindow()
        for dock_widget in self.iface.mainWindow().findChildren((QDockWidget)):
            dock_widget.topLevelChanged.connect(self.on_dock_widget_top_level_changed)

            if dock_widget.isFloating():
                # If the dock widget is floating, install the floating event filter
                self.install_floating_event_filter(dock_widget)


        # Apply event filter to the main windows
        #self.iface.mainWindow().installEventFilter(self)
        #self.installEventFilter(self)

    def on_dock_widget_top_level_changed(self, floating):
        dock_widget = self.sender()
        if floating:
            # Switch to the floating event filter
            self.install_floating_event_filter(dock_widget)
        else:
            # Switch to the docked event filter
            #self.install_docked_event_filter(dock_widget)
            self.remove_floating_event_filter(dock_widget)

    def remove_floating_event_filter(self, dock_widget):
        # Remove any existing event filter
        if dock_widget in self.event_filters:
            dock_widget.removeEventFilter(self.event_filters[dock_widget])

    def install_floating_event_filter(self, dock_widget):
        # Remove any existing event filter
        if dock_widget in self.event_filters:
            dock_widget.removeEventFilter(self.event_filters[dock_widget])

        # Install the floating event filter
        event_filter = FloatingDockEventFilter(dock_widget, self)
        dock_widget.installEventFilter(event_filter)
        self.event_filters[dock_widget] = event_filter

        QgsMessageLog.logMessage(
            f"Installed floating event filter for '{dock_widget.windowTitle()}'.",
            "DualDocker",
            Qgis.Info
        )

class FloatingDockEventFilter(QObject):
    def __init__(self, dock_widget, parent_window):
        super().__init__()
        self.dock_widget = dock_widget
        self.parent_window = parent_window  # Reference to the parent DualDockerWindow

    def eventFilter(self, obj, event):

        # TODO: 
        # check if the left mouse button is pressed and the mouse is moved
        # check when a move is started and ended
        # check if the mouse is moved over the main window or the DualDockerWindow
        if event.type() == QEvent.Type.Move:

            mouse_pos = QCursor.pos()

            # Check if the mouse is within the geometry of iface.mainWindow()
            iface_window = self.parent_window.iface.mainWindow()
            iface_contains = iface_window.geometry().contains(mouse_pos)

            # Check if the mouse is within the geometry of this DualDockerWindow
            dual_docker_contains = self.parent_window.geometry().contains(mouse_pos)

            QgsMessageLog.logMessage(
                f"Current parent: {self.dock_widget.parent().windowTitle()}, iface_contains: {iface_contains}, dual_docker_contains: {dual_docker_contains}",
                "DualDocker",
                Qgis.Info
            )

            if iface_contains and self.dock_widget.parent() != iface_window:
                # Log the change in hovered window
                QgsMessageLog.logMessage(
                    f"{self.dock_widget.windowTitle()} is dragged to the main QGIS window.",
                    "DualDocker",
                    Qgis.Info
                )
                self.reparent_dock_widget(self.dock_widget,iface_window)

            elif dual_docker_contains and self.dock_widget.parent() != self.parent_window:
                # Log the change in hovered window
                QgsMessageLog.logMessage(
                    f"{self.dock_widget.windowTitle()} is dragged to the DualDockerWindow.",
                    "DualDocker",
                    Qgis.Info
                )
                self.reparent_dock_widget(self.dock_widget, self.parent_window)


        return super().eventFilter(obj, event)
    
    def reparent_dock_widget(self, dock_widget, window):
        if not isinstance(window, QMainWindow):
            QgsMessageLog.logMessage(
                "Target window is not a QMainWindow. Cannot reparent dock widget.",
                "DualDocker",
                Qgis.Warning
            )
            return

        if dock_widget:
            QgsMessageLog.logMessage(
                f"Reparenting {dock_widget.windowTitle()} to {window.windowTitle()}",
                "DualDocker",
                Qgis.Info
            )

            mouse_pos = QCursor.pos()

            # # Convert the local position to QPointF
            local_pos = QPointF(dock_widget.mapFromGlobal(mouse_pos))

            # Simulate a mouse release event to end the current drag
            QTimer.singleShot(0, lambda: self._simulate_mouse_release(dock_widget, local_pos, mouse_pos))

            # # # Process all pending events to stabilize the widget
            QApplication.processEvents()

            # Reparent
            # first, remove the dock widget from its current parent
            current_parent = dock_widget.parentWidget()
            if isinstance(current_parent, QMainWindow):
                current_parent.removeDockWidget(dock_widget)

            # Add the dock widget to the new parent
            window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)
            #self.current_dragged_dock.setFloating(True)
            dock_widget.show()


            # Defer the mouse press event using QTimer
            #QTimer.singleShot(100, lambda: self._simulate_mouse_press(local_pos, mouse_pos))
            #QApplication.processEvents()


    def _simulate_mouse_release(self, dock_widget, local_pos, global_pos):
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
        QApplication.sendEvent(dock_widget, press_event)

        QgsMessageLog.logMessage(
            f"Mouse release event simulated for {dock_widget.windowTitle()}",
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
