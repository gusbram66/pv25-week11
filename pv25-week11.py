import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QDockWidget,
    QStatusBar, QScrollArea, QHeaderView
)
from PyQt5.QtCore import Qt

class EnhancedMovieApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Movie Bookmark Manager")
        self.setGeometry(100, 100, 800, 600)
        self.resize(1000, 500)

        self.db_conn = None
        self.db_cursor = None
        self.init_db()

        self.initUI()

        self.load_movies_to_table()

    def init_db(self):
        try:
            self.db_conn = sqlite3.connect("movies_enhanced.db")
            self.db_cursor = self.db_conn.cursor()
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    genre TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    favorite INTEGER DEFAULT 0
                )
            """)
            self.db_conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not initialize database: {e}")
            sys.exit(1)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.setup_dock_widget()

        self.setup_status_bar()

        self.setup_scrollable_form(main_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Movie")
        add_button.clicked.connect(self.add_movie)
        update_button = QPushButton("Update Selected")
        update_button.clicked.connect(self.update_movie)
        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_movie)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        main_layout.addLayout(button_layout)

        self.movie_table = QTableWidget()
        self.movie_table.setColumnCount(5)
        self.movie_table.setHorizontalHeaderLabels(["ID", "Title", "Genre", "Rating", "Favorite"])
        self.movie_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.movie_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.movie_table.verticalHeader().setVisible(False)
        self.movie_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) 
        self.movie_table.cellClicked.connect(self.populate_form_on_select)
        main_layout.addWidget(self.movie_table)


    def setup_dock_widget(self):
        dock_widget = QDockWidget("Info Panel", self)
        dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        info_label = QLabel(
            "<h3>Application Help</h3>"
            "<p><b>Add:</b> Fill the form and click 'Add Movie'.</p>"
            "<p><b>Update:</b> Click a movie in the table, change the details in the form, and click 'Update Selected'.</p>"
            "<p><b>Delete:</b> Select a movie from the table and click 'Delete Selected'.</p>"
            "<p>This panel can be dragged, detached, or closed.</p>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px;")
        dock_widget.setWidget(info_label)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    def setup_status_bar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("NIM: F1D022052 | Name: Ida Bagus Brahmanta Jayana")

    def setup_scrollable_form(self, main_layout):
        form_container_widget = QWidget()
        form_layout = QGridLayout(form_container_widget)

        self.id_label = QLabel("N/A") 
        self.title_input = QLineEdit()
        self.genre_input = QComboBox()
        self.genre_input.addItems(["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller"])
        self.rating_input = QSpinBox()
        self.rating_input.setRange(1, 10)
        self.favorite_checkbox = QCheckBox("Mark as Favorite")

        paste_button = QPushButton("Paste from Clipboard")
        paste_button.clicked.connect(self.paste_title_from_clipboard)

        form_layout.addWidget(QLabel("<b>ID:</b>"), 0, 0)
        form_layout.addWidget(self.id_label, 0, 1)
        form_layout.addWidget(QLabel("<b>Title:</b>"), 1, 0)
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_input)
        title_layout.addWidget(paste_button)
        form_layout.addLayout(title_layout, 1, 1)
        
        form_layout.addWidget(QLabel("<b>Genre:</b>"), 2, 0)
        form_layout.addWidget(self.genre_input, 2, 1)
        form_layout.addWidget(QLabel("<b>Rating:</b>"), 3, 0)
        form_layout.addWidget(self.rating_input, 3, 1)
        form_layout.addWidget(self.favorite_checkbox, 4, 1)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(form_container_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        main_layout.addWidget(scroll_area)
        
    def paste_title_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.title_input.setText(clipboard.text())

    def add_movie(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Movie title cannot be empty.")
            return

        genre = self.genre_input.currentText()
        rating = self.rating_input.value()
        is_favorite = 1 if self.favorite_checkbox.isChecked() else 0

        try:
            self.db_cursor.execute(
                "INSERT INTO movies (title, genre, rating, favorite) VALUES (?, ?, ?, ?)",
                (title, genre, rating, is_favorite)
            )
            self.db_conn.commit()
            self.clear_form()
            self.load_movies_to_table()
            self.statusBar().showMessage(f"Successfully added '{title}'!", 3000)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Database Error", f"A movie with the title '{title}' already exists.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not add movie: {e}")

    def update_movie(self):
        movie_id = self.id_label.text()
        if not movie_id.isdigit():
            QMessageBox.warning(self, "Selection Error", "Please select a movie from the table to update.")
            return

        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Input Error", "Movie title cannot be empty.")
            return
            
        genre = self.genre_input.currentText()
        rating = self.rating_input.value()
        is_favorite = 1 if self.favorite_checkbox.isChecked() else 0

        try:
            self.db_cursor.execute(
                "UPDATE movies SET title = ?, genre = ?, rating = ?, favorite = ? WHERE id = ?",
                (title, genre, rating, is_favorite, int(movie_id))
            )
            self.db_conn.commit()
            self.clear_form()
            self.load_movies_to_table()
            self.statusBar().showMessage(f"Successfully updated '{title}'!", 3000)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not update movie: {e}")

    def delete_movie(self):
        current_row = self.movie_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a movie to delete.")
            return

        movie_id = self.movie_table.item(current_row, 0).text()
        movie_title = self.movie_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete '{movie_title}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.db_cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
                self.db_conn.commit()
                self.clear_form()
                self.load_movies_to_table()
                self.statusBar().showMessage(f"Successfully deleted '{movie_title}'!", 3000)
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Could not delete movie: {e}")

    def load_movies_to_table(self):
        try:
            self.db_cursor.execute("SELECT id, title, genre, rating, favorite FROM movies ORDER BY title")
            rows = self.db_cursor.fetchall()
            self.movie_table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                self.movie_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0]))) # ID
                self.movie_table.setItem(row_idx, 1, QTableWidgetItem(row_data[1])) # Title
                self.movie_table.setItem(row_idx, 2, QTableWidgetItem(row_data[2])) # Genre
                self.movie_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3]))) # Rating
                favorite_str = "Yes" if row_data[4] == 1 else "No"
                self.movie_table.setItem(row_idx, 4, QTableWidgetItem(favorite_str)) # Favorite
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Could not load movies: {e}")


    def populate_form_on_select(self, row, column):
        self.id_label.setText(self.movie_table.item(row, 0).text())
        self.title_input.setText(self.movie_table.item(row, 1).text())
        self.genre_input.setCurrentText(self.movie_table.item(row, 2).text())
        self.rating_input.setValue(int(self.movie_table.item(row, 3).text()))
        is_favorite = self.movie_table.item(row, 4).text() == "Yes"
        self.favorite_checkbox.setChecked(is_favorite)

    def clear_form(self):
        self.id_label.setText("N/A")
        self.title_input.clear()
        self.genre_input.setCurrentIndex(0)
        self.rating_input.setValue(1)
        self.favorite_checkbox.setChecked(False)

    def closeEvent(self, event):
        if self.db_conn:
            self.db_conn.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EnhancedMovieApp()
    window.show()
    sys.exit(app.exec_())