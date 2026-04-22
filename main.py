import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from math import sqrt
from scipy.stats import pearsonr, spearmanr, shapiro, t
import threading
import json
import io
import csv
from flask import Flask, render_template_string, redirect, url_for, request, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from dash import Dash, dcc, html, Input, Output, callback_context
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# ?? ЗАМЕНИТЕ ПУТИ К ВАШИМ ФАЙЛАМ через import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_PATHS = {
    'ЭОК 1': os.path.join(BASE_DIR, "logs_Python_науч_20240623-0236.xlsx"),
    'ЭОК 2': os.path.join(BASE_DIR, "logs_Time_series _20240623-0046.xlsx"),
    'ЭОК 3': os.path.join(BASE_DIR, "logs_РКИиП_ТВиМС_1_20240623-0235.xlsx"),
    'ЭОК 4': os.path.join(BASE_DIR, "logs_ТВиМС_ИВТ_1_20240623-0234.xlsx"),
    'ЭОК 5': os.path.join(BASE_DIR, "logs_БМ_ИБCDIO_20240623-0048.xlsx"),
    'ЭОК 6': os.path.join(BASE_DIR, "logs_ВМ 1_20240623-0049.xlsx"),
    'ЭОК 7': os.path.join(BASE_DIR, "logs_ВМ2_20240623-0049.xlsx"),
    'ЭОК 8': os.path.join(BASE_DIR, "logs_ПАОС МЛиТА_20250305-1134.xlsx"),
    'ЭОК 9': os.path.join(BASE_DIR, "logs_РКИиП_ТВиМС_1_20250305-1118k.xlsx"),
    'ЭОК 10': os.path.join(BASE_DIR, "logs_ТВиМС_ИВТ_1_20250305-1119k.xlsx"),
}

# Списки студентов для курсов 9 и 10
students_to_keep_df_course9 = [
    "Абросимов Всеволод Сергеевич", "Айрапетян Давид Артакович", "Андронов Владислав Васильевич",
    "Басов Егор Дмитриевич", "Батодалаев Даши Дугарович", "Башмаков Артём Алексеевич",
    "Ведров Артем Андреевич", "Волков Владислав Михайлович", "Галеев Тимур Ренатович",
    "Данилов Ярослав Федорович", "Даудов Даниил Вахмурадович", "Емельянов Андрей Валентинович",
    "Епанчинцева Дарья Евгеньевна", "Заболоцкий Влас Витальевич", "Зайцева Анастасия Юрьевна",
    "Зайцева Евгения Александровна", "Захаров Владислав Сергеевич", "Зиганшин Михаил Радиевич",
    "Зленко Дмитрий Алексеевич", "Зникин Алексей Валерьевич", "Каханова Диана Дмитриевна",
    "Кириченко Полина Сергеевна", "Кондрашин Родион Леонидович", "Королькова Анастасия Олеговна",
    "Кочетков Иван -", "Кузин Данил Александрович", "Липатова Вера Геннадьевна",
    "Листвягов Артём Николаевич", "Литвинцев Михаил Евгеньевич", "Логвинов Виталий Владимирович",
    "Логинова Дарья Александровна", "Лужникова Виктория Ивановна", "Лященко Лея Евгеньевна",
    "Мацука Александра Сергеевна", "Мышенин Егор Максимович", "Мягкий Станислав Евгеньевич",
    "Письменный Георгий Юрьевич", "Пономарёв Александр Сергеевич", "Пылев Максим Сергеевич",
    "Ржаницына Анастасия Денисовна", "Сазанович Максим Олегович", "Сковытин Владимир Александрович",
    "Смологонов Артур Константинович", "Собенин Михаил Владимирович", "Стативко Максим Витальевич",
    "Топоров Николай Алексеевич", "Учаев Павел Сергеевич", "Федорова Марина Максимовна",
    "Филимонов Алексей Евгеньевич", "Хабибуллин Ильяс Рустамович", "Хан Вячеслав -",
    "Худышкин Станислав Дмитриевич", "Шафоростов Роман Сергеевич", "Яковлев Артём Сергеевич"
]

students_to_keep_df_course10 = [
    "Адимханов Владимир Дмитриевич", "Андриенко Захар Юрьевич", "Арсаланов Доржи Александрович",
    "Афонин Илья -", "Болонев Егор Юрьевич", "Брайнингер Иван Сергеевич", "Бученик Никита Сергеевич",
    "Вальков Антон Андреевич", "Губанов Андрей Валентинович", "Дондукова Дари Эрдэмовна",
    "Евдокимов Андрей Робертович", "Зайченко Константин Олегович", "Захматов Сергей Артёмович",
    "Кириллов Валерий Денисович", "Кустикова Ксения Александровна", "Лисихин Александр Леонидович",
    "Мандричко Никита Сергеевич", "Матлай Александр Николаевич", "Молостов Степан Викторович",
    "Морозов Михаил Викторович", "Нагаев Артур Андреевич", "Непомнящих Павел Олегович",
    "Нефёдов Илья Андреевич", "Никитин Виталий Игоревич", "Никифоров Михаил Андреевич",
    "Нимаева Ажима Базаровна", "Новикова Наталья Дмитриевна", "Новоселов Михаил Романович",
    "Пак Родион Эдуардович", "Пантелеев Григорий Дмитриевич", "Петраковский Роман Олегович",
    "Платонов Александр Александрович", "Русов Данил Дмитриевич", "Савчук Мирра Александровна",
    "Салтыков Алексей Владиславович", "Сафронов Максим Дмитриевич", "Сошнев Никита Сергеевич",
    "Тахтин Данил Сергеевич", "Тумашов Георгий Игоревич", "Укиев Шерулан Сейтбекович",
    "Филимонов Валерий Александрович", "Черненченко Тимофей Александрович", "Чумутин Евгений Олегович",
    "Шалин Никита -", "Шарыгин Владимир Алексеевич", "Шинкарев Григорий Игоревич",
    "Щирба Михаил Игоревич", "Яловкин Данил Николаевич"
]

# Группы курсов по семестрам
AUTUMN_COURSES_2023 = ['ЭОК 3', 'ЭОК 4', 'ЭОК 5', 'ЭОК 6']
SPRING_COURSES_2024 = ['ЭОК 1', 'ЭОК 2', 'ЭОК 7']
AUTUMN_COURSES_2024 = ['ЭОК 8', 'ЭОК 9', 'ЭОК 10']

# Недельные диапазоны
WEEK_RANGES = {
    'AUTUMN_2023': [
        ('2023-09-01', '2023-09-06'), ('2023-09-06', '2023-09-13'), ('2023-09-13', '2023-09-20'),
        ('2023-09-20', '2023-09-27'), ('2023-09-27', '2023-10-04'), ('2023-10-04', '2023-10-11'),
        ('2023-10-11', '2023-10-18'), ('2023-10-18', '2023-10-25'), ('2023-10-25', '2023-11-01'),
        ('2023-11-01', '2023-11-08'), ('2023-11-08', '2023-11-15'), ('2023-11-15', '2023-11-22'),
        ('2023-11-22', '2023-11-29'), ('2023-11-29', '2023-12-06'), ('2023-12-06', '2023-12-13'),
        ('2023-12-13', '2023-12-20'), ('2023-12-20', '2023-12-27'), ('2023-12-27', '2024-01-10'),
    ],
    'SPRING_2024': [
        ('2024-02-05', '2024-02-12'), ('2024-02-12', '2024-02-19'), ('2024-02-19', '2024-02-26'),
        ('2024-02-26', '2024-03-04'), ('2024-03-04', '2024-03-11'), ('2024-03-11', '2024-03-18'),
        ('2024-03-18', '2024-03-25'), ('2024-03-25', '2024-04-01'), ('2024-04-01', '2024-04-08'),
        ('2024-04-08', '2024-04-15'), ('2024-04-15', '2024-04-22'), ('2024-04-22', '2024-04-29'),
        ('2024-04-29', '2024-05-06'), ('2024-05-06', '2024-05-13'), ('2024-05-13', '2024-05-20'),
        ('2024-05-20', '2024-05-27'), ('2024-05-27', '2024-06-03'), ('2024-06-03', '2024-06-10'),
    ],
    'AUTUMN_2024': [
        ('2024-09-01', '2024-09-06'), ('2024-09-06', '2024-09-13'), ('2024-09-13', '2024-09-20'),
        ('2024-09-20', '2024-09-27'), ('2024-09-27', '2024-10-04'), ('2024-10-04', '2024-10-11'),
        ('2024-10-11', '2024-10-18'), ('2024-10-18', '2024-10-25'), ('2024-10-25', '2024-11-01'),
        ('2024-11-01', '2024-11-08'), ('2024-11-08', '2024-11-15'), ('2024-11-15', '2024-11-22'),
        ('2024-11-22', '2024-11-29'), ('2024-11-29', '2024-12-06'), ('2024-12-06', '2024-12-13'),
        ('2024-12-13', '2024-12-20'), ('2024-12-20', '2024-12-27'), ('2024-12-27', '2025-01-10')
    ]
}

# Соответствие курсов преподавателям
teacher_dict = {
    'ЭОК 1': 'Преподаватель 1', 'ЭОК 2': 'Преподаватель 1',
    'ЭОК 3': 'Преподаватель 1', 'ЭОК 4': 'Преподаватель 1',
    'ЭОК 5': 'Преподаватель 2', 'ЭОК 6': 'Преподаватель 3',
    'ЭОК 7': 'Преподаватель 3', 'ЭОК 8': 'Преподаватель 4',
    'ЭОК 9': 'Преподаватель 1', 'ЭОК 10': 'Преподаватель 1',
}

# Пароли
TEACHER_CREDENTIALS = {
    'Преподаватель 1': 'pass1',
    'Преподаватель 2': 'pass2',
    'Преподаватель 3': 'pass3',
    'Преподаватель 4': 'pass4',
    'Заведующий': 'headpass',
}

# Загрузка данных
courses = {}
for name, path in FILE_PATHS.items():
    try:
        courses[name] = pd.read_excel(path)
        print(f"Загружен {name}")
    except Exception as e:
        print(f"Ошибка загрузки {name}: {e}")
        courses[name] = pd.DataFrame()

# Стиль графиков
GRAPH_STYLE = {
    'height': 500,
    'margin': {'l': 50, 'r': 50, 'b': 100, 't': 100, 'pad': 4},
    'legend': {'orientation': 'h', 'y': -0.3, 'x': 0.5, 'xanchor': 'center'}
}

# ==================== ЦИФРОВОЙ СЛЕД (РАСШИРЕННЫЙ) ====================
logs = []
logs_lock = threading.Lock()
LOG_FILE = 'digital_footprint.json'

def save_logs_to_file():
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения логов: {e}")

def load_logs_from_file():
    global logs
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            for log in logs:
                if 'source' not in log:
                    log['source'] = 'unknown'
    except FileNotFoundError:
        logs = []
    except Exception as e:
        print(f"Ошибка загрузки логов: {e}")
        logs = []

def get_request_client_info():
    from flask import request
    try:
        ip = request.remote_addr
        user_agent = request.user_agent.string if request.user_agent else 'N/A'
        return ip, user_agent
    except RuntimeError:
        return 'N/A', 'N/A'

def log_action(user, action, details, error=False, ip=None, user_agent=None, source=None):
    if source is None:
        # Определение источника из user_agent
        if user_agent and user_agent != 'N/A':
            ua_lower = user_agent.lower()
            if any(key in ua_lower for key in ['mobile', 'android', 'iphone', 'ipad', 'phone']):
                source = 'mobile'
            else:
                source = 'web'
        else:
            source = 'unknown'
    with logs_lock:
        logs.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user': user,
            'action': action,
            'details': details,
            'error': error,
            'ip': ip or 'N/A',
            'user_agent': user_agent or 'N/A',
            'source': source
        })
        if len(logs) > 1000:
            logs.pop(0)
    save_logs_to_file()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def get_week_ranges_for_course(course_name):
    if course_name in AUTUMN_COURSES_2023:
        return WEEK_RANGES['AUTUMN_2023']
    elif course_name in SPRING_COURSES_2024:
        return WEEK_RANGES['SPRING_2024']
    elif course_name in AUTUMN_COURSES_2024:
        return WEEK_RANGES['AUTUMN_2024']
    return WEEK_RANGES['AUTUMN_2023']

def get_actual_weeks_count(df, selected_course):
    try:
        week_ranges = get_week_ranges_for_course(selected_course)
        current_date = datetime.now()
        actual_weeks = 0
        for week_num, (start_date, end_date) in enumerate(week_ranges, 1):
            end_dt = pd.to_datetime(end_date)
            if current_date >= end_dt:
                actual_weeks = week_num
            else:
                break
        if actual_weeks == 0:
            actual_weeks = len(week_ranges)
        return actual_weeks
    except Exception:
        return len(week_ranges)

def calculate_feedback_speed(df, teacher_name):
    try:
        feedback_events = [
            'Представленный ответ был оценен.', 'Пользователю поставлена оценка',
            'Отзыв просмотрен', 'Оценки экспортированы в формат XLS',
            'Таблица оценивания просмотрена', 'Форма оценивания просмотрена',
            'Quiz attempt regraded', 'Grade item updated', 'Grade item created',
            'Пользователь принял заявление о представлении работы.',
            'Рассмотрена форма подтверждения представленных ответов',
            'Страница состояния представленного ответа просмотрена'
        ]
        df_feedback = df[(df['Полное имя пользователя'] == teacher_name) & (df['Название события'].isin(feedback_events))].copy()
        if df_feedback.empty:
            return 0
        df_feedback['Время'] = pd.to_datetime(df_feedback['Время'], format="%d/%m/%y, %H:%M", errors='coerce')
        df_feedback = df_feedback.dropna(subset=['Время']).sort_values('Время')
        df_feedback['time_diff'] = df_feedback['Время'].diff()
        time_diffs = df_feedback['time_diff'][df_feedback['time_diff'] < pd.Timedelta(days=7)]
        if time_diffs.empty:
            return 0
        return time_diffs.mean().total_seconds() / 3600
    except Exception as e:
        ip, ua = get_request_client_info()
        log_action(teacher_name, "Ошибка", f"calculate_feedback_speed: {str(e)}", error=True, ip=ip, user_agent=ua)
        return 0

def calculate_session_length(df, teacher_name, selected_course, session_threshold_minutes=30):
    try:
        teacher_df = df[df['Полное имя пользователя'] == teacher_name].copy()
        if teacher_df.empty:
            return 0, {}, {}
        teacher_df['Время'] = pd.to_datetime(teacher_df['Время'], format="%d/%m/%y, %H:%M", errors='coerce')
        teacher_df = teacher_df.dropna(subset=['Время']).sort_values('Время')
        week_ranges = get_week_ranges_for_course(selected_course)
        actual_weeks_count = get_actual_weeks_count(df, selected_course)
        actual_week_ranges = week_ranges[:actual_weeks_count]
        teacher_df['time_diff'] = teacher_df['Время'].diff()
        teacher_df['new_session'] = teacher_df['time_diff'] > pd.Timedelta(minutes=session_threshold_minutes)
        teacher_df['session_id'] = teacher_df['new_session'].cumsum()
        session_durations = []
        weekly_sessions = {w: 0 for w in range(1, actual_weeks_count+1)}
        weekly_session_durations = {w: [] for w in range(1, actual_weeks_count+1)}
        for session_id in teacher_df['session_id'].unique():
            session_data = teacher_df[teacher_df['session_id'] == session_id]
            if len(session_data) > 1:
                session_start = session_data['Время'].min()
                session_end = session_data['Время'].max()
                session_duration = (session_end - session_start).total_seconds() / 60
                session_durations.append(session_duration)
                session_weeks = set()
                for week_num, (start_date, end_date) in enumerate(actual_week_ranges, 1):
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)
                    if session_start <= end_dt and session_end >= start_dt:
                        session_weeks.add(week_num)
                for week_num in session_weeks:
                    weekly_sessions[week_num] += 1
                    weekly_session_durations[week_num].append(session_duration)
        avg_session_length = np.mean(session_durations) if session_durations else 0
        return avg_session_length, weekly_sessions, weekly_session_durations
    except Exception as e:
        ip, ua = get_request_client_info()
        log_action(teacher_name, "Ошибка", f"calculate_session_length: {str(e)}", error=True, ip=ip, user_agent=ua)
        return 0, {}, {}

def calculate_pedagogical_activity_level(metrics):
    weights = {
        'weekly_activity': 0.20, 'session_length': 0.20,
        'student_engagement': 0.20, 'course_updates': 0.20, 'feedback_speed': 0.20
    }
    pedagogical_thresholds = {
        'weekly_activity': [(50,100),(30,75),(15,50),(5,25),(0,10)],
        'session_length': [(45,100),(30,80),(20,60),(10,40),(0,20)],
        'student_engagement': [(0.7,100),(0.5,80),(0.3,60),(0.1,40),(0,20)],
        'course_updates': [(10,100),(7,80),(5,60),(3,40),(0,20)],
        'feedback_speed': [(0,100),(24,80),(48,60),(72,40),(96,20)]
    }
    normalized_scores = {}
    for metric, value in metrics.items():
        if metric == 'course_updates':
            value = value / 18 if value > 0 else 0
        pedagogical_score = 0
        if metric == 'feedback_speed':
            for threshold, score in pedagogical_thresholds[metric]:
                if value <= threshold:
                    pedagogical_score = score
                    break
        else:
            for threshold, score in pedagogical_thresholds[metric]:
                if value >= threshold:
                    pedagogical_score = score
                    break
        normalized_scores[metric] = pedagogical_score
    total_score = sum(normalized_scores[m] * weights[m] for m in weights)
    if total_score >= 85:
        level = "Очень высокий"; color = "#28a745"; description = "Исключительная педагогическая активность"
    elif total_score >= 70:
        level = "Высокий"; color = "#17a2b8"; description = "Высокая педагогическая активность"
    elif total_score >= 55:
        level = "Средний"; color = "#ffc107"; description = "Умеренная педагогическая активность"
    elif total_score >= 40:
        level = "Низкий"; color = "#fd7e14"; description = "Активность требует улучшения"
    else:
        level = "Очень низкий"; color = "#dc3545"; description = "Необходимо повышение активности"
    return {'total_score': round(total_score), 'level': level, 'color': color, 'description': description, 'detailed_scores': normalized_scores}

def create_graph_with_tooltip(graph_id, figure=None, tooltip_text=""):
    if figure is None:
        figure = go.Figure().update_layout(title="Нет данных", xaxis=dict(visible=False), yaxis=dict(visible=False))
    return html.Div([
        dbc.Tooltip(tooltip_text, target=f"help-icon-{graph_id}", placement="right"),
        html.Div(style={'display': 'flex', 'align-items': 'center'}, children=[
            html.I(className="fas fa-question-circle", id=f"help-icon-{graph_id}",
                   style={'margin-right': '10px', 'cursor': 'pointer'}),
            dcc.Graph(id=graph_id, figure=figure)
        ])
    ])

# ==================== FLASK И DASH ====================
server = Flask(__name__)
server.secret_key = 'supersecretkey2025'

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, name):
        self.id = name
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    if user_id in TEACHER_CREDENTIALS:
        return User(user_id)
    return None

app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP,
                                                           'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'],
           routes_pathname_prefix='/dash/')

# ==================== LAYOUTS ====================
def home_page(current_teacher):
    semesters = ['Осенний', 'Весенний']
    teachers_list = [t for t in TEACHER_CREDENTIALS.keys() if t != 'Заведующий']
    return html.Div(style={'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'margin-bottom': '20px'}, children=[
            html.H1("Активность преподавателя и студентов в электронной среде", style={'textAlign': 'center', 'margin': '0 auto'}),
            html.Div([
                html.Span(f"Вы вошли как {current_teacher}", style={'margin-right': '15px'}),
                html.A("Выйти", href="/logout", style={'color': 'white', 'backgroundColor': '#dc3545', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'}),
                html.A("Страница преподавателя", href="/dash/teacher", style={'margin-left': '10px', 'color': 'white', 'backgroundColor': '#007BFF', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'}),
                html.A("Цифровой след", href="/dash/logs", style={'margin-left': '10px', 'color': 'white', 'backgroundColor': '#6f42c1', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'}) if current_teacher == 'Заведующий' else html.Div()
            ])
        ]),
        # Для заведующего - выбор преподавателя, для преподавателя - пустой Div
        html.Div([
            html.Label("Выберите преподавателя:", style={'font-weight': 'bold', 'margin-top': '10px'}),
            dcc.Dropdown(id='head-teacher-select', options=[{'label': t, 'value': t} for t in teachers_list],
                         value=None, placeholder="Выберите преподавателя", clearable=False,
                         style={'margin-bottom': '20px'})
        ]) if current_teacher == 'Заведующий' else html.Div(),
        html.Div([
            html.Label("Выберите семестр:", style={'font-weight': 'bold', 'margin-top': '10px'}),
            dcc.Dropdown(id='semester-dropdown', options=[{'label': s, 'value': s} for s in semesters],
                         value=semesters[0] if semesters else '', clearable=False),
            html.Label("Выберите курс:", style={'font-weight': 'bold', 'margin-top': '10px'}),
            dcc.Dropdown(id='course-dropdown', options=[], value=None, clearable=False),
        ], style={'margin-bottom': '20px'}),
        dcc.Store(id='current-teacher', data=current_teacher),
        dcc.Store(id='selected-teacher', data=current_teacher if current_teacher != 'Заведующий' else None),
        dcc.Store(id='statist-unique-students-count-store'),
        dcc.Store(id='statist-avg-activity-events-per-week-prepod-store'),
        dcc.Store(id='statist-avg-activity-events-per-week-students-store'),
        dcc.Store(id='statist-avg-session-length-store'),
        dcc.Store(id='statist-weekly-sessions-store'),
        dcc.Store(id='statist-feedback-speed-store'),
        dcc.Store(id='statist-correlation-text'),
        # Блок статистики
        html.Div(style={'margin-bottom': '20px'}, children=[
            html.H4("Статистика активности преподавателя в электронной среде:"),
            dbc.Row([
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Всего студентов", style={'color': '#6c757d', 'text-align': 'center'}),
                                           html.H3(id='main-statist-unique-students', style={'color': '#17a2b8', 'text-align': 'center'})]), width=3),
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Ср. активность преподавателя (неделя)", style={'color': '#6c757d', 'text-align': 'center'}),
                                           html.H3(id='main-statist-teacher-avg-activity', style={'color': '#fd7e14', 'text-align': 'center'})]), width=3),
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Ср. активность студентов (неделя)", style={'color': '#6c757d', 'text-align': 'center'}),
                                           html.H3(id='main-statist-students-avg-activity', style={'color': '#e83e8c', 'text-align': 'center'})]), width=3),
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Ср. длина сессии преподавателя (мин)", style={'color': '#6c757d', 'text-align': 'center'}),
                                           html.H3(id='main-statist-avg-session-length', style={'color': '#28a745', 'text-align': 'center'})]), width=3),
            ], className="g-2"),
            dbc.Row([
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Количество сессий преподавателя", style={'color': '#6c757d', 'text-align': 'center'}),
                                           html.H3(id='main-statist-total-sessions', style={'color': '#6f42c1', 'text-align': 'center'})]), width=3),
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Ср. скорость обратной связи (часы)", style={'color': '#6c757d', 'text-align': 'center'}),
                                           html.H3(id='main-statist-feedback-speed', style={'color': '#20c997', 'text-align': 'center'})]), width=3),
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Зависимость активности", style={'color': '#6c757d', 'text-align': 'center'}),
                                           html.H6(id='main-statist-correlation-text', style={'color': '#007bff', 'text-align': 'center', 'margin-top': '5px'})]), width=6),
            ], className="g-2"),
        ]),
        html.Div(style={'margin-bottom': '20px'}, children=[
            html.H4("Интегрированная оценка педагогической активности:", style={'text-align': 'center'}),
            dbc.Row([
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '20px', 'border-radius': '10px', 'text-align': 'center', 'border': '2px solid #dee2e6'},
                                 children=[html.H5("Общий уровень", style={'color': '#6c757d', 'margin-bottom': '15px'}),
                                           html.Div(id='pedagogical-activity-level', style={'fontSize': '24px', 'fontWeight': 'bold', 'margin-bottom': '10px'}),
                                           html.Div(id='pedagogical-activity-description')]), width=8, style={'margin': '0 auto'})
            ]),
        ]),
        # Все графики
        html.Div(style={'display': 'flex', 'flex-wrap': 'wrap', 'gap': '20px'}, children=[
            create_graph_with_tooltip('activity-graph', None, "Активность преподавателя по месяцам"),
            create_graph_with_tooltip('weekly-activity-graph', None, "Динамика активности преподавателя по неделям"),
            create_graph_with_tooltip('student-activity-graph', None, "Динамика активности студентов по неделям"),
            create_graph_with_tooltip('unique-student-activity-graph', None, "Количество активных уникальных студентов по неделям"),
            create_graph_with_tooltip('unique-student-resources-graph', None, "Количество используемых ресурсов по неделям"),
            create_graph_with_tooltip('forum-activity-graph', None, "Активность на форумах"),
            create_graph_with_tooltip('weekly-sessions-graph', None, "Количество и длительность сессий преподавателя"),
            create_graph_with_tooltip('component-type-pie-chart', None, "Структура курса по компонентам"),
            html.Div(style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'flex-start'}, children=[
                dcc.Dropdown(id='week-dropdown', options=[], value=1, clearable=False, style={'margin': '10px 0', 'width': '250px'}),
                create_graph_with_tooltip('weekly-teacher-activities-graph', None, "Активность преподавателя по компонентам за неделю"),
            ]),
            create_graph_with_tooltip('average-posts-weekly-graph', None, "Соотношение действий преподавателя к общим"),
            create_graph_with_tooltip('student-teacher-activity-graph', None, "Сравнение активности преподавателя и студентов"),
            create_graph_with_tooltip('hourly-activity-graph', None, "Средняя часовая активность"),
            create_graph_with_tooltip('course-updates-graph', None, "Активность обновления курса по неделям"),
        ])
    ])

def teacher_page(current_teacher):
    semesters = ['Осенний', 'Весенний']
    teachers_list = [t for t in TEACHER_CREDENTIALS.keys() if t != 'Заведующий']
    empty_fig = go.Figure()
    empty_fig.update_layout(title="Загрузка данных...", xaxis=dict(visible=False), yaxis=dict(visible=False))
    return html.Div(style={'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'margin-bottom': '20px'}, children=[
            html.H1("Страница преподавателя", style={'textAlign': 'center', 'margin': '0 auto'}),
            html.Div([
                html.Span(f"Вы вошли как {current_teacher}", style={'margin-right': '15px'}),
                html.A("Выйти", href="/logout", style={'color': 'white', 'backgroundColor': '#dc3545', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'}),
                html.A("Главная страница", href="/dash/", style={'margin-left': '10px', 'color': 'white', 'backgroundColor': '#007BFF', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'}),
                html.A("Цифровой след", href="/dash/logs", style={'margin-left': '10px', 'color': 'white', 'backgroundColor': '#6f42c1', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'}) if current_teacher == 'Заведующий' else html.Div()
            ])
        ]),
        # Для заведующего - выбор преподавателя, для преподавателя - пустой Div
        html.Div([
            html.Label("Выберите преподавателя:", style={'font-weight': 'bold', 'margin-top': '10px'}),
            dcc.Dropdown(id='head-teacher-select-page', options=[{'label': t, 'value': t} for t in teachers_list],
                         value=None, placeholder="Выберите преподавателя", clearable=False,
                         style={'margin-bottom': '20px'})
        ]) if current_teacher == 'Заведующий' else html.Div(),
        dcc.Store(id='current-teacher-teacher-page', data=current_teacher),
        dcc.Store(id='selected-teacher-page', data=current_teacher if current_teacher != 'Заведующий' else None),
        dcc.Store(id='avg-activity-store', data=0),
        dcc.Store(id='avg-student-activity-store', data=0),
        dbc.ButtonGroup([
            dbc.Button("Информационная панель", id="info-btn", n_clicks=0, color="primary"),
            dbc.Button("Дашборды", id="dashboard-btn", n_clicks=0, color="primary")
        ], style={'margin-bottom': '20px'}),
        html.Div(id='teacher-info-panel', style={'display': 'block'}),
        html.Div(id='teacher-dashboards', style={'display': 'none'}, children=[
            html.Div([
                html.Label("Выберите семестр:", style={'font-weight': 'bold', 'margin-top': '10px'}),
                dcc.Dropdown(id='semester-dropdown-teacher', options=[{'label': s, 'value': s} for s in semesters],
                             value=semesters[0] if semesters else '', clearable=False, style={'margin-bottom': '20px'})
            ]),
            html.Div(style={'margin-bottom': '20px'}, children=[
                html.H4("Статистика активности преподавателя в электронной среде:"),
                dbc.Row([
                    dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                     children=[html.H5("Количество курсов",
                                                       style={'color': '#6c757d', 'text-align': 'center'}),
                                               html.H3(id='teacher-courses-count',
                                                       style={'color': '#007bff', 'text-align': 'center'})]), width=3),
                    dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                     children=[
                                         html.H5("Всего студентов", style={'color': '#6c757d', 'text-align': 'center'}),
                                         html.H3(id='teacher-students-count',
                                                 style={'color': '#17a2b8', 'text-align': 'center'})]), width=3),
                    dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                     children=[html.H5("Ср. активность преподавателя (неделя)",
                                                       style={'color': '#6c757d', 'text-align': 'center'}),
                                               html.H3(id='teacher-avg-activity',
                                                       style={'color': '#fd7e14', 'text-align': 'center'})]), width=3),
                    dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                     children=[html.H5("Ср. активность студентов (неделя)",
                                                       style={'color': '#6c757d', 'text-align': 'center'}),
                                               html.H3(id='students-avg-activity',
                                                       style={'color': '#e83e8c', 'text-align': 'center'})]), width=3),
                ]),
            ]),
            html.Div(style={'display': 'flex', 'gap': '20px', 'flex-wrap': 'wrap'}, children=[
                create_graph_with_tooltip('activity-graph-teacher', empty_fig, "Активность по месяцам (все курсы)"),
                create_graph_with_tooltip('weekly-activity-graph-teacher', empty_fig, "Динамика по неделям (все курсы)"),
            ])
        ])
    ])

def digital_footprint_page():
    return html.Div(style={'padding': '20px'}, children=[
        html.Div(style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center', 'margin-bottom': '20px'}, children=[
            html.H1("Цифровой след действий пользователей", style={'textAlign': 'center', 'margin': '0 auto'}),
            html.Div([
                html.A("Главная страница", href="/dash/", style={'color': 'white', 'backgroundColor': '#007BFF', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'}),
                html.A("Выйти", href="/logout", style={'margin-left': '10px', 'color': 'white', 'backgroundColor': '#dc3545', 'padding': '8px 12px', 'borderRadius': '5px', 'textDecoration': 'none'})
            ])
        ]),
        html.Div([
            html.Label("Фильтр по пользователю:"),
            dcc.Dropdown(id='filter-user', multi=False, placeholder="Все", style={'width': '300px'}),
            html.Label("Фильтр по действию (содержит):", style={'margin-top': '10px'}),
            dcc.Input(id='filter-action', type='text', placeholder="Введите текст", style={'width': '300px', 'margin-bottom': '10px'}),
            html.Label("Диапазон дат:", style={'margin-top': '10px'}),
            dcc.DatePickerRange(id='filter-date-range', start_date=None, end_date=None, display_format='YYYY-MM-DD', style={'margin-bottom': '10px'}),
            html.Div([
                html.Button("Сбросить фильтры", id='reset-filters', n_clicks=0, style={'margin-right': '10px'}),
                html.Button("Экспорт в CSV", id='export-csv-btn', n_clicks=0),
            ], style={'margin-top': '10px'}),
            dcc.Download(id='download-csv')
        ], style={'margin-bottom': '20px', 'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'}),
        html.Div(id='logs-table-container')
    ])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# ==================== CALLBACKS ====================
@app.callback(
    Output('selected-teacher', 'data'),
    Input('head-teacher-select', 'value'),
    Input('current-teacher', 'data'),
    prevent_initial_call=True
)
def update_selected_teacher_for_head(head_value, current_teacher):
    if current_teacher == 'Заведующий' and head_value:
        return head_value
    return current_teacher

@app.callback(
    Output('selected-teacher-page', 'data'),
    Input('head-teacher-select-page', 'value'),
    Input('current-teacher-teacher-page', 'data'),
    prevent_initial_call=True
)
def update_selected_teacher_page_for_head(head_value, current_teacher):
    if current_teacher == 'Заведующий' and head_value:
        return head_value
    return current_teacher

@app.callback(
    Output('course-dropdown', 'options'),
    Input('semester-dropdown', 'value'),
    Input('selected-teacher', 'data')
)
def update_course_options(selected_semester, teacher_name):
    if not teacher_name:
        return []
    teacher_courses = [c for c, t in teacher_dict.items() if t == teacher_name]
    if selected_semester == 'Весенний':
        allowed = SPRING_COURSES_2024
    else:
        allowed = AUTUMN_COURSES_2023 + AUTUMN_COURSES_2024
    available = [c for c in teacher_courses if c in allowed]
    return [{'label': c, 'value': c} for c in available]

@app.callback(
    Output('course-dropdown', 'value'),
    Input('course-dropdown', 'options'),
    prevent_initial_call=True
)
def set_default_course(options):
    if options and len(options) > 0:
        return options[0]['value']
    return None

@app.callback(
    Output('week-dropdown', 'options'),
    Input('course-dropdown', 'value')
)
def update_week_dropdown(selected_course):
    if not selected_course or selected_course not in courses:
        return []
    df = courses[selected_course]
    actual_weeks = get_actual_weeks_count(df, selected_course)
    return [{'label': f'Неделя {w}', 'value': w} for w in range(1, actual_weeks + 1)]

@app.callback(
    Output('week-dropdown', 'value'),
    Input('course-dropdown', 'value'),
    prevent_initial_call=True
)
def set_default_week(selected_course):
    if selected_course and selected_course in courses:
        return 1
    return None

@app.callback(
    Output('main-statist-unique-students', 'children'),
    Output('main-statist-teacher-avg-activity', 'children'),
    Output('main-statist-students-avg-activity', 'children'),
    Output('main-statist-avg-session-length', 'children'),
    Output('main-statist-total-sessions', 'children'),
    Output('main-statist-feedback-speed', 'children'),
    Output('main-statist-correlation-text', 'children'),
    Input('course-dropdown', 'value'),
    Input('statist-unique-students-count-store', 'data'),
    Input('statist-avg-activity-events-per-week-prepod-store', 'data'),
    Input('statist-avg-activity-events-per-week-students-store', 'data'),
    Input('statist-avg-session-length-store', 'data'),
    Input('statist-weekly-sessions-store', 'data'),
    Input('statist-feedback-speed-store', 'data'),
    Input('statist-correlation-text', 'data'),
)
def update_main_stats(selected_course, total_students, avg_teacher_weekly,
                      avg_students_weekly, avg_session_length, weekly_sessions_data, feedback_speed, correlation_text):
    if not selected_course:
        return 0, 0, 0, 0, 0, 0, 0
    total_sessions = sum(weekly_sessions_data.values()) if weekly_sessions_data else 0
    return (
        total_students,
        f"{avg_teacher_weekly:.1f}",
        f"{avg_students_weekly:.1f}",
        f"{avg_session_length:.1f}",
        f"{total_sessions}",
        f"{feedback_speed:.1f} ч",
        f"{correlation_text}",
    )

# ==================== ГЛАВНЫЙ CALLBACK СО ВСЕМИ ГРАФИКАМИ ====================
@app.callback(
    [Output('activity-graph', 'figure'), Output('weekly-activity-graph', 'figure'),
     Output('student-activity-graph', 'figure'), Output('unique-student-activity-graph', 'figure'),
     Output('unique-student-resources-graph', 'figure'), Output('forum-activity-graph', 'figure'),
     Output('weekly-sessions-graph', 'figure'), Output('weekly-teacher-activities-graph', 'figure'),
     Output('average-posts-weekly-graph', 'figure'), Output('student-teacher-activity-graph', 'figure'),
     Output('component-type-pie-chart', 'figure'), Output('hourly-activity-graph', 'figure'),
     Output('course-updates-graph', 'figure'),
     Output('statist-unique-students-count-store', 'data'),
     Output('statist-avg-activity-events-per-week-prepod-store', 'data'),
     Output('statist-avg-activity-events-per-week-students-store', 'data'),
     Output('statist-avg-session-length-store', 'data'),
     Output('statist-weekly-sessions-store', 'data'),
     Output('statist-feedback-speed-store', 'data'),
     Output('statist-correlation-text', 'data'),
     Output('pedagogical-activity-level', 'children'),
     Output('pedagogical-activity-description', 'children')],
    [Input('course-dropdown', 'value'), Input('week-dropdown', 'value'), Input('selected-teacher', 'data'),
     Input('current-teacher', 'data')]  # Добавлен current-teacher
)
def update_main_graphs(selected_course, selected_week, teacher_name, current_user):
    ip, ua = get_request_client_info()
    try:
        if not teacher_name or not selected_course or selected_course not in courses:
            empty = go.Figure().update_layout(title="Нет данных для отображения")
            return [empty] * 13 + [0] * 7 + ["", "", ""]

        # Логируем действие от имени текущего пользователя (заведующий или сам преподаватель)
        log_action(current_user, "Просмотр курса", f"Преподаватель: {teacher_name}, Курс: {selected_course}, неделя: {selected_week}", ip=ip, user_agent=ua)

        df = courses[selected_course].copy()
        df['Время'] = pd.to_datetime(df['Время'], format="%d/%m/%y, %H:%M", errors='coerce')

        actual_weeks = get_actual_weeks_count(df, selected_course)
        week_ranges = get_week_ranges_for_course(selected_course)
        actual_week_ranges = week_ranges[:actual_weeks]

        df_teacher = df[df['Полное имя пользователя'] == teacher_name]
        df_students = df[df['Полное имя пользователя'] != teacher_name]
        if selected_course == 'ЭОК 9':
            df_students = df_students[df_students['Полное имя пользователя'].isin(students_to_keep_df_course9)]
        elif selected_course == 'ЭОК 10':
            df_students = df_students[df_students['Полное имя пользователя'].isin(students_to_keep_df_course10)]

        # Месячная активность
        if selected_course in SPRING_COURSES_2024:
            df_month = df_teacher[(df_teacher['Время'].dt.month >= 2) & (df_teacher['Время'].dt.month <= 5)]
            month_order = [2, 3, 4, 5]
        else:
            df_month = df_teacher[(df_teacher['Время'].dt.month >= 9) | (df_teacher['Время'].dt.month == 1)]
            month_order = [9, 10, 11, 12, 1]

        if not df_month.empty:
            df_month['Месяц'] = df_month['Время'].dt.month
            monthly = df_month.groupby('Месяц').size().reset_index(name='Количество событий')
            month_map = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май',
                         9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
            monthly['Месяц'] = monthly['Месяц'].map(month_map)
            monthly = monthly[monthly['Месяц'].notnull()]
            monthly['Месяц'] = pd.Categorical(monthly['Месяц'], categories=[month_map[m] for m in month_order if m in month_map], ordered=True)
            monthly = monthly.sort_values('Месяц')
            activity_fig = go.Figure(data=[go.Pie(labels=monthly['Месяц'], values=monthly['Количество событий'], hole=0.3, sort=False)])
        else:
            activity_fig = go.Figure().update_layout(title="Нет данных за семестр")
        activity_fig.update_layout(title='Активность преподавателя по месяцам', **GRAPH_STYLE)

        # Недельная активность преподавателя
        weekly_teacher = []
        for s, e in actual_week_ranges:
            cnt = len(df_teacher.query("@s <= Время <= @e"))
            weekly_teacher.append(cnt)
        events_teacher = pd.DataFrame({'Неделя': range(1, actual_weeks + 1), 'Количество событий': weekly_teacher})
        avg_teacher = events_teacher['Количество событий'].mean()
        weekly_activity_fig = go.Figure(data=[go.Bar(x=events_teacher['Неделя'], y=events_teacher['Количество событий'], name='Активность преподавателя')])
        weekly_activity_fig.add_trace(go.Scatter(x=events_teacher['Неделя'], y=[avg_teacher] * len(events_teacher),
                                                 mode='lines', name='Средняя активность',
                                                 line=dict(color='red', dash='dash')))
        weekly_activity_fig.update_layout(title='Динамика активности преподавателя по неделям',
                                          yaxis_title='Количество событий', xaxis_title='Неделя', **GRAPH_STYLE)

        # Активность студентов
        weekly_students = []
        for s, e in actual_week_ranges:
            cnt = len(df_students.query("@s <= Время <= @e"))
            weekly_students.append(cnt)
        events_students = pd.DataFrame({'Неделя': range(1, actual_weeks + 1), 'Количество событий': weekly_students})
        avg_students = events_students['Количество событий'].mean()
        student_activity_fig = go.Figure(data=[go.Bar(x=events_students['Неделя'], y=events_students['Количество событий'], name='Активность студентов')])
        student_activity_fig.add_trace(go.Scatter(x=events_students['Неделя'], y=[avg_students] * len(events_students),
                                                  mode='lines', name='Средняя активность',
                                                  line=dict(color='red', dash='dash')))
        student_activity_fig.update_layout(title='Динамика активности студентов по неделям',
                                           yaxis_title='Количество событий', xaxis_title='Неделя', **GRAPH_STYLE)

        # Уникальные активные студенты
        unique_students_weekly = []
        for s, e in actual_week_ranges:
            uniq = df_students.query("@s <= Время <= @e")['Полное имя пользователя'].nunique()
            unique_students_weekly.append(uniq)
        uniq_df = pd.DataFrame({'Неделя': range(1, actual_weeks + 1), 'Количество активных уникальных студентов': unique_students_weekly})
        total_unique = df_students['Полное имя пользователя'].nunique()
        uniq_fig = go.Figure(data=[go.Bar(x=uniq_df['Неделя'], y=uniq_df['Количество активных уникальных студентов'], name='Активные студенты')])
        uniq_fig.add_trace(go.Scatter(x=uniq_df['Неделя'], y=[total_unique] * len(uniq_df), mode='lines', name='Всего студентов',
                                      line=dict(color='green', dash='dash')))
        uniq_fig.add_trace(go.Scatter(x=uniq_df['Неделя'], y=[uniq_df['Количество активных уникальных студентов'].mean()] * len(uniq_df),
                                      mode='lines', name='Средняя активность', line=dict(color='red', dash='dash')))
        uniq_fig.update_layout(title='Динамика количества активных студентов по неделям',
                               yaxis_title='Количество уникальных студентов', xaxis_title='Неделя', **GRAPH_STYLE)

        # Уникальные ресурсы
        resources_weekly = []
        for s, e in actual_week_ranges:
            uniq = df_students.query("@s <= Время <= @e")['Контекст события'].nunique()
            resources_weekly.append(uniq)
        res_df = pd.DataFrame({'Неделя': range(1, actual_weeks + 1), 'Количество уникальных элементов': resources_weekly})
        res_fig = px.bar(res_df, x='Неделя', y='Количество уникальных элементов', title='Динамика используемых ресурсов по неделям')
        res_fig.update_traces(name='Количество ресурсов')
        res_fig.update_layout(**GRAPH_STYLE)

        # Форум
        df_forum = df[df['Компонент'].str.contains('Форум', case=False, na=False)]
        if not df_forum.empty:
            forum_posts = len(df_forum)
            teacher_forum = len(df_forum[df_forum['Полное имя пользователя'] == teacher_name])
            student_forum = len(df_forum[df_forum['Полное имя пользователя'] != teacher_name])
            participants = df_forum['Полное имя пользователя'].nunique()
            discussions = df_forum['Контекст события'].nunique()
            forum_fig = go.Figure(data=[go.Bar(x=['Все сообщения', 'Преподаватель', 'Студенты'],
                                               y=[forum_posts, teacher_forum, student_forum],
                                               marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
                                               name='Количество сообщений')])
            forum_fig.add_annotation(x=1, y=max(forum_posts, teacher_forum, student_forum) * 1.1,
                                     text=f"Участников: {participants} | Обсуждений: {discussions}", showarrow=False)
            forum_fig.update_layout(title='Активность на форумах курса', **GRAPH_STYLE)
        else:
            forum_fig = go.Figure().update_layout(title="Нет данных о форумах", **GRAPH_STYLE)

        # Сессии преподавателя
        avg_sess_len, weekly_sessions, weekly_sess_durations = calculate_session_length(df, teacher_name, selected_course)
        sess_fig = go.Figure()
        if weekly_sess_durations:
            weeks_sorted = sorted([w for w in weekly_sess_durations.keys() if w <= actual_weeks])
            counts = [weekly_sessions.get(w, 0) for w in weeks_sorted]
            avg_durs = [np.mean(weekly_sess_durations[w]) if weekly_sess_durations[w] else 0 for w in weeks_sorted]
            hover_texts = [f"Неделя {w}<br>Сессий: {weekly_sessions.get(w, 0)}<br>Средняя длит: {avg_durs[i]:.1f} мин<br><br>Длительности сессий:<br>" +
                           "<br>".join([f"Сессия {j+1}: {d:.1f} мин" for j, d in enumerate(weekly_sess_durations[w])])
                           for i, w in enumerate(weeks_sorted)]
            sess_fig.add_trace(go.Bar(x=weeks_sorted, y=counts, name='Количество сессий', hovertext=hover_texts, hoverinfo='text', marker_color='#6f42c1'))
            sess_fig.add_trace(go.Scatter(x=weeks_sorted, y=avg_durs, mode='lines+markers', name='Средняя длительность (мин)',
                                          line=dict(color='#fd7e14', width=3), yaxis='y2'))
            sess_fig.update_layout(yaxis2=dict(title='Длительность (мин)', overlaying='y', side='right'),
                                   title='Количество и длительность сессий преподавателя по неделям', **GRAPH_STYLE)
        else:
            sess_fig.update_layout(title="Нет данных о сессиях преподавателя", **GRAPH_STYLE)

        # Активность преподавателя по компонентам за выбранную неделю
        teacher_weekly_activities = []
        for i, (s, e) in enumerate(actual_week_ranges, 1):
            temp = df_teacher.query("@s <= Время <= @e")
            temp['Неделя'] = i
            teacher_weekly_activities.append(temp)
        teacher_weeks = pd.concat(teacher_weekly_activities) if teacher_weekly_activities else pd.DataFrame()
        bad_components = ['Система', 'Отчет по пользователю', 'Отчет по оценкам', 'Журнал событий',
                          'Комментарии к ответам', 'Отчет о деятельности', 'Обзорный отчет', 'Ответ в виде файла', 'Корзина']
        if not teacher_weeks.empty:
            teacher_weeks = teacher_weeks[~teacher_weeks['Компонент'].isin(bad_components)]
            week_data = teacher_weeks[teacher_weeks['Неделя'] == selected_week]
            if not week_data.empty:
                comp_counts = week_data['Компонент'].value_counts().reset_index()
                comp_counts.columns = ['Компонент', 'Количество активностей']
                comp_fig = px.bar(comp_counts, x='Компонент', y='Количество активностей',
                                  title=f'Количество активностей преподавателя по компонентам (Неделя {selected_week})')
            else:
                comp_fig = go.Figure().update_layout(title=f'Нет активности на неделе {selected_week}')
        else:
            comp_fig = go.Figure().update_layout(title='Нет данных об активности преподавателя')
        comp_fig.update_layout(**GRAPH_STYLE)

        # Соотношение действий
        if not teacher_weeks.empty:
            total_actions_teacher = teacher_weeks.groupby('Неделя').size().reindex(range(1, actual_weeks+1), fill_value=0)
        else:
            total_actions_teacher = pd.Series([0]*actual_weeks, index=range(1, actual_weeks+1))
        student_weeks_list = []
        for i, (s, e) in enumerate(actual_week_ranges, 1):
            tmp = df_students.query("@s <= Время <= @e")
            tmp['Неделя'] = i
            student_weeks_list.append(tmp)
        student_weeks = pd.concat(student_weeks_list) if student_weeks_list else pd.DataFrame()
        if not student_weeks.empty:
            total_actions_students = student_weeks.groupby('Неделя').size().reindex(range(1, actual_weeks+1), fill_value=0)
        else:
            total_actions_students = pd.Series([0]*actual_weeks, index=range(1, actual_weeks+1))
        ratio = total_actions_teacher / (total_actions_teacher + total_actions_students).replace(0, np.nan)
        ratio_df = pd.DataFrame({'Неделя': range(1, actual_weeks+1), 'Соотношение действий преподавателя': ratio.values})
        ratio_fig = px.bar(ratio_df, x='Неделя', y='Соотношение действий преподавателя',
                           title='Динамика соотношения действий преподавателя внутри курса к общему количеству действий всех пользователей')
        ratio_fig.update_layout(**GRAPH_STYLE)

        # Сравнение активности
        compare_fig = go.Figure()
        compare_fig.add_trace(go.Scatter(x=events_teacher['Неделя'], y=events_teacher['Количество событий'],
                                         mode='lines+markers', name='Активность преподавателя', line=dict(color='blue')))
        compare_fig.add_trace(go.Scatter(x=events_students['Неделя'], y=events_students['Количество событий'],
                                         mode='lines+markers', name='Активность студентов', line=dict(color='red')))
        compare_fig.update_layout(title='Сравнение активности студентов и преподавателя по неделям',
                                  xaxis_title='Неделя', yaxis_title='Количество событий', **GRAPH_STYLE)

        # Компоненты курса
        component_counts = df['Компонент'].value_counts()
        filtered_counts = component_counts[~component_counts.index.isin(bad_components)]
        pie_fig = go.Figure(data=[go.Pie(labels=filtered_counts.index, values=filtered_counts.values,
                                         hoverinfo='label+percent', textinfo='label+percent',
                                         pull=[0.1]*len(filtered_counts))])
        pie_fig.update_traces(textposition='inside')
        pie_fig.update_layout(title='Количество компонентов разного типа в курсе', showlegend=True, **GRAPH_STYLE)

        # Часовая активность
        df['Час'] = df['Время'].dt.hour
        hourly = df.groupby(['Час', 'Полное имя пользователя']).size().reset_index(name='Кол-во')
        teacher_hourly = hourly[hourly['Полное имя пользователя'] == teacher_name].groupby('Час')['Кол-во'].mean().reset_index()
        student_hourly = hourly[hourly['Полное имя пользователя'] != teacher_name].groupby('Час')['Кол-во'].mean().reset_index()
        hour_fig = go.Figure()
        if not teacher_hourly.empty:
            hour_fig.add_trace(go.Bar(x=teacher_hourly['Час'], y=teacher_hourly['Кол-во'], name='Активность преподавателя', marker_color='blue'))
        if not student_hourly.empty:
            hour_fig.add_trace(go.Bar(x=student_hourly['Час'], y=student_hourly['Кол-во'], name='Активность студентов', marker_color='red'))
        hour_fig.update_layout(title='Средняя часовая активность преподавателя и студентов', xaxis_title='Часы',
                               yaxis_title='Среднее количество событий', **GRAPH_STYLE)
        hour_fig.update_xaxes(tickmode='linear', dtick=1)

        # Обновления курса
        update_events = ['Модуль курса обновлен', 'Курс обновлен', 'Выполнение элемента курса обновлено',
                         'Событие календаря обновлено', 'Grade item updated', 'Question updated', 'Раздел курса обновлен',
                         'Представленный ответ обновлен.', 'Состояние представленного ответа было обновлено.',
                         'Сообщение обновлено', 'Quiz attempt regraded']
        updates = df[df['Название события'].isin(update_events)]
        weekly_updates = []
        for i, (s, e) in enumerate(actual_week_ranges, 1):
            cnt = len(updates.query("@s <= Время <= @e"))
            weekly_updates.append(cnt)
        updates_df = pd.DataFrame({'Неделя': range(1, actual_weeks+1), 'Количество обновлений': weekly_updates})
        total_updates = updates_df['Количество обновлений'].sum()
        avg_updates = updates_df['Количество обновлений'].mean()
        updates_fig = go.Figure(data=[go.Bar(x=updates_df['Неделя'], y=updates_df['Количество обновлений'], name='Обновления', marker_color='#17a2b8')])
        updates_fig.add_trace(go.Scatter(x=updates_df['Неделя'], y=[avg_updates]*len(updates_df), mode='lines',
                                         name=f'Среднее: {avg_updates:.1f}', line=dict(color='red', dash='dash', width=2)))
        max_updates = max(updates_df['Количество обновлений']) if max(updates_df['Количество обновлений'])>0 else 1
        updates_fig.add_annotation(x=0.5, y=max_updates*1.15, text=f"Всего обновлений за семестр: {total_updates}",
                                   showarrow=False, font=dict(size=14), bgcolor="lightblue", bordercolor="black",
                                   borderwidth=1, xref="paper", xanchor="center")
        updates_fig.update_layout(title='Активность обновления курса по неделям', **GRAPH_STYLE)

        # Корреляция
        df_act = pd.DataFrame({'Преподаватель': events_teacher['Количество событий'], 'Студенты': events_students['Количество событий']})
        if len(df_act) > 2:
            stat_t, p_t = shapiro(df_act['Преподаватель'])
            stat_s, p_s = shapiro(df_act['Студенты'])
            if p_t < 0.05 or p_s < 0.05:
                corr, p_corr = spearmanr(df_act['Преподаватель'], df_act['Студенты'])
            else:
                corr, p_corr = pearsonr(df_act['Преподаватель'], df_act['Студенты'])
            if p_corr < 0.05:
                if abs(corr) < 0.3: interp = "слабая"
                elif abs(corr) >= 0.7: interp = "сильная"
                else: interp = "умеренная"
                direction = "прямая" if corr > 0 else "обратная"
                corr_text = f"{interp} {direction} зависимость ({corr:.3f})"
            else:
                corr_text = "Статистически не значима"
        else:
            corr = 0
            corr_text = "Недостаточно данных"

        # Педагогическая активность
        metrics = {
            'weekly_activity': avg_teacher,
            'session_length': avg_sess_len,
            'student_engagement': abs(corr) if 'corr' in locals() else 0,
            'course_updates': total_updates,
            'feedback_speed': calculate_feedback_speed(df, teacher_name)
        }
        ped = calculate_pedagogical_activity_level(metrics)
        ped_level = html.Div([html.H4("Уровень педагогической активности:", style={'margin-bottom': '10px'}),
                              dbc.Badge(ped['level'], color=ped['color'], style={'fontSize': '20px', 'padding': '10px'})])
        ped_desc = html.Div([html.P(ped['description'], style={'fontStyle': 'italic', 'margin-top': '10px'})])

        return (activity_fig, weekly_activity_fig, student_activity_fig, uniq_fig, res_fig, forum_fig,
                sess_fig, comp_fig, ratio_fig, compare_fig, pie_fig, hour_fig, updates_fig,
                total_unique, avg_teacher, avg_students, avg_sess_len, weekly_sessions, metrics['feedback_speed'],
                corr_text, ped_level, ped_desc)
    except Exception as e:
        log_action(current_user, "Ошибка в графиках", f"{str(e)}", error=True, ip=ip, user_agent=ua)
        empty = go.Figure().update_layout(title="Ошибка загрузки данных")
        return [empty] * 13 + [0] * 7 + ["", "", ""]

# ==================== CALLBACKS ДЛЯ СТРАНИЦЫ ПРЕПОДАВАТЕЛЯ ====================
@app.callback(
    [Output('activity-graph-teacher', 'figure'), Output('weekly-activity-graph-teacher', 'figure'),
     Output('avg-activity-store', 'data'), Output('avg-student-activity-store', 'data')],
    [Input('semester-dropdown-teacher', 'value'), Input('selected-teacher-page', 'data'),
     Input('current-teacher-teacher-page', 'data')]  # Добавлен current-teacher
)
def update_teacher_dashboards(selected_semester, teacher_name, current_user):
    ip, ua = get_request_client_info()
    try:
        if not teacher_name:
            empty = go.Figure().update_layout(title="Нет данных")
            return empty, empty, 0, 0

        log_action(current_user, "Просмотр дашбордов преподавателя", f"Преподаватель: {teacher_name}, Семестр: {selected_semester}", ip=ip, user_agent=ua)

        teacher_courses = [c for c, t in teacher_dict.items() if t == teacher_name]
        if selected_semester == 'Весенний':
            allowed = SPRING_COURSES_2024
            week_ranges = WEEK_RANGES['SPRING_2024']
            month_order = [2, 3, 4, 5]
        else:
            allowed = AUTUMN_COURSES_2023 + AUTUMN_COURSES_2024
            week_ranges = WEEK_RANGES['AUTUMN_2024']
            month_order = [9, 10, 11, 12, 1]
        teacher_courses = [c for c in teacher_courses if c in allowed]
        if not teacher_courses:
            empty = go.Figure().update_layout(title="Нет курсов в этом семестре")
            return empty, empty, 0, 0

        total_weeks = len(week_ranges)
        total_teacher_weekly = [0] * total_weeks
        total_student_weekly = [0] * total_weeks
        monthly_teacher_events = []

        for course in teacher_courses:
            df_course = courses[course]
            if df_course.empty:
                continue

            df_course['Время'] = pd.to_datetime(df_course['Время'], format="%d/%m/%y, %H:%M", errors='coerce')
            df_teacher_course = df_course[df_course['Полное имя пользователя'] == teacher_name]
            df_students_course = df_course[df_course['Полное имя пользователя'] != teacher_name]

            if selected_semester == 'Весенний':
                df_month = df_teacher_course[(df_teacher_course['Время'].dt.month >= 2) & (df_teacher_course['Время'].dt.month <= 5)]
            else:
                df_month = df_teacher_course[(df_teacher_course['Время'].dt.month >= 9) | (df_teacher_course['Время'].dt.month == 1)]
            if not df_month.empty:
                df_month['Месяц'] = df_month['Время'].dt.month
                monthly_teacher_events.extend(df_month['Месяц'].tolist())

            week_ranges_course = get_week_ranges_for_course(course)
            actual_weeks_course = get_actual_weeks_count(df_course, course)
            for week_idx in range(min(actual_weeks_course, total_weeks)):
                s, e = week_ranges_course[week_idx]
                cnt_teacher = len(df_teacher_course.query("@s <= Время <= @e"))
                total_teacher_weekly[week_idx] += cnt_teacher
                cnt_student = len(df_students_course.query("@s <= Время <= @e"))
                total_student_weekly[week_idx] += cnt_student

        if sum(total_teacher_weekly) == 0:
            empty = go.Figure().update_layout(title="Нет активности преподавателя")
            return empty, empty, 0, 0

        if monthly_teacher_events:
            monthly_counts = pd.Series(monthly_teacher_events).value_counts().reset_index()
            monthly_counts.columns = ['Месяц', 'Количество событий']
            month_map = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май',
                         9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
            monthly_counts['Месяц'] = monthly_counts['Месяц'].map(month_map)
            monthly_counts = monthly_counts[monthly_counts['Месяц'].notnull()]
            month_labels = [month_map[m] for m in month_order if m in month_map]
            monthly_counts['Месяц'] = pd.Categorical(monthly_counts['Месяц'], categories=month_labels, ordered=True)
            monthly_counts = monthly_counts.sort_values('Месяц')
            activity_fig = go.Figure(data=[go.Pie(labels=monthly_counts['Месяц'], values=monthly_counts['Количество событий'], hole=0.3)])
        else:
            activity_fig = go.Figure().update_layout(title="Нет данных по месяцам")
        activity_fig.update_layout(title='Активность преподавателя по месяцам (все курсы)', **GRAPH_STYLE)

        weeks = list(range(1, total_weeks + 1))
        avg_teacher = np.mean(total_teacher_weekly)
        weekly_fig = go.Figure(data=[go.Bar(x=weeks, y=total_teacher_weekly, name='Активность преподавателя')])
        weekly_fig.add_trace(go.Scatter(x=weeks, y=[avg_teacher] * total_weeks,
                                        mode='lines', name='Средняя активность',
                                        line=dict(color='red', dash='dash')))
        weekly_fig.update_layout(title='Динамика активности преподавателя по неделям (все курсы)',
                                 yaxis_title='Суммарное количество событий', xaxis_title='Неделя семестра',
                                 xaxis=dict(tickmode='linear', dtick=1), **GRAPH_STYLE)

        avg_student = np.mean(total_student_weekly) if total_student_weekly else 0
        return activity_fig, weekly_fig, avg_teacher, avg_student

    except Exception as e:
        log_action(current_user, "Ошибка в дашбордах преподавателя", f"{str(e)}", error=True, ip=ip, user_agent=ua)
        empty = go.Figure().update_layout(title="Ошибка загрузки")
        return empty, empty, 0, 0

@app.callback(
    [Output('teacher-info-panel', 'style'), Output('teacher-dashboards', 'style'),
     Output('info-btn', 'className'), Output('dashboard-btn', 'className')],
    [Input('info-btn', 'n_clicks'), Input('dashboard-btn', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_panels(info_clicks, dashboard_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return {'display': 'block'}, {'display': 'none'}, "btn btn-primary active", "btn btn-primary"
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'info-btn':
        return {'display': 'block'}, {'display': 'none'}, "btn btn-primary active", "btn btn-primary"
    else:
        return {'display': 'none'}, {'display': 'block'}, "btn btn-primary", "btn btn-primary active"

@app.callback(
    Output('teacher-info-panel', 'children'),
    [Input('selected-teacher-page', 'data'), Input('avg-activity-store', 'data'),
     Input('avg-student-activity-store', 'data'), Input('current-teacher-teacher-page', 'data')]  # Добавлен current-teacher
)
def update_teacher_info(teacher_name, avg_teacher, avg_student, current_user):
    ip, ua = get_request_client_info()
    try:
        if not teacher_name:
            return html.Div("Нет данных")
        # Логируем просмотр информации
        log_action(current_user, "Просмотр информации преподавателя", f"Преподаватель: {teacher_name}", ip=ip, user_agent=ua)

        teacher_info = {
            'Преподаватель 1': {'avatar': 'https://img.icons8.com/color/96/000000/user-male-circle--v1.png',
                                'position': 'Преподаватель информатики и вычислительной техники',
                                'education': 'Кандидат педагогических наук', 'experience': '9 лет преподавания',
                                'placeOfWork': 'Кафедра прикладной математики и анализа данных, доцент',
                                'phone': '+7 (123) 456-78-90', 'email': 'prep1@university.edu'},
            'Преподаватель 2': {'avatar': 'https://img.icons8.com/color/96/000000/user-female-circle--v1.png',
                                'position': 'Преподаватель математики',
                                'education': 'Кандидат педагогических наук', 'experience': '31 год преподавания',
                                'placeOfWork': 'Кафедра фундаментального естественнонаучного образования, доцент',
                                'phone': '+7 (234) 567-89-01', 'email': 'prep2@university.edu'},
            'Преподаватель 3': {'avatar': 'https://img.icons8.com/color/96/000000/user-female-circle--v1.png',
                                'position': 'Преподаватель математического анализа и аналитической геометрии',
                                'education': 'Кандидат физико-математических наук', 'experience': '12 лет преподавания',
                                'placeOfWork': 'Кафедра прикладной математики и анализа данных, доцент',
                                'phone': '+7 (345) 678-90-12', 'email': 'prep3@university.edu'},
            'Преподаватель 4': {'avatar': 'https://img.icons8.com/color/96/000000/user-female-circle--v1.png',
                                'position': 'Преподаватель математической логики и теории алгоритмов',
                                'education': 'Доктор педагогических наук', 'experience': '21 год преподавания',
                                'placeOfWork': 'Кафедра прикладной математики и анализа данных, профессор',
                                'phone': '+7 (456) 789-01-23', 'email': 'prep4@university.edu'}
        }
        info = teacher_info.get(teacher_name, {})
        teacher_courses = [c for c, t in teacher_dict.items() if t == teacher_name]
        total_students = 0
        for course in teacher_courses:
            df = courses[course]
            if df.empty:
                continue
            if course in ['ЭОК 9']:
                students = df[df['Полное имя пользователя'].isin(students_to_keep_df_course9)][
                    'Полное имя пользователя'].nunique()
            elif course in ['ЭОК 10']:
                students = df[df['Полное имя пользователя'].isin(students_to_keep_df_course10)][
                    'Полное имя пользователя'].nunique()
            else:
                students = df[df['Полное имя пользователя'] != teacher_name]['Полное имя пользователя'].nunique()
            total_students += students

        courses_count = len(teacher_courses)
        avg_teacher_val = float(avg_teacher) if avg_teacher is not None else 0
        avg_student_val = float(avg_student) if avg_student is not None else 0

        return html.Div([
            html.Div(style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '20px'}, children=[
                html.Img(src=info.get('avatar', ''),
                         style={'width': '100px', 'height': '100px', 'border-radius': '50%', 'margin-right': '20px'}),
                html.Div([html.H3(teacher_name), html.P(info.get('position', '')), html.P(info.get('education', '')),
                          html.P(f"Опыт преподавания: {info.get('experience', '')}")])
            ]),
            html.Div([html.H4("Контактная информация:"), dbc.Row([
                dbc.Col(html.Div([html.I(className="fas fa-phone"), html.P(info.get('phone', ''),
                                                                           style={'display': 'inline-block',
                                                                                  'margin-left': '10px'})]), width=6),
                dbc.Col(html.Div([html.I(className="fas fa-envelope"), html.P(info.get('email', ''),
                                                                              style={'display': 'inline-block',
                                                                                     'margin-left': '10px'})]), width=6)
            ])]),
            html.Div([html.H4("Место работы:"), html.P(info.get('placeOfWork', ''))]),
            html.Div([html.H4("Статистика активности преподавателя в электронной среде:"), dbc.Row([
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Количество курсов"),
                                           html.H3(courses_count, style={'color': '#007bff'})]), width=3),
                dbc.Col(html.Div(style={'background': '#f8f9fa', 'padding': '15px', 'border-radius': '5px'},
                                 children=[html.H5("Всего студентов"),
                                           html.H3(total_students, style={'color': '#17a2b8'})]), width=3),
            ])]),
            html.Div([html.H4("Список курсов:"), html.Ul([html.Li(course) for course in teacher_courses])])
        ])
    except Exception as e:
        log_action(current_user, "Ошибка загрузки информации преподавателя", str(e), error=True, ip=ip, user_agent=ua)
        return html.Div("Ошибка загрузки данных")

@app.callback(
    [Output('teacher-courses-count', 'children'), Output('teacher-students-count', 'children'),
     Output('teacher-avg-activity', 'children'), Output('students-avg-activity', 'children')],
    [Input('selected-teacher-page', 'data'), Input('semester-dropdown-teacher', 'value'),
     Input('avg-activity-store', 'data'), Input('avg-student-activity-store', 'data')]
)
def update_teacher_stats(teacher_name, semester, avg_teacher, avg_student):
    if not teacher_name:
        return 0, 0, "0.0", "0.0"

    teacher_courses = [c for c, t in teacher_dict.items() if t == teacher_name]
    if semester == 'Весенний':
        teacher_courses = [c for c in teacher_courses if c in SPRING_COURSES_2024]
    else:
        teacher_courses = [c for c in teacher_courses if c in AUTUMN_COURSES_2023 + AUTUMN_COURSES_2024]

    total_students = 0
    for course in teacher_courses:
        df = courses[course]
        if df.empty:
            continue
        if course == 'ЭОК 9':
            students = df[df['Полное имя пользователя'].isin(students_to_keep_df_course9)]['Полное имя пользователя'].nunique()
        elif course == 'ЭОК 10':
            students = df[df['Полное имя пользователя'].isin(students_to_keep_df_course10)]['Полное имя пользователя'].nunique()
        else:
            students = df[df['Полное имя пользователя'] != teacher_name]['Полное имя пользователя'].nunique()
        total_students += students

    courses_count = len(teacher_courses)
    avg_teacher_val = float(avg_teacher) if avg_teacher is not None else 0
    avg_student_val = float(avg_student) if avg_student is not None else 0

    return courses_count, total_students, f"{avg_teacher_val:.1f}", f"{avg_student_val:.1f}"

# ==================== CALLBACKS ДЛЯ СТРАНИЦЫ ЦИФРОВОГО СЛЕДА ====================
@app.callback(
    [Output('logs-table-container', 'children'),
     Output('filter-user', 'options'),
     Output('filter-user', 'value')],
    [Input('filter-user', 'value'),
     Input('filter-action', 'value'),
     Input('filter-date-range', 'start_date'),
     Input('filter-date-range', 'end_date'),
     Input('reset-filters', 'n_clicks')]
)
def update_logs_table(selected_user, action_contains, start_date, end_date, reset_clicks):
    ctx = callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'reset-filters.n_clicks':
        selected_user = None
        action_contains = ''
        start_date = None
        end_date = None

    # Блокировка при копировании списка логов
    with logs_lock:
        logs_copy = logs.copy()

    filtered = logs_copy
    if selected_user:
        filtered = [l for l in filtered if l['user'] == selected_user]
    if action_contains:
        filtered = [l for l in filtered if action_contains.lower() in l['action'].lower() or action_contains.lower() in l['details'].lower()]
    if start_date:
        start_ts = datetime.strptime(start_date, '%Y-%m-%d')
        filtered = [l for l in filtered if datetime.strptime(l['timestamp'], '%Y-%m-%d %H:%M:%S') >= start_ts]
    if end_date:
        end_ts = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        filtered = [l for l in filtered if datetime.strptime(l['timestamp'], '%Y-%m-%d %H:%M:%S') <= end_ts]

    # Пользователи также из копии
    users = sorted(set(l['user'] for l in logs_copy))
    user_options = [{'label': u, 'value': u} for u in users]

    if not filtered:
        table = html.Div("Нет записей, соответствующих фильтрам", style={'textAlign': 'center', 'padding': '20px'})
    else:
        table = dbc.Table(
            [
                html.Thead(html.Tr([html.Th("Время"), html.Th("Пользователь"), html.Th("Действие"), html.Th("Детали"), html.Th("IP"), html.Th("Источник"), html.Th("Ошибка")])),
                html.Tbody([
                    html.Tr([
                        html.Td(l['timestamp']),
                        html.Td(l['user']),
                        html.Td(l['action']),
                        html.Td(l['details']),
                        html.Td(l['ip']),
                        html.Td(l['source']),
                        html.Td("Да" if l['error'] else "Нет")
                    ]) for l in reversed(filtered)
                ])
            ],
            bordered=True, hover=True, striped=True, responsive=True, style={'margin-top': '20px'}
        )
    return table, user_options, selected_user


@app.callback(
    Output('download-csv', 'data'),
    Input('export-csv-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_logs_csv(n_clicks):
    if n_clicks > 0:
        # Блокировка при копировании списка логов
        with logs_lock:
            logs_copy = logs.copy()
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['timestamp', 'user', 'action', 'details', 'error', 'ip', 'source'])
        writer.writeheader()
        for log in logs_copy:
            writer.writerow({k: log.get(k, '') for k in ['timestamp', 'user', 'action', 'details', 'error', 'ip', 'source']})
        csv_content = output.getvalue()
        return dict(content=csv_content, filename=f"digital_footprint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    return None

# ==================== FLASK МАРШРУТЫ ====================
@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        teacher = request.form.get('teacher')
        password = request.form.get('password')
        ip, ua = get_request_client_info()
        if teacher in TEACHER_CREDENTIALS and TEACHER_CREDENTIALS[teacher] == password:
            user = User(teacher)
            login_user(user)
            session['user_id'] = teacher
            log_action(teacher, "Вход в систему", "Успешный вход", ip=ip, user_agent=ua)
            return redirect('/dash/')
        else:
            log_action(teacher if teacher else "Unknown", "Ошибка входа", "Неверный логин или пароль", error=True, ip=ip, user_agent=ua)
            return render_template_string(login_page() + "<div class='alert alert-danger'>Неверный логин или пароль</div>")
    return render_template_string(login_page())

def login_page():
    return '''
    <!doctype html>
    <html>
    <head><title>Вход</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>
    <div class="container mt-5">
        <h2>Вход в систему анализа активности</h2>
        <form method="post">
            <div class="form-group">
                <label>Пользователь</label>
                <select name="teacher" class="form-control" required>
                    <option value="">-- Выберите --</option>
                    <option value="Преподаватель 1">Преподаватель 1</option>
                    <option value="Преподаватель 2">Преподаватель 2</option>
                    <option value="Преподаватель 3">Преподаватель 3</option>
                    <option value="Преподаватель 4">Преподаватель 4</option>
                    <option value="Заведующий">Заведующий</option>
                </select>
            </div>
            <div class="form-group">
                <label>Пароль</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Войти</button>
        </form>
    </div>
    </body>
    </html>
    '''

@server.route('/logout')
@login_required
def logout():
    user = session.get('user_id', 'Unknown')
    ip, ua = get_request_client_info()
    log_action(user, "Выход из системы", "Пользователь вышел", ip=ip, user_agent=ua)
    logout_user()
    session.pop('user_id', None)
    return redirect('/login')

@server.route('/')
def root():
    if 'user_id' in session:
        return redirect('/dash/')
    return redirect('/login')

@server.route('/admin/clear_logs', methods=['POST'])
def admin_clear_logs():
    secret_token = request.args.get('token')
    if secret_token != 'Tutor':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    with logs_lock:
        logs.clear()
    save_logs_to_file()
    ip, ua = get_request_client_info()
    log_action("Система", "Очистка лога", "Лог очищен администратором", ip=ip, user_agent=ua)
    return jsonify({'status': 'success', 'message': 'Logs cleared'})

# ==================== РЕНДЕРИНГ СТРАНИЦ ПО URL ====================
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def render_page_from_url(pathname):
    from flask import session as flask_session
    teacher = flask_session.get('user_id')
    if not teacher:
        return html.Div("Доступ запрещён. Пожалуйста, войдите.", style={'padding': '20px', 'textAlign': 'center'})
    if pathname == '/dash/teacher':
        return teacher_page(teacher)
    elif pathname == '/dash/logs':
        if teacher != 'Заведующий':
            return html.Div("Доступ запрещён. Только для заведующего.", style={'padding': '20px', 'textAlign': 'center'})
        return digital_footprint_page()
    else:
        return home_page(teacher)

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    load_logs_from_file()
    server.run(debug=True, host='0.0.0.0', port=5000)
