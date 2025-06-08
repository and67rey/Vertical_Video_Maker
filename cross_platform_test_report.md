
# 🌍 Отчёт о кроссплатформенном тестировании

## Цель

Подтвердить, что проект **Vertical Video Maker** корректно работает на основных платформах: **Windows**, **Linux (Ubuntu)**, **macOS**.

## Методика

* Для тестирования использовались:
  * `ubuntu-latest` и `macos-latest` — в CI на **GitHub Actions**
  * Windows 10 — локально в среде разработки **PyCharm**
  * Тестовый фреймворк: `pytest` + `pytest-cov` + `pytest-html`
* Покрытие кода: HTML-отчёт по `pytest-cov`

## Результаты

### ✅ Ubuntu (GitHub Actions)

* Все **58 тест** пройден
* Покрытие кода: **97%**
* Артефакт: [HTML Coverage Report Ubuntu-latest (GitHub Actions)](https://github.com/and67rey/Vertical_Video_Maker/actions/runs/15516616364/artifacts/3283166311)

### ✅ macOS (GitHub Actions)

* Все **58 тест** пройден
* Покрытие кода: **97%**
* Артефакт: [HTML Coverage Report Macos-latest (GitHub Actions)](https://github.com/and67rey/Vertical_Video_Maker/actions/runs/15516616364/artifacts/3283165386)

### ✅ Windows (PyCharm локально)

* Тесты запущены в среде PyCharm (Python 3.10.1)
* Все **58 тест** пройден
* Покрытие кода: **97%**
* Локально просмотрен автономный отчёт `report.html` 

## Вывод

Требование ТЗ о кроссплатформенности выполнено:

* Код успешно собран и протестирован на Windows, Linux (Ubuntu), macOS
* Ошибок или сбоев не выявлено
* Код покрыт тестами на **97%**, все тесты пройдены
