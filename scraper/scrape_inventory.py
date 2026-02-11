import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timezone


import re
from urllib.parse import urlparse, parse_qs

URL = "https://www.audiwestisland.com/fr/inventaire/occasion/"

def extract_vin(url: str):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return qs.get("vehicleId", [None])[0]

async def scrape_inventory():
    vehicles = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # keep False for debugging
        page = await browser.new_page()

        print("🔄 Loading inventory page...")
        await page.goto(URL, timeout=60000)
        await page.wait_for_selector(
    "div[data-testid='model-name']",
    timeout=60000
)

        cards = await page.locator(
            "div.T3Card-styles__CardContainer-sc-a6ff5dc7-1"
        ).all()

        print(f"🔍 Found {len(cards)} vehicle cards")

        for card in cards:
            try:
                # URL + VIN
                link_el = card.locator("a[href*='vehicleId']").first
                href = await link_el.get_attribute("href")
                if not href:
                    continue

                full_url = (
                    href if href.startswith("http")
                    else "https://www.audiwestisland.com" + href
                )

                vin = extract_vin(full_url)
                if not vin:
                    continue

                # Title
                title = await card.locator(
                    "div[data-testid='model-name']"
                ).inner_text()

                # Trim
                trim = await card.locator(
                    "div[data-testid='trim-name']"
                ).inner_text()

                # Mileage
                mileage_text = await card.locator(
                    "div[data-testid='model-mileage']"
                ).inner_text()
                mileage = int(
                    re.sub(r"[^\d]", "", mileage_text)
                )

                # Price
                price_text = await card.locator(
                 "div.PriceBreakdown-styles__Total-sc-2a8ad1a6-6"
                ).inner_text()

                # "$33,795.00" → 33795
                price = int(float(
                    re.sub(r"[^\d.]", "", price_text)
                ))
                now = datetime.now(timezone.utc)
 
                # Year (from title)
                year_match = re.search(r"(20\d{2})", title)
                year = int(year_match.group(1)) if year_match else None

                vehicles.append({
                    "vin": vin,
                    "title": title.strip(),
                    "trim": trim.strip(),
                    "year": year,
                    "price": price,
                    "mileage_km": mileage,
                    "listing_url": full_url,
                    "website_url": "https://www.audiwestisland.com",
                    "status": "active",
                    "date_scraped": now,
                    "last_seen": now
                })

            except Exception as e:
                print("⚠️ Failed to parse a card:", e)
                continue

        await browser.close()

    print(f"✅ Successfully scraped {len(vehicles)} vehicles")
    return vehicles


if __name__ == "__main__":
    asyncio.run(scrape_inventory())