import psycopg2
import csv
from datetime import datetime
import os
import glob
from tkinter import Tk, Button, Label, Entry, StringVar, END
from tkinter import filedialog



'''
Модуль программы отвечает за формирование файлов реплик БД в формате CSV
Реплии ки берутся от даты указанной во вспомогательном файле history.txt
'''

selected_directory = ""
history_date =  ''
current_date = ''
'''
Получаем данные в файл csv
Данные получаем с учетом, того что время начала бепрется из файла history.txt
'''


def SaveDataFile():
    global selected_directory
    global history_date
    global current_date
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if selected_directory =='':
        #selected_directory = "C:\\Users\\I.Perekalskiy\\Sync\\"
        selected_directory = "C:\\Users\\user\\YandexDisk\\"
        
    

    # Чтение даты из файла history.txt Получаем дату последнего формирования отчета из файла
    try:
       with open('history.txt', 'r') as file:
        history_date = file.readline().strip()
        print(history_date)
        file.close()
    except FileNotFoundError:
        print("Ошибка чтения даты из файла")
        
    if history_date =='':
        history_date = '2024-01-06 03:01:00+00' 
          
    try:
    # Установите соединение с базой данных
        connection = psycopg2.connect(
            user="IntegrationUser",
            password="cie5upai4piev9Va",
            host="localhost",
            port="5432",
            database="MMPC_9x5_AGMK"
        )
        # print("Connect Success")
        
   
        # Создайте курсор
        cursor = connection.cursor()
        

        # Выполните SQL запрос
        # postgreSQL_select_Query = f'SELECT data, value FROM public."MesContent" WHERE data > {history_date} ORDER BY "idMes" ASC, "idDataBlock" ASC, "TagNum" ASC'
        # postgreSQL_select_Query = f'SELECT * FROM public."MesContent" ORDER BY "idMes" ASC, "idDataBlock" ASC, "TagNum" ASC'
        
        # Выполните SQL запрос
        postgreSQL_select_Query = f"""
        SELECT
            "Message"."FixTime",
            "MesContent"."idDataBlock",
            "MesContent"."TagNum",
            "MesContent"."Value",
            "TagPLC"."Name",
            "TagPLC"."Description"
        FROM public."MesContent"
        LEFT JOIN public."Message" ON "MesContent"."idMes" = "Message"."id"
        LEFT JOIN public."TagPLC" ON "TagPLC"."TagNum" = "MesContent"."TagNum"
        WHERE "Message"."FixTime" > '{history_date}';
        """
        
        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from mobile table using cursor.fetchall")
        current_date2 = current_date.replace(":", "-")
        records = cursor.fetchall()
        if not records:
            with open(os.path.join(selected_directory, '{}.csv'.format(current_date2)), 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['FixTime', 'idDataBlock', 'TagNum', 'Value', 'Name', 'Description'])
                for row in records:
                    writer.writerow(0, 0, 0, 0, 0, 0)
            print("Данные из базы не получены либо новых данных нет")
                    
        for row in records:
            '''
            print("FixTime = ", row[0], )
            print("idDataBlock = ", row[1])
            print("TagNum = ", row[2], )
            print("Value = ", row[3])
            
            '''
            
            if records:
                current_date2 = current_date.replace(":", "-")
                with open(os.path.join(selected_directory, '{}.csv'.format(current_date2)), 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(['FixTime', 'idDataBlock', 'TagNum', 'Value', 'Name', 'Description'])
                    for row in records:
                        writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5]])
                            
        # Пишем в файл дату обращения функция def wrightFileDate()
        wrightFileDate()
            
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
    # Закройте соединение с базой данных
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            

    # Update the "Run Count" label
    run_count.set(int(run_count.get()) + 1)

    # Update the "Last Run Time" label
    last_run_time.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    root.after(int(period.get())*1000, SaveDataFile)


# Функция пишет в файл текст дату обновления данных    
def wrightFileDate():
    global current_date
    try:                   
        # Пишем в файл с какого временибыл последний забор
        # Открыть файл для записи
        with open('history.txt', 'w') as file:
            # Записать текущую дату в файл
            file.write(current_date)
            print("Файл создан: ", file.name)
    except FileNotFoundError:
        print("Ошибка чтения даты из файла")

def start_automatically():
    # Schedule the SaveDataFile function to be called immediately, then every period seconds
    # Schedule the function to be called again after the period specified in the input field
    SaveDataFile()
    print("work start_automatically")

def browse_directory():
  global selected_directory
  dir_path = filedialog.askdirectory()
  dir_entry.delete(0, END)
  dir_entry.insert(0, dir_path)
  selected_directory = dir_path
  print(dir_path)

# print(getFileName())
# SaveDataFile()
root = Tk()
root.title("Database Replication")
run_count = StringVar()
run_count = StringVar(value='5')
last_run_time = StringVar()
period = StringVar()
period = StringVar(value='0')



# Create a Button to browse directories
browse_button = Button(root, text="Browse", command=browse_directory)
browse_button.grid(row=3, column=2)

Label(root, text="Period (seconds):").grid(row=2)
Entry(root, textvariable=period).grid(row=2, column=1)

Label(root, text="Run Count:").grid(row=0)
Label(root, textvariable=run_count).grid(row=0, column=1)

Label(root, text="Last Run Time:").grid(row=1)
Label(root, textvariable=last_run_time).grid(row=1, column=1)

Button(root, text="Start Automatically", command=start_automatically).grid(row=4)

# Create an Entry field for the directory path
dir_label = Label(root, text="Directory Path:")
dir_label.grid(row=3)
dir_entry = Entry(root)
dir_entry.grid(row=3, column=1)

root.mainloop()
