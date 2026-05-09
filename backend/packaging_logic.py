import hashlib
from typing import Dict, List

from . import schemas


def simulate_cpu_load(item_count: int):
    """
    Simulates a CPU-bound task by performing redundant calculations.
    Growth is exponential: complexity ~ O(1.5^n) to simulate heavy algorithms.
    """
    base_iterations = 50_000
    iterations = int(base_iterations * (1.5 ** min(item_count, 25)))

    result = 0
    for i in range(iterations):
        result += (i * i) % 123
        if i % 1000 == 0:
            hashlib.sha256(str(i).encode()).hexdigest()
    return result


def get_box_type(volume: float) -> str:
    if volume <= 5000:
        return "Small Box (A4)"
    elif volume <= 20000:
        return "Medium Box (B2)"
    elif volume <= 60000:
        return "Large Box (C1)"
    else:
        return "Extra Large Box (D3)"


def optimize_packaging_logic(items: List[schemas.ProductItem], db_products: Dict):
    total_items_count = sum(p.count for p in items)

    # 1. Simulate CPU load
    simulate_cpu_load(total_items_count)

    # 2. Heuristic packaging
    # We want to pack items into boxes with a realistic distribution
    BOX_MAX_VOLUME = 60000.0  # Max volume for Large Box

    boxes = []
    current_box_items = []
    current_box_volume = 0.0
    current_box_weight = 0.0

    total_volume = 0.0
    total_weight = 0.0

    # Process each item one by one to simulate "filling" boxes
    for item_req in items:
        product = db_products.get(item_req.id)
        if not product:
            continue

        prod_volume = product.dim_x * product.dim_y * product.dim_z
        prod_weight = product.weight

        for _ in range(item_req.count):
            # If item itself is larger than BOX_MAX_VOLUME, it gets its own XL box
            if prod_volume > BOX_MAX_VOLUME:
                # Close current box if it has anything
                if current_box_items:
                    boxes.append(
                        schemas.PackagingBox(
                            box_type=get_box_type(current_box_volume),
                            items=current_box_items,
                            total_weight_g=round(current_box_weight, 2),
                            total_volume_cm3=round(current_box_volume, 2),
                        )
                    )
                    current_box_items = []
                    current_box_volume = 0.0
                    current_box_weight = 0.0

                # Add XL box for the oversized item
                boxes.append(
                    schemas.PackagingBox(
                        box_type=get_box_type(prod_volume),
                        items=[schemas.ProductItem(id=item_req.id, count=1)],
                        total_weight_g=round(prod_weight, 2),
                        total_volume_cm3=round(prod_volume, 2),
                    )
                )
                total_volume += prod_volume
                total_weight += prod_weight
                continue

            # Check if it fits in current box
            if current_box_volume + prod_volume > BOX_MAX_VOLUME:
                # Close current box
                boxes.append(
                    schemas.PackagingBox(
                        box_type=get_box_type(current_box_volume),
                        items=current_box_items,
                        total_weight_g=round(current_box_weight, 2),
                        total_volume_cm3=round(current_box_volume, 2),
                    )
                )
                current_box_items = []
                current_box_volume = 0.0
                current_box_weight = 0.0

            # Add item to box
            # Check if item already in box to increment count
            found = False
            for bi in current_box_items:
                if bi.id == item_req.id:
                    bi.count += 1
                    found = True
                    break
            if not found:
                current_box_items.append(schemas.ProductItem(id=item_req.id, count=1))

            current_box_volume += prod_volume
            current_box_weight += prod_weight
            total_volume += prod_volume
            total_weight += prod_weight

    # Add last box if not empty
    if current_box_items:
        boxes.append(
            schemas.PackagingBox(
                box_type=get_box_type(current_box_volume),
                items=current_box_items,
                total_weight_g=round(current_box_weight, 2),
                total_volume_cm3=round(current_box_volume, 2),
            )
        )

    return schemas.PackagingResponse(
        boxes=boxes,
        total_volume_cm3=round(total_volume, 2),
        total_weight_g=round(total_weight, 2),
    )
