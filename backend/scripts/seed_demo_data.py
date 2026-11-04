#!/usr/bin/env python3
"""
Seed Fresh Professional Demo Data for Free GST Billing Software
Cleans previous data, resets counters, and writes fresh sample records.
"""
import os
import sys
import json
import shutil
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
INVOICES_DIR = BASE_DIR / "Saved Invoices"
TRASH_DIR = BASE_DIR / "Trash"
SUPPORTERS_JSON = DATA_DIR / "supporters.json"

DIRS_TO_CLEAR = [
    "bills",
    "clients",
    "products",
    "expenses",
    "purchases",
    "purchase-orders",
    "productions",
    "cash-book",
    "receipts",
    "recurring",
    "profiles",
    "trash",
    "backups",
    "cancelled-pdf-originals"
]

def clean_old_data():
    print("Clearing old data and test files...")
    for d in DIRS_TO_CLEAR:
        target_dir = DATA_DIR / d
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
        target_dir.mkdir(parents=True, exist_ok=True)
        
    # Clear Saved Invoices and Trash
    if INVOICES_DIR.exists():
        shutil.rmtree(INVOICES_DIR, ignore_errors=True)
    INVOICES_DIR.mkdir(parents=True, exist_ok=True)
    
    if TRASH_DIR.exists():
        shutil.rmtree(TRASH_DIR, ignore_errors=True)
    TRASH_DIR.mkdir(parents=True, exist_ok=True)
    
    # Reset errors.log
    errors_log = DATA_DIR / "errors.log"
    if errors_log.exists():
        errors_log.unlink()
        
    print("  [OK] Old directories cleared.")

def seed_profile():
    print("Seeding fresh Business Profile...")
    profile = {
        "businessName": "Swapnil Enterprises",
        "address": "Plot No. 42, Okhla Industrial Area, Phase-III, New Delhi",
        "state": "Delhi",
        "gstin": "07AABCS1234F1Z8",
        "pan": "AABCS1234F",
        "email": "billing@swapnil.in",
        "phone": "+91 98110 98110",
        "bankName": "HDFC Bank Ltd.",
        "accountNumber": "50200012345678",
        "ifsc": "HDFC0001234",
        "logo": "",
        "signature": "",
        "upiId": "swapnil@okhdfcbank",
        "googleClientId": "",
        "googleDriveFolder": "GST Billing Invoices",
        "country": "India",
        "paymentAccounts": [
            {
                "id": "acc_primary",
                "bankName": "HDFC Bank Ltd.",
                "accountNumber": "50200012345678",
                "ifsc": "HDFC0001234",
                "upiId": "apextech@okhdfcbank",
                "isDefault": True,
                "label": "Primary Current Account"
            }
        ]
    }
    with open(DATA_DIR / "profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    return profile

def seed_clients():
    print("Seeding Clients...")
    clients = [
        {
            "id": "client_nexus",
            "name": "Nexus Retail Solutions Pvt. Ltd.",
            "state": "Delhi",
            "gstin": "07AAACN5678Q1ZB",
            "pan": "AAACN5678Q",
            "address": "B-12, Connaught Place, Inner Circle",
            "city": "New Delhi",
            "pin": "110001",
            "email": "accounts@nexusretail.in",
            "phone": "+91 98101 12345",
            "country": "India"
        },
        {
            "id": "client_zenith",
            "name": "Zenith Infotech Systems",
            "state": "Maharashtra",
            "gstin": "27AABCZ9876K1ZS",
            "pan": "AABCZ9876K",
            "address": "402, Trade World B-Wing, BKC, Bandra East",
            "city": "Mumbai",
            "pin": "400051",
            "email": "finance@zenithinfotech.com",
            "phone": "+91 98200 54321",
            "country": "India"
        },
        {
            "id": "client_cascade",
            "name": "Cascade Logistics Pvt. Ltd.",
            "state": "Karnataka",
            "gstin": "29AAACC1122D1ZV",
            "pan": "AAACC1122D",
            "address": "88, Electronic City Phase 1, Hosur Road",
            "city": "Bengaluru",
            "pin": "560100",
            "email": "billing@cascadelogistics.com",
            "phone": "+91 99800 77665",
            "country": "India"
        },
        {
            "id": "client_rahul",
            "name": "Rahul Sharma (Retail Client)",
            "state": "Delhi",
            "gstin": "",
            "pan": "",
            "address": "Flat 304, Green Park Extension",
            "city": "New Delhi",
            "pin": "110016",
            "email": "rahul.sharma@gmail.com",
            "phone": "+91 98711 22334",
            "country": "India"
        }
    ]
    for c in clients:
        with open(DATA_DIR / "clients" / f"{c['id']}.json", "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2)
    return {c["id"]: c for c in clients}

def seed_products():
    print("Seeding Products Catalog...")
    products = [
        {
            "id": "prod_server_rack",
            "name": "Cloud Server Rack 42U",
            "kind": "goods",
            "price": 45000.0,
            "stock": 12,
            "unit": "NOS",
            "hsn": "8471",
            "gst": 18.0,
            "purchasePrice": 36000.0,
            "lowStockThreshold": 3
        },
        {
            "id": "prod_router_ac1200",
            "name": "Wireless Gigabit Router AC1200",
            "kind": "goods",
            "price": 3200.0,
            "stock": 45,
            "unit": "NOS",
            "hsn": "8517",
            "gst": 18.0,
            "purchasePrice": 2400.0,
            "lowStockThreshold": 10
        },
        {
            "id": "prod_office_chair",
            "name": "Ergonomic Mesh Office Chair",
            "kind": "goods",
            "price": 8500.0,
            "stock": 18,
            "unit": "NOS",
            "hsn": "9401",
            "gst": 12.0,
            "purchasePrice": 6200.0,
            "lowStockThreshold": 5
        },
        {
            "id": "prod_thermal_rolls",
            "name": "Thermal POS Paper Rolls (80mm Pack of 10)",
            "kind": "goods",
            "price": 450.0,
            "stock": 150,
            "unit": "PAC",
            "hsn": "4811",
            "gst": 5.0,
            "purchasePrice": 320.0,
            "lowStockThreshold": 25
        },
        {
            "id": "prod_annual_amc",
            "name": "IT Infrastructure Annual Maintenance (AMC)",
            "kind": "service",
            "price": 12000.0,
            "unit": "NOS",
            "sac": "9987",
            "gst": 18.0
        },
        {
            "id": "prod_consultation",
            "name": "GST & Systems Cloud Consultation",
            "kind": "service",
            "price": 4000.0,
            "unit": "HRS",
            "sac": "9983",
            "gst": 18.0
        }
    ]
    for p in products:
        with open(DATA_DIR / "products" / f"{p['id']}.json", "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2)
    return {p["id"]: p for p in products}

def seed_bills(profile, clients, products):
    print("Seeding Invoices...")
    today = datetime.date.today()
    y_str = f"{today.year if today.month >= 4 else today.year - 1}-{str((today.year if today.month >= 4 else today.year - 1) + 1)[-2:]}"
    
    # 1. Delhi Intra-state (CGST 9% + SGST 9%) - Paid
    inv_1_num = f"INV/{y_str}/0001"
    inv_1 = {
        "id": inv_1_num,
        "invoiceNumber": inv_1_num,
        "clientName": clients["client_nexus"]["name"],
        "invoiceDate": (today - datetime.timedelta(days=12)).isoformat(),
        "invoiceType": "tax-invoice",
        "currency": "INR",
        "totalAmount": 53100.0,
        "totalTaxAmount": 8100.0,
        "status": "paid",
        "paidAmount": 53100.0,
        "payments": [
            {
                "id": "pay_01",
                "amount": 53100.0,
                "date": (today - datetime.timedelta(days=10)).isoformat(),
                "mode": "bank-transfer",
                "reference": "HDFC-NEFT-9912",
                "note": "Full payment received"
            }
        ],
        "data": {
            "profile": profile,
            "client": clients["client_nexus"],
            "details": {
                "invoiceNumber": inv_1_num,
                "invoiceDate": (today - datetime.timedelta(days=12)).isoformat(),
                "dueDate": (today + datetime.timedelta(days=3)).isoformat(),
                "placeOfSupply": "07-Delhi"
            },
            "items": [
                {
                    "name": products["prod_server_rack"]["name"],
                    "hsn": "8471",
                    "rate": 45000.0,
                    "qty": 1,
                    "unit": "NOS",
                    "gst": 18.0,
                    "taxable": 45000.0,
                    "cgst": 4050.0,
                    "sgst": 4050.0,
                    "igst": 0.0,
                    "total": 53100.0
                }
            ],
            "totals": {
                "subtotal": 45000.0,
                "taxableAmount": 45000.0,
                "totalCgst": 4050.0,
                "totalSgst": 4050.0,
                "totalIgst": 0.0,
                "totalTaxAmount": 8100.0,
                "roundOff": 0.0,
                "total": 53100.0
            }
        }
    }
    
    # 2. Maharashtra Inter-state (IGST 18%) - Partly Paid
    inv_2_num = f"INV/{y_str}/0002"
    inv_2 = {
        "id": inv_2_num,
        "invoiceNumber": inv_2_num,
        "clientName": clients["client_zenith"]["name"],
        "invoiceDate": (today - datetime.timedelta(days=5)).isoformat(),
        "invoiceType": "tax-invoice",
        "currency": "INR",
        "totalAmount": 18880.0,
        "totalTaxAmount": 2880.0,
        "status": "partial",
        "paidAmount": 10000.0,
        "payments": [
            {
                "id": "pay_02",
                "amount": 10000.0,
                "date": (today - datetime.timedelta(days=2)).isoformat(),
                "mode": "upi",
                "reference": "UPI-REF-45812",
                "note": "Part advance payment"
            }
        ],
        "data": {
            "profile": profile,
            "client": clients["client_zenith"],
            "details": {
                "invoiceNumber": inv_2_num,
                "invoiceDate": (today - datetime.timedelta(days=5)).isoformat(),
                "dueDate": (today + datetime.timedelta(days=10)).isoformat(),
                "placeOfSupply": "27-Maharashtra"
            },
            "items": [
                {
                    "name": products["prod_router_ac1200"]["name"],
                    "hsn": "8517",
                    "rate": 3200.0,
                    "qty": 5,
                    "unit": "NOS",
                    "gst": 18.0,
                    "taxable": 16000.0,
                    "cgst": 0.0,
                    "sgst": 0.0,
                    "igst": 2880.0,
                    "total": 18880.0
                }
            ],
            "totals": {
                "subtotal": 16000.0,
                "taxableAmount": 16000.0,
                "totalCgst": 0.0,
                "totalSgst": 0.0,
                "totalIgst": 2880.0,
                "totalTaxAmount": 2880.0,
                "roundOff": 0.0,
                "total": 18880.0
            }
        }
    }
    
    # 3. Karnataka Inter-state - Unpaid
    inv_3_num = f"INV/{y_str}/0003"
    inv_3 = {
        "id": inv_3_num,
        "invoiceNumber": inv_3_num,
        "clientName": clients["client_cascade"]["name"],
        "invoiceDate": today.isoformat(),
        "invoiceType": "tax-invoice",
        "currency": "INR",
        "totalAmount": 9520.0,
        "totalTaxAmount": 1020.0,
        "status": "unpaid",
        "paidAmount": 0.0,
        "payments": [],
        "data": {
            "profile": profile,
            "client": clients["client_cascade"],
            "details": {
                "invoiceNumber": inv_3_num,
                "invoiceDate": today.isoformat(),
                "dueDate": (today + datetime.timedelta(days=15)).isoformat(),
                "placeOfSupply": "29-Karnataka"
            },
            "items": [
                {
                    "name": products["prod_office_chair"]["name"],
                    "hsn": "9401",
                    "rate": 8500.0,
                    "qty": 1,
                    "unit": "NOS",
                    "gst": 12.0,
                    "taxable": 8500.0,
                    "cgst": 0.0,
                    "sgst": 0.0,
                    "igst": 1020.0,
                    "total": 9520.0
                }
            ],
            "totals": {
                "subtotal": 8500.0,
                "taxableAmount": 8500.0,
                "totalCgst": 0.0,
                "totalSgst": 0.0,
                "totalIgst": 1020.0,
                "totalTaxAmount": 1020.0,
                "roundOff": 0.0,
                "total": 9520.0
            }
        }
    }
    
    bills = [inv_1, inv_2, inv_3]
    for b in bills:
        safe_name = b["id"].replace('/', '_') + ".json"
        with open(DATA_DIR / "bills" / safe_name, "w", encoding="utf-8") as f:
            json.dump(b, f, indent=2)
            
    # Meta counter
    meta = {
        "counter_INV": 3,
        "invoiceNumberSettings": {
            "format": "branded",
            "brandPrefix": "INV",
            "separator": "/",
            "showFinYear": True,
            "startNumber": 1,
            "padDigits": 4
        }
    }
    with open(DATA_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def seed_expenses():
    print("Seeding Business Expenses...")
    today = datetime.date.today()
    expenses = [
        {
            "id": "exp_airtel_fiber",
            "title": "Airtel Broadband High-Speed Leased Line",
            "category": "Utilities",
            "date": (today - datetime.timedelta(days=8)).isoformat(),
            "amount": 3540.0,
            "vendor": "Bharti Airtel Ltd.",
            "paymentMode": "bank-transfer",
            "hasGst": True,
            "gstin": "07AABCB2854L1ZT",
            "taxable": 3000.0,
            "gstAmount": 540.0,
            "itcEligible": True
        },
        {
            "id": "exp_stationery",
            "title": "Stationery & Printer Paper Cartridges",
            "category": "Office",
            "date": (today - datetime.timedelta(days=3)).isoformat(),
            "amount": 1250.0,
            "vendor": "Rajdhani Stationers Okhla",
            "paymentMode": "cash",
            "hasGst": False
        },
        {
            "id": "exp_electricity",
            "title": "BSES Rajdhani Electricity Office Bill",
            "category": "Electricity",
            "date": (today - datetime.timedelta(days=1)).isoformat(),
            "amount": 6400.0,
            "vendor": "BSES Rajdhani Power Ltd.",
            "paymentMode": "upi",
            "hasGst": False
        }
    ]
    for e in expenses:
        with open(DATA_DIR / "expenses" / f"{e['id']}.json", "w", encoding="utf-8") as f:
            json.dump(e, f, indent=2)

def seed_purchases():
    print("Seeding Purchases...")
    today = datetime.date.today()
    purchase = {
        "id": "pur_tech_hardware",
        "supplierName": "National Tech Hardware Wholesalers",
        "invoiceNumber": "NTHW/2026/0441",
        "date": (today - datetime.timedelta(days=15)).isoformat(),
        "totalAmount": 47200.0,
        "tdsAmount": 0.0,
        "paymentStatus": "Partial",
        "payments": [
            {
                "id": "ppay_01",
                "amount": 25000.0,
                "date": (today - datetime.timedelta(days=14)).isoformat(),
                "mode": "bank-transfer",
                "reference": "RTGS-55441",
                "note": "First installment paid"
            }
        ]
    }
    with open(DATA_DIR / "purchases" / f"{purchase['id']}.json", "w", encoding="utf-8") as f:
        json.dump(purchase, f, indent=2)

def seed_cash_book():
    print("Seeding Cash Book...")
    today = datetime.date.today()
    entries = [
        {
            "id": "cash_entry_01",
            "type": "in",
            "date": (today - datetime.timedelta(days=4)).isoformat(),
            "amount": 4500.0,
            "name": "Counter POS Cash Sales",
            "category": "Sales",
            "note": "10 rolls + patch cables sale"
        },
        {
            "id": "cash_entry_02",
            "type": "out",
            "date": (today - datetime.timedelta(days=2)).isoformat(),
            "amount": 380.0,
            "name": "Office Chai, Coffee & Refreshments",
            "category": "Office",
            "note": "Vendor weekly tea settlement"
        },
        {
            "id": "cash_entry_03",
            "type": "out",
            "date": today.isoformat(),
            "amount": 240.0,
            "name": "Speed Post Courier Charges",
            "category": "Logistics",
            "note": "Invoice hardcopy dispatch"
        }
    ]
    for c in entries:
        with open(DATA_DIR / "cash-book" / f"{c['id']}.json", "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2)

def seed_recurring(clients, products):
    print("Seeding Recurring Billing Template...")
    today = datetime.date.today()
    rec = {
        "id": "rec_nexus_amc",
        "clientName": clients["client_nexus"]["name"],
        "clientState": clients["client_nexus"]["state"],
        "clientGstin": clients["client_nexus"]["gstin"],
        "frequency": "monthly",
        "interval": 1,
        "nextDate": (today + datetime.timedelta(days=18)).isoformat(),
        "totalAmount": 14160.0,
        "totalTaxAmount": 2160.0,
        "active": True,
        "invoiceType": "tax-invoice",
        "items": [
            {
                "name": products["prod_annual_amc"]["name"],
                "rate": 12000.0,
                "qty": 1,
                "gst": 18.0
            }
        ]
    }
    with open(DATA_DIR / "recurring" / f"{rec['id']}.json", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)

def seed_templates():
    print("Seeding Standard Terms & Conditions...")
    tpl = {
        "id": "default",
        "name": "Commercial Terms & Payment Conditions",
        "content": (
            "1. Payment is due within 15 days of invoice date unless agreed otherwise in writing.\n"
            "2. Interest @ 18% p.a. will be chargeable on delayed payments past the due date.\n"
            "3. Goods once sold will not be taken back or exchanged unless damaged in transit.\n"
            "4. All warranty services will be honored as per original manufacturer terms.\n"
            "5. Subject to Delhi jurisdiction only. E. & O.E."
        )
    }
    with open(DATA_DIR / "templates" / "default.json", "w", encoding="utf-8") as f:
        json.dump(tpl, f, indent=2)

def reset_supporters():
    print("Resetting supporters list...")
    data = {
        "currency": "INR",
        "totalReceived": 0,
        "supporters": 0,
        "goal": {
            "amount": 50000,
            "label": "Open-Source GST Billing Software"
        },
        "thanks": [],
        "updated": datetime.date.today().isoformat(),
        "people": []
    }
    with open(SUPPORTERS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    print("\n========================================================")
    print("  INITIALIZING CLEAN DEMO ENVIRONMENT")
    print("========================================================\n")
    clean_old_data()
    profile = seed_profile()
    clients = seed_clients()
    products = seed_products()
    seed_bills(profile, clients, products)
    seed_expenses()
    seed_purchases()
    seed_cash_book()
    seed_recurring(clients, products)
    seed_templates()
    reset_supporters()
    print("\n========================================================")
    print("  FRESH DEMO DATA GENERATED SUCCESSFULLY!")
    print("========================================================\n")

if __name__ == "__main__":
    main()
