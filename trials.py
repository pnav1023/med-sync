from pytrials.client import ClinicalTrials
import pandas as pd 
import streamlit as st

# Helper function to fetch clinical trials
def fetch_clinical_trials(drug, disease):
    ct = ClinicalTrials()
    search_expr = f"{drug}+{disease}"
    try:
        fields = ct.get_study_fields(
            search_expr=search_expr,
            fields=["NCT Number", "Conditions", "Study Title", "Study Status", "Phases"],
            max_studies=25,
            fmt="csv",
        )
        return pd.DataFrame.from_records(fields[1:], columns=fields[0])
    except Exception as e:
        st.error(f"An error occurred while fetching clinical trials: {e}")
        return pd.DataFrame()
    
    
    ##available fields
    ##['NCTId', 'BriefTitle', 'NCTId', 'Acronym', 'OverallStatus', 'BriefSummary', '
    # HasResults', 'Condition', 'InterventionType', 'InterventionName', 'PrimaryOutcomeMeasure', '
    # PrimaryOutcomeDescription', 'PrimaryOutcomeTimeFrame', 'SecondaryOutcomeMeasure', '
    # SecondaryOutcomeDescription', 'SecondaryOutcomeTimeFrame', 'OtherOutcomeMeasure', 'OtherOutcomeDescription',
    # 'OtherOutcomeTimeFrame', 'LeadSponsorName', 'CollaboratorName', 'Sex', 'MinimumAge', 'MaximumAge', '
    # StdAge', 'Phase', 'EnrollmentCount', 'LeadSponsorClass', 'StudyType', 'DesignAllocation', '
    # DesignInterventionModel', 'DesignMasking', 'DesignWhoMasked', 'DesignPrimaryPurpose', 'OrgStudyId', '
    # SecondaryId', 'StartDate', 'PrimaryCompletionDate', 'CompletionDate', 'StudyFirstPostDate', '
    # ResultsFirstSubmitDate', 'LastUpdatePostDate', 'LocationFacilit
    # y', 'LocationCity', 'LocationState', 'LocationZip', 'LocationCountry', 'NCTId', 'LargeDocLabel', '
    # LargeDocFilename']}
