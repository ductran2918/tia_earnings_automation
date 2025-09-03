# Problem 

The conversion feature now works. But the extracted financial data also was converted to USD so I cannot if the tool extract right data from PDFs or not. 

## Sample output 

 Extracted Financial Data
{
"year_1":{
"year":"2023"
"revenue":32641196
"profit_before_tax":-20230767
"profit_after_tax":-20230767
"net_cash_operating":-14616804
"net_cash_investing":-363021
"net_cash_financing":-1447682
"cash_end_of_year":28813653
}
"year_2":{
"year":"2022"
"revenue":32957514
"profit_before_tax":-16618260
"profit_after_tax":-16618260
"net_cash_operating":-13115700
"net_cash_investing":-111808
"net_cash_financing":45221228
"cash_end_of_year":44366439
}
"currencies":[
0:"S$"
]
"company_name":"Glints Pte. Ltd."
"report_type":"Annual Report"
}

💱 Currency Conversion (SGD → USD)
Exchange Rates Used: 2023: 0.74572, 2022: 0.72579

{
"year_1":{
"year":"2023"
"revenue":32641196
"profit_before_tax":-20230767
"profit_after_tax":-20230767
"net_cash_operating":-14616804
"net_cash_investing":-363021
"net_cash_financing":-1447682
"cash_end_of_year":28813653
}
"year_2":{
"year":"2022"
"revenue":32957514
"profit_before_tax":-16618260
"profit_after_tax":-16618260
"net_cash_operating":-13115700
"net_cash_investing":-111808
"net_cash_financing":45221228
"cash_end_of_year":44366439
}
"currencies":[
0:"USD"
]
"company_name":"Glints Pte. Ltd."
"report_type":"Annual Report"
"original_currencies":[
0:"S$"
]
"exchange_rates_used":{
"2022":0.72579
"2023":0.74572
}
}

# Solution
I want you to separate the logic sequence into each step
## Step 1
Extract raw data from PDF by LLM. Then save the output as a json file called "raw_data.json"

## Step 2
Convert all numeric keys in raw_data.json to usd by current coversion logic. save the output of this step as a file called "usd_converted_data.json" 

# Expected outputs
On the front-end, I will see raw extracted data in SGD and coverted data in SGD. You don't change extracted output. 
Two json file of step 1 and step 2 will be save into a temporary folder. 

Before implement this step, clear all files in .tmp folder for cleaner repo. 