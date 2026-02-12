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
        browser = await p.chromium.launch(
            headless=True,
             args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-translate",
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-device-discovery-notifications",
        "--single-process"
    ]
        )

        page = await browser.new_page()

        print("🔄 Loading inventory page...")
        
        await page.route("**/*", lambda route: (
        route.abort()
        if route.request.resource_type in ["image", "stylesheet", "font", "media"]
        else route.continue_()
    ))
        await page.goto(URL, timeout=60000)

        await page.wait_for_selector(
            "div[data-testid='model-name']",
            timeout=60000
        )

        # ---------------------------------
        # HANDLE LOAD MORE BUTTON (SAFE)
        # ---------------------------------

        previous_count = 0

        while True:
            cards = await page.locator(
                "div.T3Card-styles__CardContainer-sc-a6ff5dc7-1"
            ).all()

            current_count = len(cards)

            if current_count == previous_count:
                break

            previous_count = current_count
            print(f"📦 Currently loaded: {current_count}")

            load_more_btn = page.locator(
                "section[class*='LoadMore'] button"
            )

            if await load_more_btn.count() == 0:
                break

            print("🔘 Clicking Load More...")
            await load_more_btn.first.click()
            await page.wait_for_timeout(1200)

        print(f"🔍 Final vehicle count detected: {previous_count}")

        # ---------------------------------
        # SCRAPE VEHICLES
        # ---------------------------------

        cards = await page.locator(
            "div.T3Card-styles__CardContainer-sc-a6ff5dc7-1"
        ).all()

        now = datetime.now(timezone.utc)

        for card in cards:
            try:
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

                title = await card.locator(
                    "div[data-testid='model-name']"
                ).inner_text()

                trim = await card.locator(
                    "div[data-testid='trim-name']"
                ).inner_text()

                mileage_text = await card.locator(
                    "div[data-testid='model-mileage']"
                ).inner_text()

                mileage = int(
                    re.sub(r"[^\d]", "", mileage_text)
                )

                price_text = await card.locator(
                    "div.PriceBreakdown-styles__Total-sc-2a8ad1a6-6"
                ).inner_text()

                price = int(float(
                    re.sub(r"[^\d.]", "", price_text)
                ))

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

# import asyncio
# from playwright.async_api import async_playwright
# from datetime import datetime, timezone
# import re
# from urllib.parse import urlparse, parse_qs

# URL = "https://www.audiwestisland.com/fr/inventaire/occasion/"


# def extract_vin(url: str):
#     parsed = urlparse(url)
#     qs = parse_qs(parsed.query)
#     return qs.get("vehicleId", [None])[0]


# async def scrape_inventory():
#     vehicles = []

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=True,
#             args=["--no-sandbox", "--disable-dev-shm-usage"]
#         )

#         page = await browser.new_page()

#         print("🔄 Loading inventory page...")
#         await page.goto(URL, timeout=60000)

#         await page.wait_for_selector(
#             "div[data-testid='model-name']",
#             timeout=60000
#         )

#         # ----------------------------
#         # INFINITE SCROLL LOGIC
#         # ----------------------------
#         previous_count = 0

#         while True:
#             cards = await page.locator(
#                 "div.T3Card-styles__CardContainer-sc-a6ff5dc7-1"
#             ).all()

#             current_count = len(cards)

#             if current_count == previous_count:
#                 break

#             print(f"📦 Loaded {current_count} vehicles so far...")
#             previous_count = current_count

#             await page.evaluate(
#                 "window.scrollTo(0, document.body.scrollHeight)"
#             )
#             await page.wait_for_timeout(2500)

#         print(f"🔍 Final vehicle count detected: {previous_count}")

#         # ----------------------------
#         # SCRAPE VEHICLES
#         # ----------------------------
#         cards = await page.locator(
#             "div.T3Card-styles__CardContainer-sc-a6ff5dc7-1"
#         ).all()

#         now = datetime.now(timezone.utc)

#         for card in cards:
#             try:
#                 link_el = card.locator("a[href*='vehicleId']").first
#                 href = await link_el.get_attribute("href")
#                 if not href:
#                     continue

#                 full_url = (
#                     href if href.startswith("http")
#                     else "https://www.audiwestisland.com" + href
#                 )

#                 vin = extract_vin(full_url)
#                 if not vin:
#                     continue

#                 title = await card.locator(
#                     "div[data-testid='model-name']"
#                 ).inner_text()

#                 trim = await card.locator(
#                     "div[data-testid='trim-name']"
#                 ).inner_text()

#                 mileage_text = await card.locator(
#                     "div[data-testid='model-mileage']"
#                 ).inner_text()

#                 mileage = int(
#                     re.sub(r"[^\d]", "", mileage_text)
#                 )

#                 price_text = await card.locator(
#                     "div.PriceBreakdown-styles__Total-sc-2a8ad1a6-6"
#                 ).inner_text()

#                 price = int(float(
#                     re.sub(r"[^\d.]", "", price_text)
#                 ))

#                 year_match = re.search(r"(20\d{2})", title)
#                 year = int(year_match.group(1)) if year_match else None

#                 vehicles.append({
#                     "vin": vin,
#                     "title": title.strip(),
#                     "trim": trim.strip(),
#                     "year": year,
#                     "price": price,
#                     "mileage_km": mileage,
#                     "listing_url": full_url,
#                     "website_url": "https://www.audiwestisland.com",
#                     "status": "active",
#                     "date_scraped": now,
#                     "last_seen": now
#                 })

#             except Exception as e:
#                 print("⚠️ Failed to parse a card:", e)
#                 continue

#         await browser.close()

#     print(f"✅ Successfully scraped {len(vehicles)} vehicles")
#     return vehicles


# if __name__ == "__main__":
#     asyncio.run(scrape_inventory())