import streamlit as st
import os
import shutil

# Путь к директории, где хранятся файлы
DIRECTORY_PATH = './new_files'

def list_files(directory_path):
    """Возвращает список файлов в директории"""
    return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

def upload_file(directory_path):
    """Загружает файл в указанную директорию"""
    uploaded_file = st.file_uploader("Загрузите файл", type=['pdf', 'txt', 'jpg', 'png', 'docx'])
    if uploaded_file is not None:
        file_path = os.path.join(directory_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f'Файл {uploaded_file.name} успешно загружен.')

# def delete_file(directory_path):
#     """Удаляет выбранный файл из директории"""
#     files = list_files(directory_path)
#     selected_file = st.selectbox("Выберите файл для удаления", files)
#     if st.button("Удалить файл"):
#         if selected_file:
#             file_path = os.path.join(directory_path, selected_file)
#             os.remove(file_path)
#             st.success(f'Файл {selected_file} успешно удален.')
#         else:
#             st.warning("Выберите файл для удаления.")

def main():
    st.title("Управление файлами в директории")
    
    st.sidebar.header("Функции")
    option = st.sidebar.selectbox("Выберите действие", ["Просмотр файлов", "Загрузить файл"])
    
    if option == "Просмотр файлов":
        st.subheader("Список файлов")
        files = list_files(DIRECTORY_PATH)
        if files:
            st.write(files)
        else:
            st.write("В директории нет файлов.")
    
    elif option == "Загрузить файл":
        st.subheader("Загрузите новый файл")
        upload_file(DIRECTORY_PATH)
    
   

if __name__ == "__main__":
    main()
