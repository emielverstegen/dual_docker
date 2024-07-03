# Dual Docker
This plugin creates another window next to the main QGIS interface. 
This second window can be positioned on a secondary monitor and can serve for docking widgets. 
This way you can keep your primary QGIS interface clean and your map canvas large.

## How it works
- Press the Dual Docker button in the plugin toolbar, a new window is created
- Position the Dual Docker window on a secondary monitor
- Drag a dockable widget on top of the Dual Docker screen and release it there.

## Known issues
- For now it only works when you pick up a dockwidget that is not floating (it is docked)
- When you drag the dockwidget above the Dual Docker widget it changes parent. 
However, you cannot immediately dock the widget. 
Release the widget and pick it up again, you should now be able to dock it.