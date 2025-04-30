import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTableView,
    QSplitter,
)
from PyQt5.QtCore import Qt

# GUI Constants
GUI_PATH = os.path.join("gui", "styles.qss")


class MovieExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to MoVIZ Data Explorer")
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(self._load_styles(GUI_PATH))
        self._init_ui()

    def _init_ui(self):
        # Main central widget setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Title bar at the top
        title_bar = QHBoxLayout()
        title_label = QLabel("MoViz Dashboard")
        title_label.setObjectName("TitleLabel")
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        main_layout.addLayout(title_bar)

        # Filter section with 4 sub-sections
        filter_row = QHBoxLayout()

        # Box 1: Filter A
        #
        box1 = QVBoxLayout()
        box1.addWidget(QLabel("Filter 1:"))
        self.filter1 = QComboBox()
        self.filter1.addItems(["Year", "Genre", "Director"])
        box1.addWidget(self.filter1)
        filter_row.addLayout(box1)

        # Box 2: Filter B
        box2 = QVBoxLayout()
        box2.addWidget(QLabel("Filter 2:"))
        self.filter2 = QComboBox()
        self.filter2.addItems(["Budget", "Box Office", "Votes"])
        box2.addWidget(self.filter2)
        filter_row.addLayout(box2)

        # Box 3: Plot type
        box3 = QVBoxLayout()
        box3.addWidget(QLabel("Plot Type:"))
        self.plot_type = QComboBox()
        self.plot_type.addItems(["Bar Chart", "Scatter Plot", "Line Plot"])
        box3.addWidget(self.plot_type)
        filter_row.addLayout(box3)

        # Box 4: Go Button
        box4 = QVBoxLayout()
        box4.addStretch()
        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self._run_visualization)
        box4.addWidget(self.go_button)
        box4.addStretch()
        filter_row.addLayout(box4)

        main_layout.addLayout(filter_row)

        # Display section (table + plot or status)
        self.splitter = QSplitter(Qt.Vertical)
        self.result_table = QTableView()
        self.result_label = QLabel("Ready to generate visualizations.")
        self.result_label.setAlignment(Qt.AlignCenter)

        self.splitter.addWidget(self.result_table)
        self.splitter.addWidget(self.result_label)
        main_layout.addWidget(self.splitter)

    def _run_visualization(self):
        f1 = self.filter1.currentText()
        f2 = self.filter2.currentText()
        plot = self.plot_type.currentText()
        self.result_label.setText(f"Visualizing: {f1} vs {f2} as {plot}...")
        # TODO: Connect to DB, generate plot, update table

    def _load_styles(self, qss_path):
        try:
            with open(qss_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieExplorer()
    window.show()
    sys.exit(app.exec_())
