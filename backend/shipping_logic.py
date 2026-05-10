import asyncio
import random


async def simulate_provider_delay(provider_name: str):
    # Base delays and multipliers for providers
    config = {
        "OutPost": {"base": 0.1, "mult": 1.0},
        "LHD": {"base": 0.2, "mult": 1.2},
        "SPU": {"base": 0.3, "mult": 1.5},
        "PDP": {"base": 0.15, "mult": 1.1},
    }

    c = config.get(provider_name, {"base": 0.2, "mult": 1.0})
    # Random jitter: 80% to 120% of base delay
    delay = c["base"] * c["mult"] * (0.8 + random.random() * 0.4)

    # 5% chance of a significant delay (network spike simulation)
    if random.random() < 0.05:
        delay += random.uniform(1.0, 2.5)

    await asyncio.sleep(delay)


async def get_quote_for_provider(provider: str, weight_g: float, volume: float):
    await simulate_provider_delay(provider)

    # Provider-specific logic (converts weight to kg for pricing)
    weight_kg = weight_g / 1000.0

    if provider == "OutPost":
        # OutPost has strict limits for package lockers
        if weight_kg > 25 or volume > 100000:  # Max 25kg or approx 100L
            return None, "1 day"
        return 15.0 + 1.0 * weight_kg, "1 day"

    elif provider == "LHD":
        if weight_kg > 300:
            return None, "2-3 days"
        return 20.0 + 2.0 * weight_kg, "2-3 days"

    elif provider == "SPU":
        if weight_kg > 20:
            return None, "3-7 days"
        return 10.0 + 0.5 * weight_kg, "3-7 days"

    elif provider == "PDP":
        # PDP handles the heaviest loads
        if weight_kg > 500:
            return None, "1-2 days"
        return 25.0 + 1.5 * weight_kg, "1-2 days"

    return None, "Unknown"
