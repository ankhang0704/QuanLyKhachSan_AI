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
Step 3: Update
```bash
python.exe -m pip install --upgrade pip
```
Step 4: Migrate database
```bash
python manage.py makemigrations
python manage.py migrate
```

Step 5: If you use vscode press F5 to run project or
```bash
python manage.py runserver
```

Superaccount
username: admin123
password: 123456

Step 6: Edit Css (need install Node.js) cd your project (have file package.json)
```bash
npm install
npm run watch
```
```bash
python manage.py runserver
```

Install Model AI
https://huggingface.co/unsloth/Phi-4-mini-instruct-GGUF/tree/main