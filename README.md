# api-shop-bot

- Step 1: Tạo file `.env` từ file `.env.example`: 
```sh
 cp .env.example .env
 ```
- Step 2: Thêm GOOGLE_API_KEY vào file .env (lấy từ Google AI Studio)
- Step 3: Run docker compose: 
```sh
docker compose up --build
```
- Step 4: CD vào folder chatbot-backend: 
```sh
cd shop_bot_backend
```
- Step 5: Tạo môi trường với anaconda qua lệnh: 
```sh
conda create -n shopbot python=3.11.9
```
- Step 6: Activate môi trường: 
```sh
conda activate shopbot
```
- Step 7: Install dependencies: 
```sh
pip install -r requirements.txt
```
- Step 8: Seed data vào database: 
```sh
python app/db/seed_data.py
```
- Step 9: Run backend: 
```sh
uvicorn main:app --reload --host 127.0.0.1 --port 8030
```