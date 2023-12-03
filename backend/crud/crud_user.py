from sqlalchemy.orm import Session
import bcrypt
import json

from models import user, category, item, stores
from schemas import schemas


def get_user(db: Session, user_id: int):
    return db.query(user.User).filter(user.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(user.User).filter(user.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(user.User).offset(skip).limit(limit).all()


def register_user(db: Session, userCreate: schemas.UserCreate):
    hashed_password = bcrypt.hashpw(
        userCreate.password.encode("utf-8"), bcrypt.gensalt()
    )
    hashed_password = hashed_password.decode("utf-8")
    db_user = user.User(email=userCreate.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def populate_tables(db: Session):
    file_path = "mock_data/merged_product.json"
    all_added = False
    with open(file_path, "r") as file:
        data = json.load(file)

    for item_data in data:
        # Create Category instance
        new_category = category.Category(
            sub_category_name=item_data["category"]["sub_category_name"],
            top_category_name=item_data["category"]["top_category_name"],
        )
        new_item = item.Item(
            name=item_data["name"],
            brand=item_data["brand"],
            description=item_data["description"],
            gln=item_data["gln"],
            gtin=item_data["gtin"],
            measurements_units=item_data["measurements"]["units"],
            measurements_amount=item_data["measurements"]["amount"],
            measurements_label=item_data["measurements"]["label"],
            categories=[new_category],
        )
        if item_data["piture_links"]:
            new_item.picture_link = item.PictureLink(
                width=item_data["piture_links"][0][
                    "width"
                ],  # Assuming there is at least one element in the array
                height=item_data["piture_links"][0]["height"],
                url=item_data["piture_links"][0]["url"],
            )
        db.add(new_item)
        for store_name, store_data in item_data["stores"].items():
            price = (
                float(store_data["price"]) if store_data["price"] != "null" else None
            )
            new_store = stores.Store(
                name=store_name,
                link=store_data["link"],
                price=price,
                discount_info=store_data.get("discount_info"),
            )
            new_item.stores.append(new_store)
        all_added = True
    db.commit()
    db.close()
    return all_added
