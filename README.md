# Проект Yatube (покрытие тестами)

### Написаны тесты, проверяющие:
+ модели приложения posts в Yatube.
+ правильно ли отображается значение поля __str__ в объектах моделей.
+ доступность страниц и названия шаблонов приложения Posts проекта Yatube. Проверка учитывает права доступа.
+ что запрос к несуществующей странице вернёт ошибку 404.
+ что во view-функциях используются правильные html-шаблоны.
+ соответствует ли ожиданиям словарь context, передаваемый в шаблон при вызове.
+ что если при создании поста указать группу, то этот пост появляется на главной странице сайта, на странице выбранной группы, в профайле пользователя.
+ что этот пост не попал в группу, для которой не был предназначен.
+ при отправке валидной формы со страницы создания поста reverse('posts:create_post') создаётся новая запись в базе данных.
+ при отправке валидной формы со страницы редактирования поста reverse('posts:post_edit', args=('post_id',)) происходит изменение поста с post_id в базе данных.

## Как запустить проект
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/kh199/hw04_tests
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
source env/bin/activate
```

Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Запустить проект:
```
python3 manage.py runserver
```
## Технологии
Python 3.7 
Django 2.2.19
