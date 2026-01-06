# ----- Build-In Modules -----
import os
import sys
from pathlib import Path
from typing import Literal

# ----- PyQt6 Modules -----
from PyQt6.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ModernButton(QPushButton):
    def __init__(self, text, color, hover_color, pressed_color) -> None:
        super().__init__(text)
        self.setFixedSize(100, 40)
        self.color = color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self._animation = QPropertyAnimation(self, b"geometry")
        self.setup_style()

    def setup_style(self) -> None:
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.pressed_color};
            }}
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)


class SystemPowerGUI(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.choice = ""
        self.time_left = 5

        icon_path: Path = (
            Path(__file__).parent.parent / "Assets" / "SystemPowerOptions.ico"
        )

        self.setWindowIcon(QIcon(str(icon_path)))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(380, 180)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(15, 15, 15, 15)
        outer_layout.setSpacing(0)

        container = QWidget()
        container.setObjectName("Container")
        container.setStyleSheet(
            """
            #Container {
                background-color: #1E1E2F;
                border-radius: 15px;
            }
            """
        )
        outer_layout.addWidget(container)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title_bar = QLabel("\u23fb  System Power Options")
        self.title_bar.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            """
        )
        self.title_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_bar)

        self.countdown_text = QLabel(f"Auto-shutdown in {self.time_left} seconds")
        self.countdown_text.setStyleSheet(
            """
            QLabel {
                color: #8E95B3;
                font-size: 13px;
            }
            """
        )
        main_layout.addWidget(self.countdown_text)

        main_layout.addSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.restart_btn = ModernButton("Restart", "#3B82F6", "#2563EB", "#1D4ED8")
        self.shutdown_btn = ModernButton("Shutdown", "#EF4444", "#DC2626", "#B91C1C")
        self.cancel_btn = ModernButton("Cancel", "#10B981", "#059669", "#047857")

        self.restart_btn.clicked.connect(lambda: self.button_clicked("restart"))
        self.shutdown_btn.clicked.connect(lambda: self.button_clicked("shutdown"))
        self.cancel_btn.clicked.connect(lambda: self.button_clicked("exit"))

        button_layout.addWidget(self.restart_btn)
        button_layout.addWidget(self.shutdown_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 120))
        container.setGraphicsEffect(shadow)

        # Setup timer for countdown
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

        # Setup auto-shutdown timer
        QTimer.singleShot(5000, self.auto_shutdown)

    def update_countdown(self) -> None:
        self.time_left -= 1
        if self.time_left >= 0:
            self.countdown_text.setText(f"Auto-shutdown in {self.time_left} seconds")

    def button_clicked(self, choice) -> None:
        self.choice = choice
        self.timer.stop()
        self.fade_out()

    def fade_out(self) -> None:
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(lambda: self.finish_action())
        self.animation.start()

    def finish_action(self) -> None:
        self.close()
        self.execute_choice()

    def auto_shutdown(self) -> None:
        if not self.choice:  # If no choice was made
            self.choice = "shutdown"
            self.close()
            self.execute_choice()

    def execute_choice(self) -> None:
        if self.choice == "shutdown":
            os.system("shutdown /s /t 0")  # Shut down the computer
        elif self.choice == "restart":
            os.system("shutdown /r /t 0")  # Reboot the computer
        elif self.choice == "exit":
            pass  # Just exit without action

    def mousePressEvent(self, event) -> None:
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event) -> None:
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    window = SystemPowerGUI()

    screen: QRect = app.primaryScreen().geometry()
    x: int = (screen.width() - window.width()) // 2
    y: int = (screen.height() - window.height()) // 2
    window.move(x, y)

    window.setWindowOpacity(0)
    window.show()

    animation = QPropertyAnimation(window, b"windowOpacity")
    animation.setDuration(300)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
