**Duplicate receipt**

- **File:** `receipt-02-coffee.txt`  
- **Parsed data:** vendor = Beacon Hill Beans, date = 2026‑05‑06, total = $9.75, category = Dining  

**Another receipt with the same filename but different content**

- **File:** `receipt-06-coffee.txt`  
- **Parsed data:** vendor = Beacon Hill Beans, date = 2026‑05‑06, total = $9.75, category = Dining  

Both files have the same filename (`coffee`) and were processed on the same day (May 6 2026), but they contain identical transaction details. This indicates a duplicate receipt entry.

**Suspicious receipts**

- None of the parsed receipts show unusually high totals, mismatched dates, or other anomalies that would flag them as suspicious based on vendor, date, amount, or category hint.

**Summary**

- **Duplicate:** `receipt-02-coffee.txt` (and `receipt-06-coffee.txt`) are exact duplicates.  
- No further suspicious activity detected in the current set of receipts.