import csv
import random


def generate_products_csv(filename="backend/products.csv"):
    brands = [
        "Pear",
        "Samsing",
        "Gogel",
        "Macrosoft",
        "Novolo",
        "H-Pea",
        "Asos",
        "Sonny",
        "Dellta",
    ]
    types = [
        ("Smartphone", 0.2, (15.0, 7.0, 0.8)),
        ("Laptop", 1.5, (35.0, 25.0, 2.0)),
        ("Tablet", 0.5, (25.0, 18.0, 0.7)),
        ("Monitor", 5.0, (60.0, 40.0, 15.0)),
        ("Smartwatch", 0.05, (4.0, 4.0, 1.0)),
        ("Headphones", 0.3, (20.0, 18.0, 8.0)),
        ("Webcam", 0.2, (10.0, 5.0, 5.0)),
        ("Router", 0.8, (20.0, 20.0, 5.0)),
    ]
    suffixes = ["", "Pro", "Max", "Ultra", "Lite", "Air", "Gaming", "Business"]

    products = []
    for b in brands:
        for t_name, t_weight, t_dims in types:
            for s in suffixes:
                for i in range(1, 3):
                    name = f"{b} {t_name} {s} {i}".strip().replace("  ", " ")
                    price = round(random.uniform(20.0, 2500.0), 2)
                    v = random.uniform(0.9, 1.1)
                    products.append(
                        {
                            "name": name,
                            "price": price,
                            "weight": round(t_weight * v, 2),
                            "dim_x": round(t_dims[0] * v, 1),
                            "dim_y": round(t_dims[1] * v, 1),
                            "dim_z": round(t_dims[2] * v, 1),
                        }
                    )

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "price", "weight", "dim_x", "dim_y", "dim_z"]
        )
        writer.writeheader()
        writer.writerows(products)
    print(f"Generated {len(products)} products in {filename}")


if __name__ == "__main__":
    generate_products_csv()
