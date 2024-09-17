from fastapi import FastAPI
from pydantic import BaseModel
from chunks import Chunk
import uvicorn
import os
import shutil
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Определение модели данных для FastAPI
class UserData(BaseModel):
    description: str | None = None

# Создание приложения FastAPI
app = FastAPI()

# Инициализация класса Chunk с размером 1024
chunk = Chunk(ch_size=1024)
source_directory = './new_files'
destination_directory = './RAG-Documents'

def move_files(src_dir, dest_dir):
    """Перемещает файлы из исходной директории в целевую."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_dir, filename)

        if os.path.isfile(src_file):
            shutil.move(src_file, dest_file)
            print(f"Перемещен: {src_file} -> {dest_file}")

class WatcherHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Перемещение файла и обновление после перемещения
            print(f"Новый файл обнаружен: {event.src_path}")
            chunk.load_pdf(source_directory)  # Обновление после перемещения
            move_files(source_directory, destination_directory)

def start_watching():
    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, path=source_directory, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Эндпоинт для получения ответа на запрос пользователя
@app.post("/getAnswer")
async def get_answer(userData: UserData):
    """
    Получить ответ на запрос от пользователя через FastAPI.
    Args:
        userData (UserData): Данные запроса, включающие описание.

    Returns:
        dict: Ответ на запрос.
    """
    # Используем метод async для получения ответа
    answer = await chunk.async_get_answer(userData.description)
    return {"answer": answer}

# Запуск сервера
if __name__ == "__main__":
    watcher_thread = threading.Thread(target=start_watching, daemon=True)
    watcher_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
