#!/bin/sh

# Название проекта
PROJECT_NAME="log_analyzer"

# Создание структуры папок
mkdir -p $PROJECT_NAME
cd $PROJECT_NAME

mkdir -p logs reports templates tests

# Создание файлов
touch log_analyzer.py config.py utils.py
touch tests/test_log_analyzer.py
touch templates/report.html
touch Makefile README.md pyproject.toml setup.cfg

# Заполнение README.md
cat <<EOL > README.md
# $PROJECT_NAME

## Описание

Проект для анализа логов nginx и генерации отчетов в формате HTML.

## Установка

Инструкции по установке проекта.

## Использование

Примеры использования проекта.

## Тестирование

Инструкции по запуску тестов.
EOL

# Заполнение Makefile
cat <<EOL > Makefile
.PHONY: test lint format

test:
\tpytest

lint:
\tflake8 log_analyzer.py tests/

format:
\tblack log_analyzer.py tests/
EOL

# Заполнение pyproject.toml
cat <<EOL > pyproject.toml
[tool.black]
line-length = 88

[tool.isort]
profile = "black"
EOL

# Заполнение setup.cfg
cat <<EOL > setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
EOL

# Пример шаблона HTML отчета
cat <<EOL > templates/report.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Report</title>
</head>
<body>
    <h1>Log Analysis Report</h1>
    <table>
        <thead>
            <tr>
                <th>URL</th>
                <th>Count</th>
                <th>Sum</th>
                <th>Max</th>
                <th>Avg</th>
                <th>Median</th>
            </tr>
        </thead>
        <tbody>
            <!-- Report data will be inserted here -->
        </tbody>
    </table>
</body>
</html>
EOL

echo "Структура проекта $PROJECT_NAME создана успешно!"
