# Example Prompts

Here are some example prompts to get you started.

## Customer Data

```
Generate customer records with customer_id, name, email, age (18-80), 
city (major world cities), country, phone_number, registration_date 
(2020-2024), total_purchases ($0-$10000), and loyalty_tier 
(Bronze/Silver/Gold/Platinum)
```

## E-commerce Transactions

```
Generate transaction data with transaction_id, date, product_name, 
category (Electronics/Fashion/Home/Sports), quantity (1-5), 
unit_price ($10-$500), payment_method (Card/PayPal/ApplePay), 
and status (Completed/Pending/Cancelled)
```

## Employee Records

```
Generate employee data with employee_id, name, email, department 
(Engineering/Sales/Marketing/HR), position, salary ($40k-$200k), 
hire_date, performance_rating (1-5), and is_remote (true/false)
```

## IoT Sensor Data

```
Generate sensor readings with sensor_id, timestamp, location, 
temperature (15-30°C), humidity (30-70%), battery_level (0-100%), 
and status (Online/Offline/Error)
```

## Healthcare Records (De-identified)

```
Generate patient records with patient_id, age, gender, diagnosis, 
treatment_type, admission_date, discharge_date, department 
(Emergency/Surgery/Cardiology), and recovery_status 
(Recovered/Improving/Critical)
```

## Tips for Better Results

- Be specific about field names and data types
- Include value ranges where relevant (age 18-80, price $10-$100)
- Mention realistic categories for enum fields
- Provide date ranges for time-based data
- Add an example record for complex structures
- Start with 10-20 records to test, then scale up
