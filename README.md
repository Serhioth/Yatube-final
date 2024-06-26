# YaTube: A Social Network for Posts and Images (Yandex.Praktikum)

## Project Description
This project was created as part of the Yandex.Praktikum educational course.

YaTube is a social network for authors and followers. Users can subscribe to their favorite authors, leave and delete comments on posts, create new posts on the main page and in thematic groups, and attach images to their published posts.

The project is implemented using the MVT (Model-View-Template) architecture. It includes features such as user registration, password recovery via email, unit testing using `unittest`, post pagination, and page caching.

## System Requirements
- Python 3.8+
- Works on Linux, Windows, macOS, and BSD

## Technology Stack
- Python 3.8
- Django 2.2
- Unittest
- Pytest
- SQLite3
- CSS
- JS
- HTML

## Installation from Repository (Linux and macOS)
1. Clone the repository and navigate to it in the command line:
```bash
git clone git@github.com:Serhioth/Yatube-final.git
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
3. Install dependencies from the `requirements.txt` file:
```bash
pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
cd ./yatube
```
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```

5. Start the project (in Django server mode):
```bash
python manage.py runserver
```
