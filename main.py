import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from math import factorial, exp, e
from scipy.special import lambertw
import matplotlib
import webbrowser
from PIL import Image, ImageTk
import sympy as sp
import matplotlib.animation as animation
import pandas as pd  # ← ВАЖНО: добавлен отсутствующий импорт


# Настройка бэкенда для matplotlib
matplotlib.use('TkAgg')


class SeriesAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_variables()
        self.create_widgets()
        self.create_menu()
        self.update_plots()  # ← вызывать только после создания всех компонентов

    def setup_window(self):
        """Настройка основного окна"""
        self.root.title("Advanced Series Analyzer")
        self.root.geometry("1400x1000")
        self.root.configure(bg='#2e2e2e')
        self.root.minsize(1200, 800)

        # Иконка приложения
        try:
            self.root.iconbitmap('icon.ico')  # Положите файл icon.ico в ту же папку
        except:
            pass

    def create_variables(self):
        """Инициализация переменных"""
        # Параметры по умолчанию
        self.x_value = 0.2
        self.n_terms = 20
        self.x_min = -1 / e
        self.x_max = 1 / e
        self.animation_running = False
        self.dark_mode = True
        self.current_theme = 'dark'

        # Цветовые схемы
        self.themes = {
            'dark': {
                'bg': '#2e2e2e',
                'fg': 'white',
                'plot_bg': '#2e2e2e',
                'grid': '#4a4a4a',
                'accent': '#4fc3f7',
                'secondary': '#ffb74d'
            },
            'light': {
                'bg': '#f5f5f5',
                'fg': 'black',
                'plot_bg': 'white',
                'grid': '#e0e0e0',
                'accent': '#1976d2',
                'secondary': '#ff9800'
            }
        }

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        self.setup_styles()
        self.create_header()
        self.create_control_panel()
        self.create_info_panel()
        self.create_plot_frame()
        self.create_status_bar()

    def setup_styles(self):
        """Настройка стилей элементов"""
        style = ttk.Style()
        style.theme_use('clam')

        # Общие стили
        style.configure('.',
                        background=self.themes[self.current_theme]['bg'],
                        foreground=self.themes[self.current_theme]['fg'])

        # Стиль для кнопок
        style.configure('TButton',
                        background=self.themes[self.current_theme]['accent'],
                        foreground='black',
                        font=('Helvetica', 10),
                        padding=5)

        # Стиль для заголовков
        style.configure('Header.TLabel',
                        font=('Helvetica', 12, 'bold'),
                        foreground=self.themes[self.current_theme]['accent'])

        # Стиль для информационной панели
        style.configure('Info.TFrame',
                        background='#37474f' if self.dark_mode else '#e3f2fd')
        style.configure('Info.TLabel',
                        background='#37474f' if self.dark_mode else '#e3f2fd',
                        foreground='white' if self.dark_mode else 'black')

    def create_header(self):
        """Создание заголовка приложения"""
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        # Логотип и название
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(side=tk.LEFT)

        try:
            logo_img = Image.open("logo.png").resize((40, 40))
            self.logo = ImageTk.PhotoImage(logo_img)
            ttk.Label(logo_frame, image=self.logo).pack(side=tk.LEFT, padx=5)
        except:
            pass

        ttk.Label(logo_frame,
                  text="Advanced Series Analyzer",
                  font=('Helvetica', 16, 'bold'),
                  foreground=self.themes[self.current_theme]['accent']).pack(side=tk.LEFT)

        # Уравнение ряда
        eq_frame = ttk.Frame(header_frame)
        eq_frame.pack(side=tk.LEFT, padx=20)
        ttk.Label(eq_frame,
                  text=r"$\sum_{n=1}^{\infty} \frac{n^n x^n}{n!}$",
                  font=('Helvetica', 14),
                  foreground=self.themes[self.current_theme]['secondary']).pack()

    def create_control_panel(self):
        """Создание панели управления"""
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # Левая панель (основные параметры)
        control_left = ttk.Frame(control_frame)
        control_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        ttk.Label(control_left, text="ПАРАМЕТРЫ РЯДА", style='Header.TLabel').grid(row=0, column=0, columnspan=3,
                                                                                   sticky=tk.W)

        # Слайдер для значения x
        ttk.Label(control_left, text="Значение x:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.x_slider = ttk.Scale(control_left, from_=-0.367, to=0.367,
                                  command=lambda e: self.slider_changed('x'))
        self.x_slider.set(self.x_value)
        self.x_slider.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.x_value_label = ttk.Label(control_left, text=f"{self.x_value:.4f}")
        self.x_value_label.grid(row=1, column=2, padx=5, pady=2)

        # Слайдер для количества членов ряда
        ttk.Label(control_left, text="Членов ряда (n):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.n_slider = ttk.Scale(control_left, from_=1, to=100,
                                  command=lambda e: self.slider_changed('n'))
        self.n_slider.set(self.n_terms)
        self.n_slider.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        self.n_value_label = ttk.Label(control_left, text=f"{self.n_terms}")
        self.n_value_label.grid(row=2, column=2, padx=5, pady=2)

        # Кнопка анимации
        self.animate_button = ttk.Button(control_left, text="▶ Анимация", command=self.toggle_animation)
        self.animate_button.grid(row=3, column=1, pady=5, sticky=tk.EW)

        # Правая панель (дополнительные параметры)
        control_right = ttk.Frame(control_frame)
        control_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        ttk.Label(control_right, text="ДОПОЛНИТЕЛЬНО", style='Header.TLabel').grid(row=0, column=0, columnspan=3,
                                                                                   sticky=tk.W)

        # Диапазон x
        ttk.Label(control_right, text="Диапазон x:").grid(row=1, column=0, sticky=tk.W, pady=2)
        range_frame = ttk.Frame(control_right)
        range_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)

        ttk.Label(range_frame, text="От:").pack(side=tk.LEFT)
        self.x_min_entry = ttk.Entry(range_frame, width=8)
        self.x_min_entry.insert(0, f"{self.x_min:.4f}")
        self.x_min_entry.pack(side=tk.LEFT, padx=2)

        ttk.Label(range_frame, text="До:").pack(side=tk.LEFT)
        self.x_max_entry = ttk.Entry(range_frame, width=8)
        self.x_max_entry.insert(0, f"{self.x_max:.4f}")
        self.x_max_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(range_frame, text="Применить", command=self.update_range).pack(side=tk.LEFT, padx=5)

        # Максимальное количество членов
        ttk.Label(control_right, text="Макс. членов:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_n_entry = ttk.Entry(control_right, width=8)
        self.max_n_entry.insert(0, "50")
        self.max_n_entry.grid(row=2, column=1, sticky=tk.W, pady=2)

        # Кнопки экспорта
        export_frame = ttk.Frame(control_right)
        export_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Button(export_frame, text="Экспорт данных", command=self.export_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="Экспорт графика", command=self.save_plots).pack(side=tk.LEFT, padx=2)

    def create_info_panel(self):
        """Создание информационной панели"""
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        info_container = ttk.Frame(info_frame, style='Info.TFrame')
        info_container.pack(fill=tk.X, ipady=5)

        # Текущие значения
        ttk.Label(info_container, text="Текущее значение ряда:", style='Info.TLabel').pack(side=tk.LEFT, padx=10)
        self.current_value_label = ttk.Label(info_container, text="", style='Info.TLabel', width=20)
        self.current_value_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(info_container, text="Аналитическое значение:", style='Info.TLabel').pack(side=tk.LEFT, padx=10)
        self.analytical_value_label = ttk.Label(info_container, text="", style='Info.TLabel', width=20)
        self.analytical_value_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(info_container, text="Погрешность:", style='Info.TLabel').pack(side=tk.LEFT, padx=10)
        self.error_label = ttk.Label(info_container, text="", style='Info.TLabel', width=15)
        self.error_label.pack(side=tk.LEFT, padx=5)

        # Информация о сходимости
        ttk.Label(info_container, text="Радиус сходимости: ±1/e ≈ ±0.3679", style='Info.TLabel').pack(side=tk.RIGHT,
                                                                                                      padx=10)

    def create_plot_frame(self):
        """Создание области для графиков"""
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Создание графиков
        self.figure = plt.Figure(figsize=(10, 8), dpi=100, facecolor=self.themes[self.current_theme]['plot_bg'])
        self.figure.subplots_adjust(hspace=0.4)

        # График 1: Сходимость частичных сумм
        self.ax1 = self.figure.add_subplot(311, facecolor=self.themes[self.current_theme]['plot_bg'])
        self.ax1.set_title('Сходимость частичных сумм', color=self.themes[self.current_theme]['fg'])
        self.ax1.set_xlabel('Количество членов ряда (n)', color=self.themes[self.current_theme]['fg'])
        self.ax1.set_ylabel('Значение суммы', color=self.themes[self.current_theme]['fg'])
        self.ax1.tick_params(colors=self.themes[self.current_theme]['fg'])
        self.ax1.grid(True, color=self.themes[self.current_theme]['grid'])

        # График 2: Аппроксимация ряда
        self.ax2 = self.figure.add_subplot(312, facecolor=self.themes[self.current_theme]['plot_bg'])
        self.ax2.set_title('Аппроксимация ряда', color=self.themes[self.current_theme]['fg'])
        self.ax2.set_xlabel('x', color=self.themes[self.current_theme]['fg'])
        self.ax2.set_ylabel('f(x)', color=self.themes[self.current_theme]['fg'])
        self.ax2.tick_params(colors=self.themes[self.current_theme]['fg'])
        self.ax2.grid(True, color=self.themes[self.current_theme]['grid'])

        # График 3: Точность аппроксимации
        self.ax3 = self.figure.add_subplot(313, facecolor=self.themes[self.current_theme]['plot_bg'])
        self.ax3.set_title('Точность аппроксимации', color=self.themes[self.current_theme]['fg'])
        self.ax3.set_xlabel('x', color=self.themes[self.current_theme]['fg'])
        self.ax3.set_ylabel('Абсолютная ошибка (log scale)', color=self.themes[self.current_theme]['fg'])
        self.ax3.tick_params(colors=self.themes[self.current_theme]['fg'])
        self.ax3.grid(True, color=self.themes[self.current_theme]['grid'])

        # Встраивание графиков в Tkinter с панелью инструментов
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Добавляем панель инструментов matplotlib
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """Создание строки состояния"""
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")

        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(status_bar, textvariable=self.status_var).pack(side=tk.LEFT)
        ttk.Label(status_bar, text="Advanced Series Analyzer v1.0").pack(side=tk.RIGHT)

    def create_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Сохранить графики", command=self.save_plots)
        file_menu.add_command(label="Экспорт данных", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню Настройки
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Сменить тему", command=self.toggle_theme)
        settings_menu.add_command(label="Настройки графиков", command=self.graph_settings)
        menubar.add_cascade(label="Настройки", menu=settings_menu)

        # Меню Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Справка", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.about)
        menubar.add_cascade(label="Помощь", menu=help_menu)

        self.root.config(menu=menubar)

    def analytical_solution(self, x):
        """Аналитическое решение с использованием W-функции Ламберта."""
        if x == 0:
            return 0
        try:
            return -lambertw(-x).real
        except:
            return float('nan')

    def partial_sum(self, x, n_terms):
        """Вычисление частичной суммы ряда."""
        if abs(x) > 1 / e:
            return float('nan')

        total = 0.0
        term = x  # Первый член (n=1)

        for n in range(1, n_terms + 1):
            if n == 1:
                term = x
            else:
                term = term * x * (1 - 1 / n) ** (n - 1)
            total += term
        return total

    def slider_changed(self, slider_type):
        """Обработчик изменения слайдеров"""
        if slider_type == 'x':
            self.x_value = float(self.x_slider.get())
            if hasattr(self, 'x_value_label'):
                self.x_value_label.config(text=f"{self.x_value:.4f}")
        elif slider_type == 'n':
            self.n_terms = int(float(self.n_slider.get()))
            if hasattr(self, 'n_value_label'):
                self.n_value_label.config(text=f"{self.n_terms}")

        if hasattr(self, 'current_value_label'):  # чтобы не обновлять графики до полной инициализации
            self.update_plots()

    def update_range(self):
        """Обновление диапазона для графиков"""
        try:
            self.x_min = float(self.x_min_entry.get())
            self.x_max = float(self.x_max_entry.get())
            self.update_plots()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение диапазона")

    def update_plots(self):
        """Обновление всех графиков"""
        self.status_var.set("Обновление графиков...")
        self.root.update()

        # Проверка на сходимость
        if abs(self.x_value) > 1 / e:
            messagebox.showwarning("Предупреждение",
                                   f"Ряд расходится при |x| > 1/e ≈ 0.3679\n"
                                   f"Текущее x = {self.x_value:.4f}")

        # Вычисление значений
        analytical_val = self.analytical_solution(self.x_value)
        partial_val = self.partial_sum(self.x_value, self.n_terms)
        error = abs(partial_val - analytical_val) if abs(self.x_value) <= 1 / e else float('nan')

        # Обновление информационных меток
        self.current_value_label.config(text=f"{partial_val:.6f}" if not np.isnan(partial_val) else "расходится")
        self.analytical_value_label.config(text=f"{analytical_val:.6f}" if not np.isnan(analytical_val) else "N/A")
        self.error_label.config(text=f"{error:.2e}" if not np.isnan(error) else "N/A")

        # Очистка графиков
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        # Настройка цветов графиков
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_facecolor(self.themes[self.current_theme]['plot_bg'])
            ax.tick_params(colors=self.themes[self.current_theme]['fg'])
            ax.xaxis.label.set_color(self.themes[self.current_theme]['fg'])
            ax.yaxis.label.set_color(self.themes[self.current_theme]['fg'])
            ax.title.set_color(self.themes[self.current_theme]['fg'])
            ax.grid(True, color=self.themes[self.current_theme]['grid'])

        # График 1: Сходимость частичных сумм
        try:
            max_n = int(self.max_n_entry.get())
        except:
            max_n = 50

        n_vals = np.arange(1, max_n + 1)
        partial_sums = [self.partial_sum(self.x_value, n) for n in n_vals]

        self.ax1.plot(n_vals, partial_sums, 'o-', color=self.themes[self.current_theme]['accent'],
                      label='Частичная сумма')

        if abs(self.x_value) <= 1 / e:
            self.ax1.axhline(y=analytical_val, color=self.themes[self.current_theme]['secondary'],
                             linestyle='--', label='Аналитическое решение')

        self.ax1.set_title(f'Сходимость при x = {self.x_value:.4f}')
        self.ax1.set_xlabel('Количество членов ряда (n)')
        self.ax1.set_ylabel('Значение суммы')
        self.ax1.legend()

        # График 2: Аппроксимация ряда
        x_vals = np.linspace(self.x_min, self.x_max, 400)
        analytical_vals = [self.analytical_solution(x) if abs(x) <= 1 / e else float('nan') for x in x_vals]

        self.ax2.plot(x_vals, analytical_vals, '-', color=self.themes[self.current_theme]['secondary'],
                      label='Аналитическое решение', linewidth=2)

        n_terms_list = [5, 10, 20, self.n_terms] if self.n_terms > 20 else [5, 10, 15, self.n_terms]
        colors = ['#81c784', '#4fc3f7', '#ba68c8', '#ff8a65']

        for i, n_terms in enumerate(n_terms_list):
            sum_vals = [self.partial_sum(x, n_terms) if abs(x) <= 1 / e else float('nan') for x in x_vals]
            self.ax2.plot(x_vals, sum_vals, '--', color=colors[i], label=f'n={n_terms}')

        # Отметки радиуса сходимости
        self.ax2.axvline(x=-1 / e, color='r', linestyle=':', alpha=0.5)
        self.ax2.axvline(x=1 / e, color='r', linestyle=':', alpha=0.5)

        self.ax2.set_title('Аппроксимация ряда')
        self.ax2.set_xlabel('x')
        self.ax2.set_ylabel('f(x)')
        self.ax2.legend()

        # График 3: Точность аппроксимации
        for i, n_terms in enumerate(n_terms_list):
            errors = []
            for x in x_vals:
                if abs(x) <= 1 / e:
                    s = self.partial_sum(x, n_terms)
                    a = self.analytical_solution(x)
                    errors.append(abs(s - a))
                else:
                    errors.append(float('nan'))
            self.ax3.semilogy(x_vals, errors, color=colors[i], label=f'n={n_terms}')

        self.ax3.set_title('Точность аппроксимации')
        self.ax3.set_xlabel('x')
        self.ax3.set_ylabel('Абсолютная ошибка (log scale)')
        self.ax3.legend()

        # Обновление холста
        self.figure.tight_layout(rect=[0, 0, 1, 0.97])
        self.canvas.draw()

        self.status_var.set("Готово")

    def save_plots(self):
        """Сохраняет текущие графики в файл"""
        filetypes = [('PNG Image', '*.png'), ('JPEG Image', '*.jpg'), ('PDF Document', '*.pdf'), ('All Files', '*.*')]
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)

        if filename:
            try:
                self.figure.savefig(filename, dpi=300)
                self.status_var.set(f"Графики сохранены в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить графики: {str(e)}")
                self.status_var.set("Ошибка при сохранении")

    def export_data(self):
        """Экспорт данных в CSV файл"""
        filetypes = [('CSV File', '*.csv'), ('Text File', '*.txt'), ('All Files', '*.*')]
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=filetypes)

        if filename:
            try:
                x_vals = np.linspace(self.x_min, self.x_max, 100)
                data = {
                    'x': x_vals,
                    'analytical': [self.analytical_solution(x) if abs(x) <= 1 / e else float('nan') for x in x_vals],
                    f'n={self.n_terms}': [self.partial_sum(x, self.n_terms) if abs(x) <= 1 / e else float('nan') for x
                                          in x_vals]
                }

                import pandas as pd
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)

                self.status_var.set(f"Данные экспортированы в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")
                self.status_var.set("Ошибка при экспорте")

    def toggle_animation(self):
        """Включение/выключение анимации"""
        if not self.animation_running:
            self.start_animation()
        else:
            self.stop_animation()

    def start_animation(self):
        """Запуск анимации сходимости"""
        self.animation_running = True
        self.animate_button.config(text="■ Стоп")

        # Сохраняем текущие значения
        original_x = self.x_value
        original_n = self.n_terms

        # Анимация изменения x
        x_values = np.linspace(-0.36, 0.36, 50)

        def update_frame(i):
            self.x_value = x_values[i]
            self.x_slider.set(self.x_value)
            self.x_value_label.config(text=f"{self.x_value:.4f}")
            self.update_plots()
            if i == len(x_values) - 1:
                self.root.after(1000, lambda: reverse_animation(len(x_values) - 1))

        def reverse_animation(i):
            if i >= 0 and self.animation_running:
                self.x_value = x_values[i]
                self.x_slider.set(self.x_value)
                self.x_value_label.config(text=f"{self.x_value:.4f}")
                self.update_plots()
                if i > 0:
                    self.root.after(50, lambda: reverse_animation(i - 1))
                else:
                    self.root.after(1000, lambda: animate_n(1))

        def animate_n(n):
            if n <= 50 and self.animation_running:
                self.n_terms = n
                self.n_slider.set(n)
                self.n_value_label.config(text=f"{n}")
                self.update_plots()
                if n < 50:
                    self.root.after(50, lambda: animate_n(n + 1))
                else:
                    self.root.after(1000, self.stop_animation)

        # Запускаем анимацию
        for i in range(len(x_values)):
            if self.animation_running:
                self.root.after(50 * i, lambda i=i: update_frame(i))

    def stop_animation(self):
        """Остановка анимации"""
        self.animation_running = False
        self.animate_button.config(text="▶ Анимация")
        self.status_var.set("Анимация остановлена")

    def toggle_theme(self):
        """Переключение между темной и светлой темами"""
        self.dark_mode = not self.dark_mode
        self.current_theme = 'dark' if self.dark_mode else 'light'
        self.setup_styles()
        self.update_plots()
        self.root.configure(bg=self.themes[self.current_theme]['bg'])

    def graph_settings(self):
        """Настройки графиков"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки графиков")
        settings_window.geometry("400x300")

        ttk.Label(settings_window, text="Размер шрифта:").pack(pady=5)
        font_size = ttk.Combobox(settings_window, values=["8", "10", "12", "14", "16"])
        font_size.pack(pady=5)
        font_size.set("10")

        ttk.Label(settings_window, text="Толщина линий:").pack(pady=5)
        line_width = ttk.Scale(settings_window, from_=1, to=5)
        line_width.pack(pady=5)
        line_width.set(2)

        def apply_settings():
            try:
                plt.rcParams['font.size'] = int(font_size.get())
                plt.rcParams['lines.linewidth'] = float(line_width.get())
                self.update_plots()
                settings_window.destroy()
            except:
                messagebox.showerror("Ошибка", "Некорректные значения параметров")

        ttk.Button(settings_window, text="Применить", command=apply_settings).pack(pady=10)

    def show_help(self):
        """Отображение справки"""
        help_text = """
        Advanced Series Analyzer

        Это приложение позволяет анализировать сходимость степенного ряда:

        ∑ (n=1 to ∞) (n^n * x^n) / n!

        Основные функции:
        1. Исследование сходимости при различных x
        2. Анализ точности аппроксимации
        3. Визуализация результатов

        Используйте слайдеры для изменения параметров:
        - Значение x: от -1/e до 1/e (радиус сходимости)
        - Количество членов ряда: от 1 до 100

        Графики:
        1. Сходимость частичных сумм
        2. Аппроксимация ряда
        3. Точность аппроксимации
        """
        messagebox.showinfo("Справка", help_text)

    def about(self):
        """О программе"""
        about_text = """
        Advanced Series Analyzer
        Версия 1.0

        Разработано для анализа степенных рядов

        Автор: @L1TV1N4
        Дата: 2025

        Используемые технологии:
        - Python 3
        - Tkinter
        - Matplotlib
        - NumPy
        - SciPy
        """
        messagebox.showinfo("О программе", about_text)

        # Открытие ссылки в браузере
        try:
            webbrowser.open("https://github.com/yourusername/series-analyzer")
        except:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = SeriesAnalyzerApp(root)
    root.mainloop()