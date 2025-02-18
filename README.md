# api-shop-bot

- Step 1: Tạo file `.env` từ file `.env.example`: 
```sh
 cp .env.example .env
 ```
- Step 2: Run docker compose: 
```sh
docker compose up --build
```
- Step 3: CD vào folder chatbot-backend: 
```sh
cd shop_bot_backend
```
- Step 4: Tạo môi trường với anaconda qua lệnh: 
```sh
conda create -n shopbot python=3.11.9
```
- Step 5: Activate môi trường: 
```sh
conda activate myenv
```
- Step 6: Install dependencies: 
```sh
pip install -r requirements.txt
```
- Step 7: Seed data vào database: 
```sh
python app/db/seed_data.py
```
- Step 8: Run backend: 
```sh
uvicorn main:app --reload --host 0.0.0.0 --port 8030
```