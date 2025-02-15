from pymongo import MongoClient

# Підключення до MongoDB (за замовчуванням localhost:27017)
client = MongoClient('mongodb://localhost:27017/')
# Створення (або вибір) бази даних "cats_db"
db = client['cats_db']
# Створення (або вибір) колекції "cats"
collection = db['cats']


# Функція для створення/додавання нового запису (Create)
def create_cat(name, age, features):
    cat = {"name": name, "age": age, "features": features}
    result = collection.insert_one(cat)
    print("Додано кота з _id:", result.inserted_id)


# Функція для виведення всіх записів з колекції (Read)
def read_all_cats():
    cats = collection.find()
    print("Всі коти:")
    for cat in cats:
        print(cat)


# Функція для пошуку та виведення інформації про кота за ім'ям (Read)
def read_cat_by_name(name):
    cat = collection.find_one({"name": name})
    if cat:
        print("Знайдений кіт:", cat)
    else:
        print("Кота з ім'ям", name, "не знайдено.")


# Функція для оновлення віку кота за ім'ям (Update)
def update_cat_age(name, new_age):
    result = collection.update_one({"name": name}, {"$set": {"age": new_age}})
    if result.modified_count > 0:
        print("Вік кота успішно оновлено.")
    else:
        print("Кота з ім'ям", name, "не знайдено або новий вік співпадає зі старим.")


# Функція для додавання нової характеристики до списку features кота за ім'ям (Update)
def add_feature_to_cat(name, new_feature):
    result = collection.update_one({"name": name}, {"$push": {"features": new_feature}})
    if result.modified_count > 0:
        print("Нова характеристика додана.")
    else:
        print("Кота з ім'ям", name, "не знайдено.")


# Функція для видалення запису з колекції за ім'ям тварини (Delete)
def delete_cat_by_name(name):
    result = collection.delete_one({"name": name})
    if result.deleted_count > 0:
        print("Кота з ім'ям", name, "успішно видалено.")
    else:
        print("Кота з ім'ям", name, "не знайдено.")


# Функція для видалення всіх записів із колекції (Delete)
def delete_all_cats():
    result = collection.delete_many({})
    print("Видалено", result.deleted_count, "записів.")


# Меню для взаємодії з користувачем
def menu():
    print("\nВиберіть операцію:")
    print("1. Додати нового кота (Create)")
    print("2. Вивести всіх котів (Read all)")
    print("3. Вивести інформацію про кота за ім'ям (Read by name)")
    print("4. Оновити вік кота за ім'ям (Update age)")
    print("5. Додати характеристику коту за ім'ям (Add feature)")
    print("6. Видалити кота за ім'ям (Delete by name)")
    print("7. Видалити всіх котів (Delete all)")
    print("8. Вихід")


def main():
    while True:
        menu()
        choice = input("Введіть номер операції: ").strip()
        if choice == '1':
            name = input("Введіть ім'я кота: ").strip()
            try:
                age = int(input("Введіть вік кота: ").strip())
            except ValueError:
                print("Вік має бути числом.")
                continue
            features_str = input("Введіть характеристики (через кому): ")
            features = [feature.strip() for feature in features_str.split(",") if feature.strip()]
            create_cat(name, age, features)
        elif choice == '2':
            read_all_cats()
        elif choice == '3':
            name = input("Введіть ім'я кота: ").strip()
            read_cat_by_name(name)
        elif choice == '4':
            name = input("Введіть ім'я кота: ").strip()
            try:
                new_age = int(input("Введіть новий вік: ").strip())
            except ValueError:
                print("Вік має бути числом.")
                continue
            update_cat_age(name, new_age)
        elif choice == '5':
            name = input("Введіть ім'я кота: ").strip()
            new_feature = input("Введіть нову характеристику: ").strip()
            add_feature_to_cat(name, new_feature)
        elif choice == '6':
            name = input("Введіть ім'я кота: ").strip()
            delete_cat_by_name(name)
        elif choice == '7':
            confirm = input("Ви впевнені, що хочете видалити всіх котів? (так/ні): ").strip().lower()
            if confirm == "так":
                delete_all_cats()
        elif choice == '8':
            print("Вихід із програми.")
            break
        else:
            print("Невірний вибір, спробуйте ще раз.")


if __name__ == "__main__":
    main()
