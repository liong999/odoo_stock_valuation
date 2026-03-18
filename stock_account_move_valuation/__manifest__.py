{
    "name": "Stock Accounting Move Valuation (Odoo 19)",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Create stock valuation journal entries on picking validation",
    "description": """
        Restores Odoo 18-style stock accounting entry creation for
        real-time valued products when stock pickings are validated.
    """,
    "author": "Liong",
    "website": "https://www.linkedin.com/in/nagara-liong-50ab07136/",
    "depends": [
        "stock_account",
    ],
    "data": [
        "views/product_category_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
    "price": 200000,
    "currency": "IDR"
}
