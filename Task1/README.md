# Data Cleaning Project

## Problem Statement
Clean a raw dataset by handling missing values, duplicates, and incorrect data.

**Key Requirements:**
- Identify missing or null values
- Remove duplicates
- Correct data formats (dates, numbers, text)

**Key Skills:** Data cleaning, Python (pandas), data preparation

## About the Dataset
`Dataset_for_Data_Analytics.xlsx` contains 1,200 e-commerce order records with 14 columns: OrderID, Date, CustomerID, Product, Quantity, UnitPrice, ShippingAddress, PaymentMethod, OrderStatus, TrackingNumber, ItemsInCart, CouponCode, ReferralSource, and TotalPrice.

## What the Script Does
`clean_dataset.py` runs through the raw file and:

1. **Checks for missing values** in every column
2. **Removes duplicates** — both full duplicate rows and duplicate OrderIDs
3. **Fixes CouponCode** — 309 rows had a blank CouponCode. This isn't bad data, it just means no coupon was used, so it's filled in as `"No Coupon"` instead of being dropped
4. **Cleans text columns** — strips extra whitespace and standardizes capitalization (Product, PaymentMethod, OrderStatus, ReferralSource, OrderID, TrackingNumber)
5. **Fixes date formatting** — converts the Date column to proper datetime values and drops any rows where the date can't be parsed
6. **Fixes number formatting** — rounds UnitPrice and TotalPrice to 2 decimal places, and removes any rows with a Quantity or UnitPrice of 0 or less
7. **Validates TotalPrice** — recalculates TotalPrice as `Quantity x UnitPrice` to catch and fix any mismatches

## Results
- Original rows: 1,200
- Rows after cleaning: 1,200 (no invalid rows had to be dropped)
- Missing values found: 309 (CouponCode only) — all filled
- Duplicate rows found: 0

The dataset turned out to be fairly clean overall, the main real issue was the blank CouponCode values. The script still runs the full cleaning process end to end so it would catch and fix these same issues if run on a messier version of the data.

## How to Run
```bash
pip install pandas openpyxl
python clean_dataset.py
```

Make sure `Dataset_for_Data_Analytics.xlsx` is in the same folder as the script. It will output `Cleaned_Dataset.xlsx` in that same folder.

## Files
```
├── clean_dataset.py               # cleaning script
├── Dataset_for_Data_Analytics.xlsx   # raw data
├── Cleaned_Dataset.xlsx           # output after cleaning
└── README.md
```

