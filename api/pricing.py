REGIONAL_MULTIPLIERS = {"IN": 1.0, "US": 1.25, "GB": 1.20, "DE": 1.22, "SG": 1.10}
CURRENCIES = {"IN":"INR","US":"USD","GB":"GBP","DE":"EUR","SG":"SGD"}

PLANS = [
    {"name":"Free","price":0,"currency":"INR","period":"forever",
     "features":["Idea-to-project planner","Component catalog","Cost calculator","Local saved projects","Basic code generation"]},
    {"name":"Premium Monthly","price":99,"currency":"INR","period":"month",
     "features":["Everything in Free","Advanced AI generation when configured","Advanced project tools","Extended simulations"]},
    {"name":"Premium Annual","price":799,"currency":"INR","period":"year",
     "features":["Everything in Free","Advanced AI generation when configured","Advanced project tools","Extended simulations"]},
]

def regional_price(price, country):
    return round(price * REGIONAL_MULTIPLIERS.get(country.upper(), 1.15), 2)

def plans_for_country(country):
    country = country.upper()
    currency = CURRENCIES.get(country, "INR")
    return [{**p, "price": regional_price(p["price"], country), "currency": currency} for p in PLANS]
