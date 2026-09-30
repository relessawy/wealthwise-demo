# Savings API

`GET /api/savings-guidance?target=1200.00&saved=300.00&months=6`

Sign in to WealthWise first. Open **Savings goal → Explore this API in Swagger UI**,
expand the savings endpoint and select **Try it out → Execute**. The browser uses
the same application session; API clients require a valid bearer token.

| Field | Example | Meaning |
| --- | --- | --- |
| target | 1200.00 | Illustrative target amount |
| saved | 300.00 | Amount already saved |
| months | 6 | Whole months remaining, from 1 to 120 |

The remaining amount is 900.00 and the monthly contribution is **150.00**.
Contributions round up to the nearest hundredth. An already reached goal returns
0.00. Negative amounts, more than two decimal places, amounts above 10000000,
and invalid month counts are rejected.

The current guidance is: **Set a regular savings goal and review your progress.**

No interest or fees are modelled. This is a deterministic training calculation,
not financial advice, and does not save customer data.
