from pytrials.client import ClinicalTrials

ct = ClinicalTrials()


# Get user input for drug and disease
drug_input = input("Enter drug: ")
disease_input = input("Enter disease: ")

# Format the search query with user inputs
search_expr = f"{drug_input}+{disease_input}"

# Assuming ct.get_full_studies is a valid function that fetches studies
ct.get_full_studies(search_expr=search_expr, max_studies=15)


# Get the NCTId, Condition and Brief title fields 
corona_fields = ct.get_study_fields(
    search_expr=search_expr,
    fields=["NCT Number", "Conditions", "Study Title"],
    max_studies=15,
    fmt="csv",
)

# Read the csv data in Pandas
import pandas as pd

x = pd.DataFrame.from_records(corona_fields[1:], columns=corona_fields[0])
print(x)
