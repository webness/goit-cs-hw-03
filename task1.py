import psycopg2
from faker import Faker
import random


def execute_sql_script(filename, connection):
    with connection.cursor() as cursor:
        with open(filename, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        cursor.execute(sql_script)
    connection.commit()


def populate_tables(connection):
    fake = Faker()
    user_ids = []
    with connection.cursor() as cursor:
        # Вставка користувачів
        insert_users_query = "INSERT INTO users (fullname, email) VALUES (%s, %s) RETURNING id;"
        for _ in range(10):
            fullname = fake.name()
            email = fake.unique.email()
            cursor.execute(insert_users_query, (fullname, email))
            user_id = cursor.fetchone()[0]
            user_ids.append(user_id)
        print(f"Вставлено {len(user_ids)} користувачів.")

        # Вставка завдань: статус (id: 1 - 'new', 2 - 'in progress', 3 - 'completed')
        insert_tasks_query = "INSERT INTO tasks (title, description, status_id, user_id) VALUES (%s, %s, %s, %s);"
        tasks_data = []
        for _ in range(20):
            title = fake.sentence(nb_words=6)
            description = fake.text(max_nb_chars=200)
            status_id = random.choice([1, 2, 3])
            user_id = random.choice(user_ids)
            tasks_data.append((title, description, status_id, user_id))
        cursor.executemany(insert_tasks_query, tasks_data)
        print(f"Вставлено {len(tasks_data)} завдань.")
    connection.commit()
    return user_ids


def run_queries(connection, user_ids):
    cursor = connection.cursor()

    # 1. Отримати всі завдання певного користувача (використовуємо першого з user_ids)
    query1 = "SELECT * FROM tasks WHERE user_id = %s;"
    print("\nЗапит 1:", query1, "Параметри:", user_ids[0])
    cursor.execute(query1, (user_ids[0],))
    res1 = cursor.fetchall()
    print("Відповідь 1:", res1)

    # 2. Вибрати завдання за статусом 'new' за допомогою підзапиту
    query2 = "SELECT * FROM tasks WHERE status_id = (SELECT id FROM status WHERE name = 'new');"
    print("\nЗапит 2:", query2)
    cursor.execute(query2)
    res2 = cursor.fetchall()
    print("Відповідь 2:", res2)

    # 3. Оновити статус конкретного завдання на 'in progress'
    # Для прикладу вибираємо перше завдання з таблиці
    cursor.execute("SELECT id FROM tasks LIMIT 1;")
    task_id = cursor.fetchone()[0]
    query3 = "UPDATE tasks SET status_id = (SELECT id FROM status WHERE name = 'in progress') WHERE id = %s RETURNING *;"
    print("\nЗапит 3:", query3, "Параметри:", task_id)
    cursor.execute(query3, (task_id,))
    res3 = cursor.fetchone()
    print("Відповідь 3:", res3)

    # 4. Отримати список користувачів, які не мають жодного завдання
    query4 = "SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM tasks);"
    print("\nЗапит 4:", query4)
    cursor.execute(query4)
    res4 = cursor.fetchall()
    print("Відповідь 4:", res4)

    # 5. Додати нове завдання для конкретного користувача (використовуємо першого з user_ids)
    new_task_title = "Новий тестовий таск"
    new_task_description = "Опис нового тестового завдання"
    query5 = ("INSERT INTO tasks (title, description, status_id, user_id) "
              "VALUES (%s, %s, (SELECT id FROM status WHERE name = 'new'), %s) RETURNING *;")
    print("\nЗапит 5:", query5, "Параметри:", (new_task_title, new_task_description, user_ids[0]))
    cursor.execute(query5, (new_task_title, new_task_description, user_ids[0]))
    new_task = cursor.fetchone()
    print("Відповідь 5:", new_task)
    new_task_id = new_task[0]  # збережемо id нового завдання для наступного запиту

    # 6. Отримати всі завдання, які ще не завершено (тобто статус не 'completed')
    query6 = "SELECT * FROM tasks WHERE status_id != (SELECT id FROM status WHERE name = 'completed');"
    print("\nЗапит 6:", query6)
    cursor.execute(query6)
    res6 = cursor.fetchall()
    print("Відповідь 6:", res6)

    # 7. Видалити конкретне завдання (видаляємо завдання, додане в запиті 5)
    query7 = "DELETE FROM tasks WHERE id = %s RETURNING *;"
    print("\nЗапит 7:", query7, "Параметри:", new_task_id)
    cursor.execute(query7, (new_task_id,))
    res7 = cursor.fetchone()
    print("Відповідь 7:", res7)

    # 8. Знайти користувачів з певною електронною поштою (фільтрація за доменом)
    cursor.execute("SELECT email FROM users LIMIT 1;")
    first_email = cursor.fetchone()[0]
    domain = first_email.split('@')[1]
    pattern = '%@' + domain
    query8 = "SELECT * FROM users WHERE email LIKE %s;"
    print("\nЗапит 8:", query8, "Параметри:", pattern)
    cursor.execute(query8, (pattern,))
    res8 = cursor.fetchall()
    print("Відповідь 8:", res8)

    # 9. Оновити ім'я користувача (оновлюємо першого користувача)
    new_fullname = "Новий Ім'я"
    query9 = "UPDATE users SET fullname = %s WHERE id = %s RETURNING *;"
    print("\nЗапит 9:", query9, "Параметри:", (new_fullname, user_ids[0]))
    cursor.execute(query9, (new_fullname, user_ids[0]))
    res9 = cursor.fetchone()
    print("Відповідь 9:", res9)

    # 10. Отримати кількість завдань для кожного статусу (групування)
    query10 = ("SELECT s.name, COUNT(t.id) as task_count FROM status s "
               "LEFT JOIN tasks t ON s.id = t.status_id GROUP BY s.name;")
    print("\nЗапит 10:", query10)
    cursor.execute(query10)
    res10 = cursor.fetchall()
    print("Відповідь 10:", res10)

    # 11. Отримати завдання, призначені користувачам з певною доменною частиною електронної пошти
    query11 = "SELECT t.* FROM tasks t JOIN users u ON t.user_id = u.id WHERE u.email LIKE %s;"
    print("\nЗапит 11:", query11, "Параметри:", pattern)
    cursor.execute(query11, (pattern,))
    res11 = cursor.fetchall()
    print("Відповідь 11:", res11)

    # 12. Отримати список завдань, що не мають опису.
    # Спочатку оновлюємо одне завдання, щоб його опис був NULL.
    cursor.execute("SELECT id FROM tasks LIMIT 1;")
    task_for_null = cursor.fetchone()[0]
    query_update_null = "UPDATE tasks SET description = NULL WHERE id = %s RETURNING *;"
    print("\nЗапит (оновлення опису):", query_update_null, "Параметри:", task_for_null)
    cursor.execute(query_update_null, (task_for_null,))
    res_update_null = cursor.fetchone()
    print("Відповідь (оновлення опису):", res_update_null)
    # Потім вибираємо завдання без опису.
    query12 = "SELECT * FROM tasks WHERE description IS NULL OR description = '';"
    print("\nЗапит 12:", query12)
    cursor.execute(query12)
    res12 = cursor.fetchall()
    print("Відповідь 12:", res12)

    # 13. Вибрати користувачів та їхні завдання, які є у статусі 'in progress'
    query13 = ("""
        SELECT u.fullname, t.title, s.name 
        FROM users u 
        INNER JOIN tasks t ON u.id = t.user_id 
        INNER JOIN status s ON t.status_id = s.id 
        WHERE s.name = 'in progress';
    """)
    print("\nЗапит 13:", query13)
    cursor.execute(query13)
    res13 = cursor.fetchall()
    print("Відповідь 13:", res13)

    # 14. Отримати користувачів та кількість їхніх завдань
    query14 = ("SELECT u.fullname, COUNT(t.id) AS task_count FROM users u "
               "LEFT JOIN tasks t ON u.id = t.user_id GROUP BY u.fullname;")
    print("\nЗапит 14:", query14)
    cursor.execute(query14)
    res14 = cursor.fetchall()
    print("Відповідь 14:", res14)

    connection.commit()
    cursor.close()


def main():
    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="goit-cs-hw-03",
        user="postgres",
        password="postgres"
    )

    connection.autocommit = True

    try:
        with connection.cursor() as cursor:
            sql = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
            cursor.execute(sql)

        execute_sql_script('create-tables.sql', connection)
        user_ids = populate_tables(connection)
        run_queries(connection, user_ids)
        print("\nВсі операції виконано успішно!")
    except Exception as e:
        print(f"Виникла помилка: {e}")
    finally:
        connection.close()


if __name__ == '__main__':
    main()
