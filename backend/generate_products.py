import csv
import random


def generate_products_csv(filename="backend/products.csv"):
    # Brand specialization
    brand_specializations = {
        "Pear": ["Smartphone", "Tablet", "Smartwatch"],
        "Samsing": ["Smartphone", "Tablet", "Monitor", "Smartwatch"],
        "Gugle": ["Smartphone", "Tablet", "Router"],
        "Macrosoft": ["Laptop", "Tablet"],
        "Novolo": ["Laptop", "Monitor"],
        "H-Pee": ["Laptop", "Monitor"],
        "Asos": ["Laptop", "Monitor", "Headphones", "Gaming-PC"],
        "Sonny": ["Headphones", "Monitor", "Webcam"],
        "Dellta": ["Laptop", "Monitor", "Router"],
    }

    base_types = {
        "Smartphone": (0.2, (15.0, 7.0, 0.8)),
        "Laptop": (1.5, (35.0, 25.0, 2.0)),
        "Tablet": (0.5, (25.0, 18.0, 0.7)),
        "Monitor": (5.0, (60.0, 40.0, 15.0)),
        "Smartwatch": (0.05, (4.0, 4.0, 1.0)),
        "Headphones": (0.3, (20.0, 18.0, 8.0)),
        "Webcam": (0.2, (10.0, 5.0, 5.0)),
        "Router": (0.8, (20.0, 20.0, 5.0)),
        "Gaming-PC": (10.0, (50.0, 20.0, 45.0)),
    }

    suffixes = ["", "Pro", "Max", "Ultra", "Lite", "Air"]

    products = []

    # Generate specialized products
    for brand, allowed_types in brand_specializations.items():
        for t_name in allowed_types:
            t_weight, t_dims = base_types[t_name]
            # Not all brands have all suffixes for all types
            brand_suffixes = random.sample(suffixes, k=random.randint(2, 4))
            for s in brand_suffixes:
                name = f"{brand} {t_name} {s}".strip().replace("  ", " ")
                price = round(random.uniform(150.0, 2500.0), 2)
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

    # Add some unique/rare items for search testing
    unique_items = [
        {
            "name": "Vintage Mechanical Typewriter",
            "price": 450.0,
            "weight": 5.2,
            "dim_x": 40.0,
            "dim_y": 35.0,
            "dim_z": 15.0,
        },
        {
            "name": "Quantum Computing Starter Kit",
            "price": 9999.99,
            "weight": 25.0,
            "dim_x": 100.0,
            "dim_y": 80.0,
            "dim_z": 60.0,
        },
        {
            "name": "Golden Industrial Scissors",
            "price": 120.0,
            "weight": 0.4,
            "dim_x": 25.0,
            "dim_y": 10.0,
            "dim_z": 1.5,
        },
        {
            "name": "Cybernetic Eye Implant (Mock)",
            "price": 299.0,
            "weight": 0.1,
            "dim_x": 3.0,
            "dim_y": 3.0,
            "dim_z": 2.5,
        },
    ]
    products.extend(unique_items)

    # Shuffle to avoid brand grouping in search if no sorting is applied
    random.shuffle(products)

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "price", "weight", "dim_x", "dim_y", "dim_z"]
        )
        writer.writeheader()
        writer.writerows(products)
    print(f"Generated {len(products)} specialized products in {filename}")


if __name__ == "__main__":
    generate_products_csv()
