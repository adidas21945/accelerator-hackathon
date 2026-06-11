## Headline finding  
**Most common type of 311 complaint in Boston is “Rodent Activity,” accounting for 31 complaints.**

## The data  
- **Dataset:** *311 Service Requests* (all channels) – https://data.boston.gov/dataset/311-service-requests  
- **Date range analyzed:** June 8 2025 – June 2 2026 (the most recent 12‑month period covered by the data).  
- **Rows examined:** 42 total rows; 4 “Duplicate of Existing Case” rows were excluded, leaving **38 valid complaints**.  
- **Dataset URL to reproduce:** https://data.boston.gov/api/3/action/datastore_search?resource_id=254adca6-64ab-4c5c-9fc0-a6da622be185&limit=5000  

## What we found  
1. Rodent Activity – 31 complaints (most common).  
2. Parking Enforcement – 3 complaints.  
3. Requests for Street Cleaning – 2 complaints.  
4. Improper Storage of Trash (Barrels) – 1 complaint.  
5. Request for Pothole Repair – 1 complaint.  

## Caveats  
- **Duplicates excluded:** The analysis removed 4 rows flagged as “Duplicate of Existing Case,” so the counts reflect unique service requests only.  
- **Reporting bias:** Complaints are based on reports to city services; neighborhoods that call 311 more frequently may appear over‑represented, even though the underlying issue could be similar across the city.

## Reproduce it  
Use the exact query URL below to retrieve and re‑run the analysis:

```
https://data.boston.gov/api/3/action/datastore_search?resource_id=254adca6-64ab-4c5c-9fc0-a6da622be185&limit=5000
```