from pymongo import MongoClient
import sys
sys.stdout.reconfigure(encoding='utf-8')
import certifi
import streamlit as st
def connect():
    client = MongoClient("mongodb+srv://dannyphong2407_db_user:BHDDUSYdCsOyk21m@products.if7njrq.mongodb.net/")
    if client:
        print(" Kết nối MongoDB thành công!")
    else:
        print(" Kết nối MongoDB thất bại!")
        sys.exit(1)
    db = client["flower_shop"]
    collection = db["flowers"]
    return collection

def insert_data(collection):
    try:
        flower_id = input("Nhập ID (ví dụ: A2): ").strip()
        if collection.find_one({"_id": flower_id}):
            print(" ID này đã tồn tại, vui lòng chọn ID khác!")
            return

        name = input("Nhập tên hoa: ")
        image = input("Nhập đường dẫn ảnh (ví dụ: assets/A2.png): ")

        print("Nhập giá trị cho từng tiêu chí:")
        c1 = float(input("Giá bán (C1): "))
        c2 = float(input("C2: "))
        c3 = float(input("C3: "))
        c4 = float(input("C4: "))

        data = {
            "_id": flower_id,
            "name": name,
            "image": image,
            "values": {
                "C1": c1,
                "C2": c2,
                "C3": c3,
                "C4": c4
            }
        }

        collection.insert_one(data)
        print(" Đã thêm hoa mới vào cơ sở dữ liệu!")

    except ValueError:
        print(" Lỗi: Vui lòng nhập số hợp lệ cho các tiêu chí (C1, C2, C3, C4).")
    except Exception as e:
        print(f" Lỗi khi thêm dữ liệu: {e}")


def update_field(collection):
    flower_id = input("Nhập ID hoa cần cập nhật: ").strip()
    flower = collection.find_one({"_id": flower_id})
    if not flower:
        print(" Không tìm thấy ID này trong cơ sở dữ liệu.")
        return

    print("\nChọn loại cập nhật:")
    print("1. Cập nhật thông tin chính (name, image, ...)")
    print("2. Cập nhật giá trị trong 'values' (C1, C2, C3, C4)")
    choice = input("Lựa chọn (1 hoặc 2): ").strip()

    try:
        if choice == "1":
            field = input("Nhập tên trường muốn cập nhật (vd: name, image): ").strip()
            new_value = input("Nhập giá trị mới: ").strip()

            try:
                new_value = float(new_value)
            except ValueError:
                pass

            collection.update_one({"_id": flower_id}, {"$set": {field: new_value}})
            print(" Đã cập nhật thông tin thành công!")

        elif choice == "2":
            c_field = input("Nhập tiêu chí cần thay đổi (C1, C2, C3, C4): ").strip()
            new_value = float(input(f"Nhập giá trị mới cho {c_field}: "))

            collection.update_one(
                {"_id": flower_id},
                {"$set": {f"values.{c_field}": new_value}}
            )
            print(f" Đã cập nhật {c_field} thành {new_value} thành công!")

        else:
            print(" Lựa chọn không hợp lệ.")

    except Exception as e:
        print(f" Lỗi khi cập nhật dữ liệu: {e}")


def find_data(collection):
    key = input("Nhập tên trường muốn tìm (ví dụ: Type, _id...): ").strip()
    value = input("Nhập giá trị cần tìm: ").strip()
    if value.isdigit():
        value = int(value)

    results = collection.find({key: value})
    found = False
    for doc in results:
        print(doc)
        found = True
    if not found:
        print(" Không tìm thấy dữ liệu phù hợp.")


if __name__ == "__main__":
    collection = connect()

    while True:
        print("\n ===== QUẢN LÝ HOA TƯƠI (MongoDB) =====")
        print("1. Thêm dữ liệu mới")
        print("2. Cập nhật trường cho hoa")
        print("3. Tìm kiếm hoa")
        print("4. Thoát chương trình")
        choice = input(" Chọn chức năng (1-4): ")

        if choice == "1":
            insert_data(collection)
        elif choice == "2":
            update_field(collection)
        elif choice == "3":
            find_data(collection)
        elif choice == "4":
            print(" Tạm biệt")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng nhập lại.")