# Xây dựng website quản lý đặt phòng khách sạn The Sailing Bay tích hợp AI Chatbot tư vấn.

Step 1: Activate enviroments
```bash
py -3 -m venv .venv
.venv\scripts\activate
```

Step 2: Install requirements 
```bash
pip install -r requirements.txt
```
Step 3: Update (if need)
```bash
python.exe -m pip install --upgrade pip
```
Step 4: Migrate database (if need)
```bash
python manage.py makemigrations
python manage.py migrate
```

Step 4: If you use vscode press F5 to run project or
```bash
python manage.py runserver
```
