from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QSlider, QStackedWidget, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import QTimer, QTime, pyqtSignal, QThread, QUrl, Qt
from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent
import random
import sys
from functools import partial


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.sound_effect = None

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel("Настройки")
        label.setStyleSheet("font-size: 24pt;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        volume_label = QLabel("Громкость")
        layout.addWidget(volume_label)
        volume_label.setStyleSheet("font-size: 18pt;")
        self.setLayout(layout)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        layout.addWidget(self.volume_slider)

        self.setLayout(layout)

        self.volume_slider.valueChanged.connect(self.set_volume)

    def set_volume(self, value):
        print("Громкость изменена на:", value)
        if self.sound_effect:
            volume = value / 100.0
            print("Громкость в диапазоне от 0.0 до 1.0:", volume)
            self.sound_effect.setVolume(volume)


class TimerThread(QThread):
    timeChanged = pyqtSignal(QTime)

    def __init__(self):
        super().__init__()
        self.game_time = QTime(0, 0)
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self.msleep(1000)
            self.game_time = self.game_time.addSecs(1)
            self.timeChanged.emit(self.game_time)


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Кликомания')
        self.setFixedSize(600, 600)

        self.sound_effect = QSoundEffect(self)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.main_menu_widget = QWidget()
        layout = QVBoxLayout()

        game_label = QLabel('Кликомания')
        game_label.setAlignment(Qt.AlignCenter)
        game_label.setStyleSheet("font-size: 36pt;")
        layout.addWidget(game_label)

        play_button = QPushButton('Играть')
        play_button.clicked.connect(self.play_game)
        layout.addWidget(play_button)

        settings_button = QPushButton('Настройки')
        settings_button.clicked.connect(self.show_settings)
        layout.addWidget(settings_button)

        exit_button = QPushButton('Выход')
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)

        self.main_menu_widget.setLayout(layout)
        self.central_widget.addWidget(self.main_menu_widget)

        self.settings_widget = SettingsWidget()
        self.settings_widget.sound_effect = self.sound_effect
        back_button = QPushButton('Назад')
        back_button.clicked.connect(self.show_main_menu)
        self.settings_widget.layout().addWidget(back_button)
        self.central_widget.addWidget(self.settings_widget)
        self.settings_widget.hide()

    def play_game(self):
        self.game_widget = ClickomaniaGame(sound_effect=self.sound_effect)
        self.game_widget.returnToMainMenu.connect(self.show_main_menu)
        self.central_widget.addWidget(self.game_widget)
        self.central_widget.setCurrentWidget(self.game_widget)

    def show_settings(self):
        self.central_widget.setCurrentWidget(self.settings_widget)

    def show_main_menu(self):
        self.central_widget.setCurrentWidget(self.main_menu_widget)


class ClickomaniaGame(QWidget):
    returnToMainMenu = pyqtSignal()

    def __init__(self, sound_effect=None):
        super().__init__()
        self.first_click = None
        self.sound_effect = sound_effect
        self.game_time = None
        self.initUI()
        self.timer_thread = TimerThread()
        self.timer_thread.timeChanged.connect(self.update_time_label)
        self.timer_thread.start()

        self.load_personal_record()

    def initUI(self):
        self.setWindowTitle('Кликомания')
        self.setGeometry(100, 100, 800, 800)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        self.create_grid(rows=10, cols=10)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.play_again_button = QPushButton('Играть заново')
        self.play_again_button.clicked.connect(self.restart_game)
        self.button_layout.addWidget(self.play_again_button)

        self.score = 0
        self.score_label = QLabel(f'Счет: {self.score}')
        self.score_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button_layout.addWidget(self.score_label)

        self.personal_record = 0
        self.personal_record_label = QLabel(f'Личный рекорд: {self.personal_record}')
        self.personal_record_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button_layout.addWidget(self.personal_record_label)

        self.game_time = QTime(0, 0)
        self.time_label = QLabel('Время: 00:00')
        self.time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button_layout.addWidget(self.time_label)

        self.back_button = QPushButton('Назад')
        self.back_button.clicked.connect(self.return_to_main_menu)
        self.button_layout.addWidget(self.back_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.game_started = False
        self.first_click = False

    def initSoundEffect(self):
        self.sound_effect = QSoundEffect(self)
        self.sound_effect.setSource(QUrl.fromLocalFile("da.wav"))

    def load_personal_record(self):
        try:
            with open('personal_record.txt', 'r') as f:
                self.personal_record = int(f.read())
        except FileNotFoundError:
            self.personal_record = 0

        self.personal_record_label.setText(f'Личный рекорд:{self.personal_record}')

    def save_personal_record(self):
        with open('personal_record.txt', 'w') as f:
            f.write(str(self.personal_record))

    def update_personal_record(self, score):
        if score > self.personal_record:
            self.personal_record = score
            self.save_personal_record()
        self.personal_record_label.setText(f'Личный рекорд: {self.personal_record}')

    def delete_cubes(self):
        score = self.score
        self.update_personal_record(score)

    def create_grid(self, rows, cols):
        self.buttons = []

        for i in range(rows):
            row_buttons = []
            for j in range(cols):
                color = random.choice(['red', 'blue', 'green', 'yellow'])
                button = QPushButton('')
                button.setStyleSheet(f'background-color: {color}')
                button.setFixedSize(40, 40)
                button.setMinimumSize(40, 40)
                button.setMaximumSize(40, 40)
                button.clicked.connect(lambda _, row=i, col=j: self.on_button_click(row, col))
                self.grid_layout.addWidget(button, i, j)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        for i in range(rows, 10):
            for j in range(10):
                empty_label = QLabel('')
                empty_label.setFixedSize(40, 40)
                self.grid_layout.addWidget(empty_label, i, j)

        for i in range(rows):
            empty_widget = QWidget()
            empty_widget.setFixedSize(40, 40)
            self.grid_layout.addWidget(empty_widget, i, cols)

        for j in range(cols + 1):
            empty_widget = QWidget()
            empty_widget.setFixedSize(40, 40)
            self.grid_layout.addWidget(empty_widget, rows, j)

    def reset_score(self):
        self.score = 0
        self.update_score_label()

    def update_score_label(self):
        self.score_label.setText(f'Счет: {self.score}')

    def update_time_label(self, game_time):
        formatted_time = game_time.toString("mm:ss")
        self.time_label.setText(f'Время: {formatted_time}')

    def restart_game(self):
        self.reset_score()

        self.timer_thread.stop()

        self.reset_timer()

        for row in range(len(self.buttons)):
            for col in range(len(self.buttons[row])):
                button = self.buttons[row][col]
                if button is not None:
                    button.deleteLater()
                    self.buttons[row][col] = None

        self.create_grid(rows=10, cols=10)

        self.timer_thread = TimerThread()
        self.timer_thread.timeChanged.connect(self.update_time_label)
        self.timer_thread.start()

    def reset_timer(self):
        self.game_time = QTime(0, 0)
        self.update_time_label(self.game_time)

    def return_to_main_menu(self):
        self.returnToMainMenu.emit()

    def is_column_empty(self, col):
        for row in range(len(self.buttons)):
            if self.buttons[row][col] is not None:
                return False
        return True

    def on_button_click(self, row, col):
        if not self.game_started:
            self.game_started = True
            self.first_click = True

        color = self.buttons[row][col].palette().button().color().name()

        if self.remove_group(color, row, col):
            self.check_empty_columns()

    def remove_group(self, color, row, col):
        group = set()
        self.find_adjacent_buttons(color, row, col, group)

        if len(group) > 1:
            self.play_sound_effect()
            self.score += len(group)
            self.update_score_label()

            for r, c in group:
                button = self.buttons[r][c]
                if button is not None:
                    self.grid_layout.removeWidget(button)
                    button.deleteLater()
                    self.buttons[r][c] = None

            self.apply_gravity()
            self.remove_empty_columns()
            self.update_personal_record(self.score)
            return True
        else:
            return False

    def remove_column(self, col):
        # Удаляем виджеты из удалённого столбца
        for row in range(len(self.buttons)):
            if self.buttons[row][col] is not None:
                self.grid_layout.removeWidget(self.buttons[row][col])
                self.buttons[row][col].deleteLater()
                self.buttons[row][col] = None

        # Сдвигаем все столбцы влево
        for j in range(col + 1, len(self.buttons[0])):
            for row in range(len(self.buttons)):
                self.buttons[row][j - 1] = self.buttons[row][j]
                if self.buttons[row][j - 1] is not None:
                    self.grid_layout.removeWidget(self.buttons[row][j - 1])
                    self.grid_layout.addWidget(self.buttons[row][j - 1], row, j - 1)
                    # Обновляем сигнал нажатия кнопки
                    self.buttons[row][j - 1].clicked.disconnect()
                    self.buttons[row][j - 1].clicked.connect(partial(self.on_button_click, row, j - 1))

        # Очищаем последний столбец
        for row in range(len(self.buttons)):
            self.buttons[row][len(self.buttons[0]) - 1] = None

        # Обновляем интерфейс после всех изменений
        self.grid_layout.update()

    def check_empty_columns(self):
        for col in range(len(self.buttons[0]) - 1, -1, -1):
            if self.is_column_empty(col):
                self.remove_column(col)

    def apply_gravity(self):
        for col in range(len(self.buttons[0])):
            empty_row = len(self.buttons) - 1
            for row in range(len(self.buttons) - 1, -1, -1):
                if self.buttons[row][col] is not None:
                    button = self.buttons[row][col]
                    if empty_row != row:
                        self.buttons[empty_row][col] = button
                        self.buttons[row][col] = None
                        self.grid_layout.removeWidget(button)
                        self.grid_layout.addWidget(button, empty_row, col)
                        button.clicked.disconnect()
                        button.clicked.connect(partial(self.on_button_click, empty_row, col))
                    empty_row -= 1

    def remove_empty_columns(self):
        for col in range(len(self.buttons[0]) - 1, -1, -1):
            if self.is_column_empty(col):
                self.remove_column(col)

    def play_sound_effect(self):
        self.sound_effect = QMediaPlayer(self)
        self.sound_effect.setMedia(QMediaContent(QUrl.fromLocalFile("da.wav")))
        self.sound_effect.play()

    def find_adjacent_buttons(self, color, row, col, group, visited=None):
        if visited is None:
            visited = set()

        if (
            row < 0 or row >= len(self.buttons) or
            col < 0 or col >= len(self.buttons[0]) or
            (row, col) in visited or
            self.buttons[row][col] is None or
            self.buttons[row][col].palette().button().color().name() != color
        ):
            return

        visited.add((row, col))
        group.add((row, col))

        self.find_adjacent_buttons(color, row + 1, col, group, visited)
        self.find_adjacent_buttons(color, row - 1, col, group, visited)
        self.find_adjacent_buttons(color, row, col + 1, group, visited)
        self.find_adjacent_buttons(color, row, col - 1, group, visited)

    def update_time(self):
        if self.first_click:
            self.game_time = self.game_time.addSecs(1)
            self.time_label.setText(f'Время: {self.game_time.toString("mm:ss")}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec_())


