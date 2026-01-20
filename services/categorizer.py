from typing import List, Dict
import re


def clean_description(description: str) -> str:
    """
    Clean transaction description by removing transaction codes and extra whitespace

    Examples:
        "DEBIT CARD PURCHASE 121424 5811121424 CHIPOTLE" -> "chipotle"
        "POS DEBIT 122024 5411122024 TARGET" -> "target"
    """
    desc = description.lower()

    # Remove common transaction prefixes
    desc = re.sub(
        r"(debit card purchase|pos debit|recurring deb card purch|ach withdrawal|ach dep|payment receipt credit|usaa credit|usaa debit|wire transfer credit)",
        "",
        desc,
    )

    # Remove transaction codes (6-10 digit numbers)
    desc = re.sub(r"\b\d{6,10}\b", "", desc)

    # Remove asterisks and extra whitespace
    desc = re.sub(r"\*+", "", desc)
    desc = re.sub(r"\s+", " ", desc).strip()

    return desc


# Category rules - keyword matching
# IMPORTANT: Order matters! Specific keywords are checked first, then generic ones
CATEGORY_RULES = {
    # Software & Tools - CHECK FIRST (before "amazon" in Shopping)
    "Software": [
        "aws",
        "amazon web services",
        "azure",
        "google cloud",
        "google workspace",
        "github",
        "gitlab",
        "slack",
        "zoom",
        "microsoft 365",
        "office 365",
        "adobe",
        "dropbox",
        "docusign",
        "quickbooks",
        "salesforce",
        "shopify",
        "squarespace",
        "wix",
        "godaddy",
        "namecheap",
        "heroku",
        "vercel",
        "netlify",
        "digitalocean",
        "linode",
    ],
    # Subscriptions - Common streaming/subscription services
    "Subscriptions": [
        "hulu",
        "netflix",
        "spotify",
        "apple.com/bill",
        "apple music",
        "apple tv",
        "disney+",
        "disney plus",
        "youtube",
        "youtube premium",
        "amazon prime",
        "hbo max",
        "paramount",
        "peacock",
        "discovery+",
        "crunchyroll",
        "icloud",
        "google one",
        "audible",
        "kindle unlimited",
        "scribd",
        "pixieset",
        "patreon",
        "onlyfans",
        "twitch",
    ],
    # Revenue/Income
    "Revenue": [
        "payroll",
        "salary",
        "deposit",
        "payment received",
        "payment receipt credit",
        "venmo",
        "zelle",
        "paypal",
        "stripe",
        "square",
        "invoice",
        "check deposit",
        "direct deposit",
        "ach credit",
        "wire transfer credit",
        "robinhood securities",
        "promotional credit",
        "canno payroll",
    ],
    # Debt Payments - Loans, credit cards, etc
    "Debt Payments": [
        "loan payment",
        "mortgage",
        "student loan",
        "car payment",
        "auto loan",
        "credit card payment",
        "applecard",
        "discover e-payment",
        "chase credit",
        "citi card",
        "capital one",
        "amex",
        "synchrony",
        "barclays",
        "bk of amer visa",
        "wells fargo payment",
        "usaa loan payment",
    ],
    # Fitness & Health
    "Fitness": [
        "gym",
        "fitness",
        "yoga",
        "pilates",
        "crossfit",
        "equinox",
        "f45",
        "orangetheory",
        "peloton",
        "crunch",
        "planet fitness",
        "la fitness",
        "24 hour fitness",
        "anytime fitness",
        "eos fitness",
        "gold's gym",
        "lifetime fitness",
        "climbing",
        "boxing",
        "martial arts",
        "tennis",
    ],
    # Gas & Fuel - Include convenience stores that sell gas
    "Gas & Fuel": [
        "gas",
        "fuel",
        "shell",
        "chevron",
        "exxon",
        "mobil",
        "bp",
        "texaco",
        "circle k",
        "7-eleven",
        "speedway",
        "wawa",
        "qt ",
        "quiktrip",
        "costco gas",
        "sam's club gas",
        "arco",
        "valero",
        "sunoco",
        "marathon",
        "phillips 66",
        "conoco",
        "pilot",
        "flying j",
        "outside",
        "pump",  # Often appears in gas purchases
    ],
    # Fast Food & Quick Service - Major chains
    "Fast Food": [
        "mcdonalds",
        "mcdonald's",
        "burger king",
        "wendy's",
        "taco bell",
        "chick-fil-a",
        "chick fil a",
        "popeyes",
        "kfc",
        "chipotle",
        "panda express",
        "subway",
        "arby's",
        "sonic",
        "jack in the box",
        "in-n-out",
        "five guys",
        "shake shack",
        "raising cane",
        "canes",
        "del taco",
        "qdoba",
        "moe's",
        "jersey mike",
        "jimmy john",
        "panera",
        "panera bread",
        "dunkin",
        "dunkin donuts",
        "starbucks",
        "dutch bros",
        "caribou coffee",
    ],
    # Restaurants & Dining (Sit-down, bars, etc)
    "Restaurants": [
        "restaurant",
        "cafe",
        "bistro",
        "grill",
        "tavern",
        "bar",
        "pub",
        "steakhouse",
        "sushi",
        "pizza",
        "mexican",
        "italian",
        "chinese",
        "thai",
        "indian",
        "japanese",
        "uchi",
        "taco boys",
        "bahama bucks",
        "sotol",
        "applebee",
        "chili's",
        "olive garden",
        "red lobster",
        "outback",
        "texas roadhouse",
        "longhorn",
        "cheesecake factory",
        "bj's restaurant",
        "buffalo wild wings",
        "hooters",
        "twin peaks",
        "yard house",
        "365 market",
    ],
    # Food Delivery
    "Food Delivery": [
        "doordash",
        "uber eats",
        "grubhub",
        "postmates",
        "seamless",
        "instacart",
        "gopuff",
        "favor",
        "waitr",
        "bite squad",
    ],
    # Groceries
    "Groceries": [
        "grocery",
        "supermarket",
        "whole foods",
        "trader joe",
        "safeway",
        "kroger",
        "publix",
        "albertsons",
        "food lion",
        "wegmans",
        "aldi",
        "lidl",
        "fresh market",
        "sprouts",
        "natural grocers",
        "harris teeter",
    ],
    # Shopping - General retail
    "Shopping": [
        "walmart",
        "target",
        "costco",
        "sam's club",
        "bj's wholesale",
        "amazon",
        "amzn mktp",
        "ebay",
        "etsy",
        "macy's",
        "nordstrom",
        "kohl's",
        "jcpenney",
        "dillard's",
        "tj maxx",
        "ross",
        "marshalls",
        "burlington",
        "old navy",
        "gap",
        "banana republic",
        "h&m",
        "zara",
        "forever 21",
        "urban outfitters",
        "anthropologie",
        "free people",
        "klarna",
        "afterpay",
        "affirm",
        "gymshark",
        "pandora",
    ],
    # Healthcare
    "Healthcare": [
        "pharmacy",
        "cvs",
        "walgreens",
        "rite aid",
        "duane reade",
        "doctor",
        "hospital",
        "medical",
        "dental",
        "dentist",
        "vision",
        "optometry",
        "urgent care",
        "clinic",
        "lab",
        "laboratory",
        "physical therapy",
        "chiropractor",
        "therapist",
        "counseling",
        "health",
        "ro health",
        "hims",
        "hers",
        "nurx",
        "lemonaid",
    ],
    # Entertainment
    "Entertainment": [
        "movie",
        "cinema",
        "theater",
        "theatre",
        "concert",
        "show",
        "live nation",
        "ticketmaster",
        "stubhub",
        "amc",
        "regal",
        "cinemark",
        "imax",
        "bowling",
        "arcade",
        "dave & buster",
        "main event",
        "topgolf",
        "golf",
        "mini golf",
        "escape room",
        "trampoline park",
        "theme park",
        "amusement",
        "zoo",
        "aquarium",
        "museum",
    ],
    # Personal Care
    "Personal Care": [
        "salon",
        "haircut",
        "barber",
        "spa",
        "massage",
        "nail",
        "manicure",
        "pedicure",
        "waxing",
        "facial",
        "beauty",
        "cosmetics",
        "sephora",
        "ulta",
        "bath & body",
        "lush",
        "maestros barber",
    ],
    # Pet Care
    "Pet Care": [
        "pet",
        "veterinary",
        "vet",
        "petsmart",
        "petco",
        "chewy",
        "dog",
        "cat",
        "animal hospital",
        "grooming",
    ],
    # Education
    "Education": [
        "tuition",
        "school",
        "university",
        "college",
        "academy",
        "course",
        "udemy",
        "coursera",
        "skillshare",
        "masterclass",
        "linkedin learning",
        "pluralsight",
        "datacamp",
        "bootcamp",
    ],
    # Childcare
    "Childcare": ["daycare", "childcare", "babysitter", "nanny", "tutor", "tutoring"],
    # Home & Garden
    "Home & Garden": [
        "home depot",
        "lowes",
        "lowe's",
        "ace hardware",
        "menards",
        "home improvement",
        "garden",
        "landscaping",
        "lawn",
        "nursery",
        "ikea",
        "bed bath",
        "crate and barrel",
        "williams sonoma",
        "pottery barn",
        "west elm",
        "wayfair",
        "overstock",
    ],
    # Transportation - Rideshare, transit, parking
    "Transportation": [
        "uber",
        "lyft",
        "taxi",
        "cab",
        "bus",
        "train",
        "metro",
        "subway",
        "transit",
        "parking",
        "park",
        "toll",
        "ez pass",
        "fastrak",
        "parking.com",
        "parkwhiz",
        "spothero",
    ],
    # Travel - Hotels, flights, rental cars
    "Travel": [
        "airline",
        "flight",
        "airport",
        "hotel",
        "motel",
        "resort",
        "airbnb",
        "vrbo",
        "booking.com",
        "expedia",
        "hotels.com",
        "marriott",
        "hilton",
        "hyatt",
        "ihg",
        "best western",
        "southwest",
        "delta",
        "united",
        "american airlines",
        "jetblue",
        "spirit",
        "frontier",
        "alaska airlines",
        "rental car",
        "hertz",
        "enterprise",
        "budget",
        "avis",
        "national",
        "alamo",
        "dollar",
        "thrifty",
        "turo",
        "zipcar",
    ],
    # Investments & Trading
    "Investments": [
        "robinhood",
        "coinbase",
        "crypto",
        "bitcoin",
        "ethereum",
        "etrade",
        "schwab",
        "fidelity",
        "vanguard",
        "ameritrade",
        "webull",
        "acorns",
        "stash",
        "betterment",
        "wealthfront",
        "jpms llc",
        "jpmorgan",
        "mspbna",
    ],
    # Cost of Goods Sold (for businesses)
    "COGS": [
        "inventory",
        "supplies",
        "wholesale",
        "materials",
        "merchandise",
        "stock",
        "vendor",
    ],
    # Marketing & Advertising
    "Marketing": [
        "google ads",
        "facebook ads",
        "meta ads",
        "instagram ads",
        "linkedin ads",
        "twitter ads",
        "tiktok ads",
        "pinterest ads",
        "reddit ads",
        "marketing",
        "advertising",
        "promotion",
        "campaign",
        "mailchimp",
        "constant contact",
        "sendinblue",
        "convertkit",
        "hubspot",
        "semrush",
        "ahrefs",
        "moz",
    ],
    # Office & Equipment
    "Office": [
        "staples",
        "office depot",
        "office max",
        "best buy",
        "apple store",
        "dell",
        "hp",
        "lenovo",
        "microsoft store",
        "furniture",
        "desk",
        "chair",
        "monitor",
        "laptop",
        "printer",
        "computer",
    ],
    # Rent & Utilities
    "Rent": ["rent", "lease", "property", "landlord", "real estate", "apartment"],
    "Utilities": [
        "electric",
        "electricity",
        "gas company",
        "water",
        "sewer",
        "trash",
        "internet",
        "broadband",
        "wifi",
        "phone",
        "mobile",
        "cellular",
        "at&t",
        "verizon",
        "t-mobile",
        "sprint",
        "cricket",
        "boost mobile",
        "metro pcs",
        "comcast",
        "xfinity",
        "spectrum",
        "cox",
        "optimum",
        "centurylink",
        "frontier",
        "dish",
        "directv",
    ],
    # Insurance
    "Insurance": [
        "insurance",
        "policy",
        "premium",
        "usaa insurance",
        "state farm",
        "geico",
        "progressive",
        "allstate",
        "farmers",
        "liberty mutual",
        "nationwide",
        "travelers",
        "american family",
        "health insurance",
        "auto insurance",
        "car insurance",
        "life insurance",
        "dental insurance",
        "vision insurance",
    ],
    # Professional Services
    "Professional Services": [
        "attorney",
        "lawyer",
        "legal",
        "accountant",
        "cpa",
        "tax prep",
        "consultant",
        "consulting",
        "freelancer",
        "contractor",
        "agency",
        "upwork",
        "fiverr",
        "thumbtack",
        "taskrabbit",
    ],
    # Bank Fees
    "Bank Fees": [
        "fee",
        "service charge",
        "atm fee",
        "overdraft",
        "wire fee",
        "interest charge",
        "monthly fee",
        "maintenance fee",
        "transfer fee",
        "acctverify",
    ],
    # Payroll (for business owners)
    "Payroll": [
        "gusto",
        "adp",
        "paychex",
        "payroll",
        "employee",
        "wages",
        "salary payment",
        "paycom",
        "rippling",
        "bamboohr",
        "zenefits",
    ],
    # Taxes
    "Taxes": [
        "irs",
        "tax",
        "federal tax",
        "state tax",
        "sales tax",
        "payroll tax",
        "estimated tax",
        "quarterly tax",
        "franchise tax",
        "property tax",
    ],
}


def categorize_transaction(description: str, amount: float) -> str:
    """
    Categorize a single transaction based on its description

    Returns:
        Category name (str)
    """

    # Clean the description first (removes transaction codes, etc)
    cleaned_desc = clean_description(description)
    description_lower = description.lower()

    # Check each category's keywords (using both cleaned and original)
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in cleaned_desc or keyword in description_lower:
                return category

    # Default categorization based on amount sign
    if amount > 0:
        return "Income"
    elif abs(amount) < 5:
        return "Small Expense"  # Under $5, probably not worth categorizing
    else:
        return "Other Expense"


def categorize_transactions(transactions: List[Dict]) -> List[Dict]:
    """
    Add category to each transaction

    Args:
        transactions: List of transaction dicts

    Returns:
        Same list with 'category' field added to each transaction
    """

    for transaction in transactions:
        category = categorize_transaction(
            transaction["description"], transaction["amount"]
        )
        transaction["category"] = category

    return transactions


def get_category_summary(transactions: List[Dict]) -> Dict[str, float]:
    """
    Calculate total amount per category

    Returns:
        Dictionary mapping category name to total amount
    """

    summary = {}

    for transaction in transactions:
        category = transaction.get("category", "Other")
        amount = transaction["amount"]

        if category in summary:
            summary[category] += amount
        else:
            summary[category] = amount

    return summary


def get_monthly_summary(transactions: List[Dict]) -> Dict[str, Dict]:
    """
    Calculate monthly cash flow summary

    Returns:
        Dictionary mapping month to {revenue, expenses, net_income}
    """

    monthly = {}

    for transaction in transactions:
        # Extract month (YYYY-MM)
        month = transaction["date"][:7]

        if month not in monthly:
            monthly[month] = {"revenue": 0, "expenses": 0, "net_income": 0}

        amount = transaction["amount"]

        if amount > 0:
            monthly[month]["revenue"] += amount
        else:
            monthly[month]["expenses"] += abs(amount)

    # Calculate net income for each month
    for month in monthly:
        monthly[month]["net_income"] = (
            monthly[month]["revenue"] - monthly[month]["expenses"]
        )

    return monthly
