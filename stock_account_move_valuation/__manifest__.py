{
    "name": "Stock Accounting Move Valuation (Odoo 19)",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Create stock valuation journal entries on picking validation",
    "description": """
        Creates stock valuation journal entries when validating stock pickings
        for real-time valued product categories.
    """,
    "author": "Liong",
    "website": "https://www.linkedin.com/in/nagara-liong-50ab07136/",
    "depends": [
        "stock_account",
    ],
    "data": [
        "views/product_category_view.xml",
    ],
    "images": [
        "static/description/main_screenshot.png",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
