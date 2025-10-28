# Plan for Government Enquiries — Team 1 Flu Shot Campaign

## Purpose
Produce a concise, formal enquiry plan to request relevant data from government departments (Department of Health, Hospital Authority, Education Bureau, and related agencies) needed for Team 1's analysis of flu vaccination campaign effectiveness and resource allocation.

## Summary of existing materials (from Team1_FluShot)
- Project roadmap and meeting transcripts indicate focus on: vaccination uptake, demographic factors, campaign effectiveness, and targeted interventions for vulnerable groups.
- Current deliverables: roadmap, meeting transcript, README and admin notes; no raw government datasets present in repo.

## Key data needed (missing data)
1. Vaccination participation data
   - Counts of vaccinations by age group, district, and eligibility category (e.g., elderly subsidy, school programs) for years 2017–2024.
   - Temporal granularity: weekly or monthly if available.
2. Vaccination campaign metadata
   - Dates and locations of government-run vaccination sites and outreach events.
   - Resource allocation: number of doses procured/distributed, staff allocation per site.
3. Health outcomes and burden data
   - Number of influenza-related hospitalizations and ICU admissions by age group and district, ideally with vaccination status linkage (de-identified).
   - Laboratory-confirmed influenza case counts (surveillance data) by week/month.
4. School-based program data (Education Bureau)
   - Participation rates per school and school-level identifiers (or aggregated by district), outreach dates, consent procedures.
5. Demographic and healthcare access data
   - Population by age and district, healthcare facility locations and capacities.
6. Survey or behavioral data (if exists)
   - Any government-run surveys on vaccine uptake barriers or acceptance.

## Suggested departments to contact
- Department of Health — Access to vaccination records, surveillance data, campaign metadata.
- Hospital Authority — Hospitalization and severe outcome data; possible linkage with vaccination status (de-identified).
- Education Bureau — School program participation and outreach records.
- Census & Statistics Department — Population/demographic datasets (if not publicly available via data.gov.hk).
- data.gov.hk team — Guidance on available open datasets and licensing.

## Proposed enquiry email template (short version)

Subject: Request for information under Code on Access to Information — Flu Vaccination Campaign Data

Dear Access to Information Officer,

We are undergraduate students from Hong Kong Baptist University enrolled in GCAP3226. As part of our final project we are analysing flu vaccination campaign planning and resource allocation. Under the Code on Access to Information, we respectfully request access to the following datasets (de-identified where applicable):

[Insert numbered list of items from "Key data needed" above]

Please indicate whether the requested datasets are available, the format they can be provided in, any associated fees or application steps, and estimated processing time. If direct data access is not possible, we would also appreciate public reports or aggregated summaries that address these points.

Sincerely,
Team 1 — GCAP3226

## Prioritisation & minimal viable request
If the department requests a narrowed scope, prioritise items 1 (vaccination participation) and 3 (hospitalizations / health outcomes) for causal/effectiveness analysis. Request at least year-level then weekly/monthly if available.

## Proposed timeline
- Draft and review email with supervisors (2 working days)
- Submit enquiries to Department of Health & Hospital Authority (Day 3)
- Follow-up after 10 working days if no response
- Expect data delivery 2–6 weeks depending on scope and approvals

## Notes on privacy and feasibility
- Emphasise de-identified data and research purpose. Offer to sign any data-use agreements if required. Ask for aggregated data if individual-level linkage is not possible.

## Detailed data request specifications
Below are suggested technical specifications and example schemas to include in enquiries. Providing these will make it easier for data custodians to check availability and export the data in a ready-to-use format.

### 1) Vaccination participation data (preferred formats: CSV, JSON, or Excel)
- Required fields (per row):
   - `record_id` (optional, internal id)
   - `date` (ISO 8601 date or YYYY-MM-DD) OR `year` + `week`/`month`
   - `district` (standard district name/code)
   - `age_group` (e.g., 0-4, 5-17, 18-44, 45-64, 65+)
   - `sex` (M/F/Unknown)
   - `eligibility_category` (e.g., elderly_subsidy, school_program, general_public)
   - `vaccination_count` (integer)
   - `vaccine_type` (if available, e.g., inactivated, live_attenuated)
   - `data_source` (e.g., DH_clinic, outreach_event, private_provider)

Example CSV header:
```
date,district,age_group,sex,eligibility_category,vaccination_count,vaccine_type,data_source
2023-10-01,Kowloon,65+,F,elderly_subsidy,123,inactivated,DH_clinic
```

### 2) Vaccination campaign metadata (site-level)
- Required fields (per row):
   - `site_id` (unique identifier)
   - `site_name`
   - `start_date`, `end_date` (YYYY-MM-DD)
   - `district`, `address` (text)
   - `site_type` (fixed_site, mobile_outreach, school, pharmacy)
   - `doses_allocated` (integer)
   - `staff_count` (integer)
   - `partner_organisation` (if any)

### 3) Health outcomes & hospitalization (de-identified; preferred: aggregated by week/month/age_group)
- Required/desired fields:
   - `period` (YYYY-MM or YYYY-W## or start_date/end_date)
   - `district`
   - `age_group`
   - `hospitalizations` (integer)
   - `ICU_admissions` (integer)
   - `deaths` (integer, if available)
   - `vaccinated_hospitalizations` (integer, if linkage exists)
   - `unvaccinated_hospitalizations` (integer, if linkage exists)

### 4) School-based program participation
- Required fields:
   - `school_id` (or anonymised school code)
   - `school_name` (or null if anonymised)
   - `district`
   - `program_date`
   - `eligible_students` (integer)
   - `consented_students` (integer)
   - `vaccinated_students` (integer)

### 5) Demographic & healthcare access
- Fields (aggregated is fine):
   - `district`, `population_total`, `population_by_age_group` (JSON or separate columns)
   - `primary_care_centres` (count)
   - `hospital_beds` (count)

## De-identification guidance and examples
- Request aggregated counts by week/month and age_group to avoid releasing personal data.  
- If individual-level data is necessary, request a fully de-identified dataset with:
   - No names, no ID numbers, no precise addresses (only district-level).  
   - Dates rounded to week/month, or replaced with period codes.  
   - A hashed `pseudo_id` (salted hash) if longitudinal linkage is required, with no key sharing.

## Example JSON schema (vaccination participation)
{
   "type": "object",
   "properties": {
      "date": {"type": "string", "format": "date"},
      "district": {"type": "string"},
      "age_group": {"type": "string"},
      "sex": {"type": "string"},
      "eligibility_category": {"type": "string"},
      "vaccination_count": {"type": "integer"}
   },
   "required": ["date","district","age_group","vaccination_count"]
}

## data.gov.hk / API search tips
- Suggest custodians check data.gov.hk for endpoints such as: vaccination statistics, influenza surveillance, and hospital admissions.  
- If custodians can provide APIs, request REST endpoints (JSON) or periodic CSV exports. Ask for sample API documentation or sample responses.

## Minimal SQL/CSV fields for fast delivery (priority)
If a quick, minimal extract is possible, request a CSV with these columns:
```
period,district,age_group,eligibility_category,vaccination_count,hospitalizations,ICU_admissions
2023-10,Kowloon,65+,elderly_subsidy,123,12,1
```

## Follow-up: sample query text for data custodians
If helpful, include this sample SQL-like request (custodians can adapt to internal schemas):
```
SELECT
   DATE_TRUNC('month', vaccination_date) AS period,
   district_code AS district,
   CASE WHEN age>=65 THEN '65+' WHEN age>=45 THEN '45-64' WHEN age>=18 THEN '18-44' ELSE '0-17' END AS age_group,
   eligibility_category,
   COUNT(*) AS vaccination_count
FROM vaccination_table
WHERE vaccination_date BETWEEN '2017-01-01' AND '2024-12-31'
GROUP BY period, district, age_group, eligibility_category
ORDER BY period;
```


## Next steps (for the team)
1. Review and approve the enquiry template with supervisors.  
2. Finalise prioritized variable list and required time range.  
3. Submit enquiries and log replies (store copy in Google Drive).  
4. Once data are received, clean and document provenance, then proceed to modelling.

---

*Draft generated by analysis of Team1_FluShot materials in repository.*
