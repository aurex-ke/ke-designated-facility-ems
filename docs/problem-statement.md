# Problem statement

Status: draft for milestone M1. Regulation facts were checked on 2026-10-13 against search-result excerpts of the Kenya Law text. Kenya Law blocked automated fetching of the full text, so **re-read the full text before relying on any clause**. This is not legal advice.

## The problem

Kenyan commercial, industrial and institutional sites above an annual energy-use threshold must run an energy management programme. Meeting the duties (audits, an energy manager, a committee, reporting, and realising audit savings) needs sub-metered data, a tariff model and a repeatable compliance report. This project builds a simulation-first reference implementation that shows how an open-source EMS could support that work, using a simulated 60-room hotel. Nothing is deployed.

## What the regulations say

Energy (Energy Management) Regulations, 2025 (Legal Notice 18 of 2025).

| Topic | What the text says | Status |
|---|---|---|
| Threshold (reg. 5) | A commercial, industrial or institutional facility consuming more than 180,000 kWh of thermal and electrical energy per year is classified as a designated facility | Verified excerpt, 2026-10-13 |
| Energy manager (reg. 6) | The owner engages the services of an energy manager | Verified excerpt, 2026-10-13 |
| Committee (reg. 6) | The owner appoints an energy management committee | Verified excerpt, 2026-10-13 |
| Licensing | Part VIII covers licensing of energy auditors, energy managers, audit firms and a further category whose heading is truncated in the excerpt, probably energy service companies | Heading seen; details verify |
| Audit frequency | At least once every four years | Verified excerpt, 2026-10-13 |
| Reporting | The audit report goes to the Authority within one month of undertaking the audit | Verified excerpt, 2026-10-13 |
| Authority review | The Authority has thirty days to approve or reject the report | Verified excerpt, 2026-10-13 |
| Savings | Realise at least fifty percent of the recommended energy savings, within three years of submission of the energy investment plan | Verified excerpt, 2026-10-13 |
| Auditor independence | The energy manager may not audit their own facility | Not verified in this pass: verify |

## Points where sources disagree or are unclear

- **"Thermal and electrical".** The regulation text uses "and". One secondary source writes "electrical or thermal". Whether the 180,000 kWh is a combined total or applies to each is not settled here. The project treats it as a combined total **as an assumption**.
- **Audit interval and savings rate.** One secondary article claims biennial audits and a 10% annual implementation rate. This contradicts the regulation excerpt (four years; fifty percent within three years). The project follows the regulation excerpt.
- **Designation.** The definitions refer to a facility designated by the Authority under section 188 of the Energy Act, while reg. 5 classifies by consumption. How the two interact is unresolved: verify.
- **2012 regulations.** The 2025 regulations succeed the 2012 regulations. Secondary sources describing a three-year audit cycle refer to the older text.

## Net-metering and export

Energy (Net-Metering) Regulations, 2024 (Legal Notice 104 of 2024), checked 2026-10-13 against excerpts.

- Apply to renewable energy systems below 1 MW.
- Domestic limits are 4 kW (single-phase) and 10 kW (three-phase). Commercial and industrial systems are capped at the maximum load demand reached in the twelve months before the application. **1 MW is the applicability limit, not a commercial cap.**
- A person may not operate a net-metering system without a net metering system agreement with the licensee.
- An agreement runs for a renewable term of five years.
- **Export credit rate: deliberately not stated.** Sources disagree, and the rate has not been checked against the regulation text.
- A 2026 article reports that EPRA introduced a charge for unauthorised exports. The exact instrument, its date and the term "dumping" are **unverified**.

For v0.1 the simulated hotel does not export. See the open question below.

## Assumptions to calibrate

All of these are assumptions until compared with real bills:

1. Hotel size (60 rooms) and load profile.
2. Tariff values.
3. Whether such a hotel exceeds the designated-facility threshold.
4. That the threshold is a combined thermal-plus-electrical total.

## Open questions

1. Is zero export the right default for v0.1, given the agreement and charge regime above?
2. How should the compliance report treat the "thermal" part of the threshold for an electricity-dominated site?
3. Which OpenEMS drivers and controllers exist for the simulated PV and storage? This is checked in M2.

## Sources (retrieved 2026-10-13)

- Energy (Energy Management) Regulations, 2025, Kenya Law: https://new.kenyalaw.org/akn/ke/act/ln/2025/18/eng@2025-02-07
- Energy (Net-Metering) Regulations, 2024, Kenya Law: https://new.kenyalaw.org/akn/ke/act/ln/2024/104/eng@2024-07-26
- Energy (Net-Metering) Regulations, 2024, EPRA PDF: https://www.epra.go.ke/sites/default/files/2024-11/LN104_2024.%20Net%20Metering%20Regulations.pdf
- Business Radar, EPRA energy management rules (secondary): https://www.businessradar.co.ke/blog/2026/03/11/epra-introduces-energy-management-rules-for-high-power-facilities/
- Ethical Business Africa (secondary, conflicting figures): https://ethicalbusiness.africa/2025/09/25/kenyas-energy-act-reforms-implications-for-investors/
- Africa Sustainability Matters, unauthorised export charge (secondary): https://africasustainabilitymatters.com/kenya-tightens-solar-grid-rules-as-epra-introduces-charge-for-unauthorized-electricity-exports/
