import csv
import random


def generate_products_csv(filename="backend/products.csv"):
    # Brand specialization: (allowed_types, brand_multiplier)
    brand_specializations = {
        "Pear": (["Smartphone", "Tablet", "Smartwatch"], 1.5),  # High-end brand
        "Samsing": (["Smartphone", "Tablet", "Monitor", "Smartwatch"], 1.2),
        "Gugle": (["Smartphone", "Tablet", "Router"], 1.1),
        "Macrosoft": (["Laptop", "Tablet"], 1.3),
        "Novolo": (["Laptop", "Monitor"], 0.9),
        "H-Pee": (["Laptop", "Monitor"], 0.9),
        "Asos": (["Laptop", "Monitor", "Headphones", "Gaming-PC"], 1.0),
        "Sonny": (["Headphones", "Monitor", "Webcam"], 1.4),
        "Dellta": (["Laptop", "Monitor", "Router"], 1.0),
    }

    # Base characteristics: (base_price, weight_kg, dimensions_cm)
    base_types = {
        "Smartphone": (600.0, 0.2, (15.0, 7.0, 0.8)),
        "Laptop": (1200.0, 1.5, (35.0, 25.0, 2.0)),
        "Tablet": (400.0, 0.5, (25.0, 18.0, 0.7)),
        "Monitor": (300.0, 5.0, (60.0, 40.0, 15.0)),
        "Smartwatch": (250.0, 0.05, (4.0, 4.0, 1.0)),
        "Headphones": (200.0, 0.3, (20.0, 18.0, 8.0)),
        "Webcam": (100.0, 0.2, (10.0, 5.0, 5.0)),
        "Router": (150.0, 0.8, (20.0, 20.0, 5.0)),
        "Gaming-PC": (2000.0, 10.0, (50.0, 20.0, 45.0)),
    }

    suffix_multipliers = {
        "Lite": 0.7,
        "": 1.0,
        "Air": 1.1,
        "Pro": 1.3,
        "Max": 1.5,
        "Ultra": 1.8,
    }

    products = []

    # Generate specialized products
    for brand, (allowed_types, brand_mult) in brand_specializations.items():
        for t_name in allowed_types:
            base_price, t_weight, t_dims = base_types[t_name]
            # Not all brands have all suffixes for all types
            brand_suffixes = random.sample(
                list(suffix_multipliers.keys()), k=random.randint(2, 4)
            )
            for s in brand_suffixes:
                s_mult = suffix_multipliers[s]
                name = f"{brand} {t_name} {s}".strip().replace("  ", " ")

                # Calculate price: base * brand_mult * suffix_mult + some noise
                price = round(
                    base_price * brand_mult * s_mult * random.uniform(0.95, 1.05), 2
                )

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
