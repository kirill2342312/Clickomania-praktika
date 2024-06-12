from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QStackedWidget, QHBoxLayout, QSizePolicy, QCheckBox, QMessageBox
from PyQt5.QtCore import QTimer, QTime, pyqtSignal, QThread, QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import random
import sys
from functools import partial

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.sound_effect = None
        self.volume_enabled = True

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel("Настройки")
        label.setStyleSheet("font-size: 24pt;")
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(label)

        volume_label = QLabel("Звук")
        layout.addWidget(volume_label)
        volume_label.setStyleSheet("font-size: 18pt;")

        self.volume_checkbox = QCheckBox("Включить звук")
        self.volume_checkbox.setChecked(True)
        self.volume_checkbox.setStyleSheet("font-size: 18pt;")
        layout.addWidget(self.volume_checkbox)

        self.setLayout(layout)

        self.volume_checkbox.stateChanged.connect(self.toggle_volume)

    def toggle_volume(self):
        self.volume_enabled = not self.volume_enabled
        if self.sound_effect:
            if self.volume_enabled:
                self.sound_effect.setVolume(100)
            else:
                self.sound_effect.setVolume(0)

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

class GuideWidget(QWidget):
    returnToMainMenu = pyqtSignal()  # Добавляем сигнал

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel("Руководство")
        label.setStyleSheet("font-size: 24pt;")
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(label)

        guide_text = QLabel(
            "Игра Кликомания - это головоломка. В этой игре есть стакан с кубиками разных цветов, "
            "а задача этой игры состоит в том, что нужно удалять эти группы кубиков одного цвета, нажимая на них. "
            "Когда группа кубиков удаляется, кубики, находящиеся выше, падают вниз. "
            "Цель игры - очистить весь стакан или удалить как можно больше кубиков и набрать максимальное количество очков."
        )
        guide_text.setStyleSheet("font-size: 18pt;")
        guide_text.setWordWrap(True)
        layout.addWidget(guide_text)

        back_button = QPushButton('Вернуться в главное меню')
        back_button.clicked.connect(self.return_to_main_menu)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def return_to_main_menu(self):
        self.returnToMainMenu.emit()

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Кликомания')
        self.setFixedSize(600, 600)

        self.sound_effect = QMediaPlayer(self)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.main_menu_widget = QWidget()
        layout = QVBoxLayout()

        game_label = QLabel('Кликомания')
        game_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        game_label.setStyleSheet("font-size: 36pt;")
        layout.addWidget(game_label)

        play_button = QPushButton('Играть')
        play_button.clicked.connect(self.play_game)
        layout.addWidget(play_button)

        settings_button = QPushButton('Настройки')
        settings_button.clicked.connect(self.show_settings)
        layout.addWidget(settings_button)

        guide_button = QPushButton('Руководство')
        guide_button.clicked.connect(self.show_guide)
        layout.addWidget(guide_button)

        exit_button = QPushButton('Выход')
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)

        layout.setAlignment(Qt.AlignHCenter)

        self.main_menu_widget.setLayout(layout)
        self.central_widget.addWidget(self.main_menu_widget)

        self.settings_widget = SettingsWidget()
        self.settings_widget.sound_effect = self.sound_effect
        back_button = QPushButton('Вернуться в главное меню')
        back_button.clicked.connect(self.show_main_menu)
        self.settings_widget.layout().addWidget(back_button)
        self.central_widget.addWidget(self.settings_widget)

        self.guide_widget = GuideWidget()
        self.guide_widget.returnToMainMenu.connect(self.show_main_menu)
        self.central_widget.addWidget(self.guide_widget)

    def play_game(self):
        self.game_widget = ClickomaniaGame(sound_effect=self.sound_effect)
        self.game_widget.returnToMainMenu.connect(self.show_main_menu)
        self.central_widget.addWidget(self.game_widget)
        self.central_widget.setCurrentWidget(self.game_widget)

    def show_settings(self):
        self.central_widget.setCurrentWidget(self.settings_widget)

    def show_guide(self):  # Метод для показа руководства
        self.central_widget.setCurrentWidget(self.guide_widget)

    def show_main_menu(self):
        self.central_widget.setCurrentWidget(self.main_menu_widget)

    def play_game(self):
        self.game_widget = ClickomaniaGame(sound_effect=self.sound_effect)
        self.game_widget.returnToMainMenu.connect(self.show_main_menu)
        self.central_widget.addWidget(self.game_widget)
        self.central_widget.setCurrentWidget(self.game_widget)

    def show_settings(self):
        self.central_widget.setCurrentWidget(self.settings_widget)

    def show_guide(self):
        self.central_widget.setCurrentWidget(self.guide_widget)

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

        self.back_button = QPushButton('Вернуться в главное меню')
        self.back_button.clicked.connect(self.return_to_main_menu)
        self.button_layout.addWidget(self.back_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.game_started = False
        self.first_click = False

    def load_personal_record(self):
        try:
            with open('personal_record.txt', 'r') as f:
                self.personal_record = int(f.read())
        except FileNotFoundError:
            self.personal_record = 0

        self.personal_record_label.setText(f'Личный рекорд: {self.personal_record}')

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

    def check_game_state(self):
        # Проверка на победу
        if all(button is None for row in self.buttons for button in row):
            QTimer.singleShot(100, lambda: self.show_message("Поздравляем!", "Все кубики очищены, Вы выиграли!"))
            return

        # Проверка на поражение
        if not any(self.has_adjacent_same_color(i, j) for i in range(len(self.buttons)) for j in
                   range(len(self.buttons[i])) if self.buttons[i][j] is not None):
            QTimer.singleShot(100, lambda: self.show_message("Конец игры", "Больше нет смежных кубиков. Вы проиграли ;("))
            self.stop_game()
            return

    def has_adjacent_same_color(self, row, col):
        color = self.buttons[row][col].palette().button().color().name()
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < len(self.buttons) and 0 <= c < len(self.buttons[row]) and self.buttons[r][c] is not None:
                if self.buttons[r][c].palette().button().color().name() == color:
                    return True
        return False

    def show_message(self, title, text):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


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
                button.clicked.connect(partial(self.on_button_click, row=i, col=j))
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

            self.check_game_state() # Проверка состояния игры после удаления группы

            return True
        else:
            return False

    def remove_column(self, col):
        for row in range(len(self.buttons)):
            if self.buttons[row][col] is not None:
                self.grid_layout.removeWidget(self.buttons[row][col])
                self.buttons[row][col].deleteLater()
                self.buttons[row][col] = None

        for j in range(col + 1, len(self.buttons[0])):
            for row in range(len(self.buttons)):
                self.buttons[row][j - 1] = self.buttons[row][j]
                if self.buttons[row][j - 1] is not None:
                    self.grid_layout.removeWidget(self.buttons[row][j - 1])
                    self.grid_layout.addWidget(self.buttons[row][j - 1], row, j - 1)
                    self.buttons[row][j - 1].clicked.disconnect()
                    self.buttons[row][j - 1].clicked.connect(partial(self.on_button_click, row, j - 1))

        for row in range(len(self.buttons)):
            self.buttons[row][len(self.buttons[0]) - 1] = None

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
        if self.sound_effect.state() == QMediaPlayer.PlayingState:
            self.sound_effect.stop()

        media = QMediaContent(QUrl.fromLocalFile("sound.wav"))
        self.sound_effect.setMedia(media)
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

    def stop_game(self):
        self.timer_thread.stop()
        for row in self.buttons:
            for button in row:
                if button is not None:
                    button.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec_())
