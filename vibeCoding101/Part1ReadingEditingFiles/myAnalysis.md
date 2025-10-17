# Team 6 — Bus Stop Merge: Policy Issues Analysis

This document summarizes the key policy issues and recommended next steps based on Team 6's project materials and the Bus-Stop-Optimization resources (case study: St. Martin Road and Chong San Road, 52 meters apart), including available simulation and empirical assets.

1. Executive summary (quick recap)
Team 6 builds on a comprehensive research foundation (master's thesis, Python discrete-event simulation, KMB Open Data API) to evaluate the efficiency and accessibility impacts of merging bus stops. Four scenarios have been analyzed (current setup, designated routes, merged superstation, single-station), supported by 100+ simulation runs and statistical summaries.

2. Core policy issues

- Accessibility and equity
	- Stop merging can reduce total travel time and operating costs, but it may increase walking distance/time for certain passenger groups (people with reduced mobility, older adults, caregivers with children). Policy evaluation should quantify who is affected, how much, and the socioeconomic vulnerability of affected groups.

- Disability and inclusive access
	- Walking routes must be checked for accessible infrastructure (ramps, sidewalks, marked crossings, lifts/ramps where applicable). If merging causes significant hardship for mobility-impaired users, exemptions or mitigating measures are required (e.g., retain stops at specific locations or provide shuttle services).

- Decision thresholds and measurable metrics
	- Authorities should define clear indicators and thresholds (e.g., maximum acceptable walking distance, allowable percentage change in average wait time, maximum number of affected residents in low-income areas) to guide merge decisions and avoid relying solely on operating-cost considerations.

- Data governance and model validation
	- Before policy adoption, validate data completeness (boardings/alightings, OD data, peak/off-peak splits) and model assumptions. Large gaps between model assumptions and operational reality increase decision risk.

- Stakeholder engagement and public consultation
	- Stop merging is highly visible; engage residents, district councils, senior/disabled advocacy groups, and bus operators early. Transparent cost-benefit and impact assessments, plus pilot mechanisms, reduce public resistance.

- Regulatory and planning alignment
	- Merging decisions must be coordinated with road design, pedestrian circulation, safety standards, and broader urban mobility policies (walkability/slow-street strategies) to avoid disconnected departmental actions.

- Monitoring and iterative rollout
	- Adopt a phased pilot approach: implement small-scale trials with predefined monitoring indicators (boardings, walking distance distribution, passenger satisfaction, operating costs) and evaluate during and after the trial to refine the plan.

3. Data and analyses needed

- Fine-grained OD (origin-destination) and boarding/alighting data with time granularity (peak/off-peak, weekdays/weekends).
- Network and pedestrian accessibility data (including slope, crosswalk safety features, and estimated crossing times).
- User vulnerability attributes (age, disability status, low-income indicators) or representative survey data to quantify equity impacts.
- Rapid cost–benefit analysis including user delay costs and social cost measures and sensitivity testing across scenarios.

4. Suggested policy workflow (brief)

1. Define quantitative decision thresholds and KPIs (for example: merges should achieve >X% reduction in average wait time while affecting <Y% of vulnerable populations).
2. Validate data and replicate model results by benchmarking simulations against historical operational data.
3. Run a short-term field pilot in target areas with monitoring and survey components.
4. Review pilot outcomes with stakeholders and adopt staged implementation or carve-out exemptions as needed.

5. Conclusion
Team 6 has the technical foundation and simulation outputs to inform policy recommendations. Before practical adoption, focus is needed on data validation, vulnerability impact assessment, and transparent decision thresholds combined with public engagement. Priority next steps are obtaining OD and pedestrian accessibility datasets and launching a targeted pilot, then scaling decisions based on empirical evidence.

---
*This analysis was prepared using Team 6's Bus-Stop-Optimization resources in the repository. If desired, I can convert the pilot evaluation checklist or KPI template into an Excel/CSV file next.*