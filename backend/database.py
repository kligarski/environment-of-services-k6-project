import csv
import os

from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./logistics.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    weight = Column(Float)  # in kg
    dim_x = Column(Float)  # in cm
    dim_y = Column(Float)  # in cm
    dim_z = Column(Float)  # in cm


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_data(db):
    if db.query(Product).first() is None:
        csv_path = os.path.join(os.path.dirname(__file__), "products.csv")
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found. Skipping seeding.")
            return

        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            products = [
                Product(
                    name=row["name"],
                    price=float(row["price"]),
                    weight=float(row["weight"]),
                    dim_x=float(row["dim_x"]),
                    dim_y=float(row["dim_y"]),
                    dim_z=float(row["dim_z"]),
                )
                for row in reader
            ]
            db.add_all(products)
            db.commit()
            print(f"Seeded {len(products)} products from CSV.")
