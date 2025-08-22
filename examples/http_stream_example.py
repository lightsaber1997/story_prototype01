# -*- coding: utf-8 -*-
"""
Example usage of HTTP streaming functionality in StorybookArea

This demonstrates how to integrate the new HTTP streaming capabilities
with existing UI components, replacing direct LLM engine calls.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel
from PySide6.QtCore import Qt

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.storybook_area import StorybookArea


class HttpStreamDemo(QMainWindow):
    """Demo application showing HTTP streaming integration"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTTP Stream Demo - StorybookArea")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Control panel
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Enter story prompt...")
        self.prompt_input.returnPressed.connect(self.start_stream)
        
        self.server_url_input = QLineEdit("http://localhost:8080")
        self.server_url_input.setPlaceholderText("C++ server URL...")
        
        self.start_button = QPushButton("Start Stream")
        self.start_button.clicked.connect(self.start_stream)
        
        self.stop_button = QPushButton("Stop Stream")
        self.stop_button.clicked.connect(self.stop_stream)
        self.stop_button.setEnabled(False)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: green;")
        
        # Add controls to layout
        layout.addWidget(QLabel("Prompt:"))
        layout.addWidget(self.prompt_input)
        layout.addWidget(QLabel("Server URL:"))
        layout.addWidget(self.server_url_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)
        
        # Storybook area
        self.storybook = StorybookArea()
        layout.addWidget(self.storybook, 1)  # Give it most of the space
        
        # Connect storybook signals
        self.storybook.streamStarted.connect(self.on_stream_started)
        self.storybook.streamFinished.connect(self.on_stream_finished)
        self.storybook.streamError.connect(self.on_stream_error)
        
    def start_stream(self):
        """Start HTTP streaming with user input"""
        prompt = self.prompt_input.text().strip()
        server_url = self.server_url_input.text().strip()
        
        if not prompt:
            self.status_label.setText("Please enter a prompt")
            self.status_label.setStyleSheet("color: red;")
            return
            
        if not server_url:
            server_url = "http://localhost:8080"
        
        # Update server URL
        self.storybook.setServerUrl(server_url)
        
        # Start streaming
        self.storybook.startHttpStream(prompt)
        
    def stop_stream(self):
        """Stop current streaming"""
        self.storybook.stopHttpStream()
        
    def on_stream_started(self):
        """Handle stream start"""
        self.status_label.setText("Streaming...")
        self.status_label.setStyleSheet("color: blue;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
    def on_stream_finished(self):
        """Handle stream completion"""
        self.status_label.setText("Stream completed")
        self.status_label.setStyleSheet("color: green;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
    def on_stream_error(self, error_message: str):
        """Handle stream error"""
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("color: red;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    demo = HttpStreamDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()