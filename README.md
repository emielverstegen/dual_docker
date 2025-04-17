# QGIS Plugin Documentation

## Overview
This QGIS plugin is designed to enhance the user experience by providing a custom toolbar button that opens a new maximizable window. The plugin allows users to drag and drop QtWidgets from the main application into the new window, facilitating a more flexible workspace.

## Project Structure
The project is organized as follows:

```
qgis-plugin
├── plugin
│   ├── __init__.py          # Initializes the plugin package
│   ├── main.py              # Main entry point for the plugin
│   ├── resources.qrc        # Resource definitions for icons and images
│   ├── ui
│   │   ├── main_window.ui    # Main window UI layout
│   │   └── secondary_window.ui # Secondary window UI layout
│   └── utils
│       └── helpers.py       # Utility functions for the plugin
├── metadata.txt             # Plugin metadata
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

## Installation
1. Clone the repository or download the plugin files.
2. Place the `qgis-plugin` folder in your QGIS plugins directory.
3. Install the required dependencies listed in `requirements.txt` using pip:
   ```
   pip install -r requirements.txt
   ```

## Usage
- After installing the plugin, restart QGIS.
- You will see a new button on the toolbar.
- Click the button to open a new maximizable window.
- You can drag and drop QtWidgets from the main QGIS application into the new window.

## Contributing
Contributions are welcome! Please feel free to submit issues or pull requests.

## License
This project is licensed under the MIT License. See the LICENSE file for details.