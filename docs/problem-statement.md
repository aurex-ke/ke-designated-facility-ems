# Problem statement

Status: draft for milestone M1. Regulation facts were first checked on 2026-10-13 against search-result excerpts of the Kenya Law text, then re-checked on 2026-10-20 against the full gazette PDFs of both instruments (supplied by the owner as project files). Amendments and later tariff instruments were not checked, so **confirm against the current law before relying on any clause**. This is not legal advice.

## The problem

Kenyan commercial, industrial and institutional sites above an annual energy-use threshold must run an energy management programme. Meeting the duties (audits, an energy manager, a committee, reporting, and realising audit savings) needs sub-metered data, a tariff model and a repeatable compliance report. This project builds a simulation-first reference implementation that shows how an open-source EMS could support that work, using a simulated 60-room hotel. Nothing is deployed.

## What the regulations say

Energy (Energy Management) Regulations, 2025 (Legal Notice 18 of 2025).

| Topic | What the text says | Status |
|---|---|---|
| Threshold (reg. 5) | A commercial, industrial or institutional facility consuming more than 180,000 kWh of thermal and electrical energy per year is classified as a designated facility | Verified, reg. 5, full text, 2026-10-20 |
| Energy manager (reg. 6) | The owner engages the services of an energy manager | Verified, reg. 6(1), full text, 2026-10-20 |
| Committee (reg. 6) | The owner appoints an energy management committee | Verified, reg. 6(3), full text, 2026-10-20 |
| Licensing | The licensing part covers energy auditors, energy managers, energy audit firms and energy service companies (regs. 16 to 29) | Verified, full text, 2026-10-20 |
| Audit frequency | At least once every four years | Verified, reg. 8(1), full text, 2026-10-20 |
| Reporting | The audit report goes to the Authority within one month of undertaking the audit | Verified, reg. 9(1), full text, 2026-10-20 |
| Authority review | The Authority has thirty days to approve or reject the report | Verified, reg. 9(2), full text, 2026-10-20 |
| Savings | Realise at least fifty percent of the recommended energy savings, within three years of submission of the energy investment plan (the plan is due within six months of approval of the audit report, reg. 10(1)) | Verified, reg. 10(2)(a), full text, 2026-10-20 |
| Auditor independence (reg. 8(3)) | An energy manager in a designated facility shall not conduct an energy audit of the facility | Verified, full text, 2026-10-20 |
| Licensed energy manager (regs. 16, 17) | A person shall not be employed or contracted as an energy manager unless licensed by the Authority | Verified, regs. 16(1)(c) and 17(d), full text, 2026-10-20 |

## Points where sources disagree or are unclear

- **"Thermal and electrical".** The regulation text uses "and". One secondary source writes "electrical or thermal". Whether the 180,000 kWh is a combined total or applies to each is not settled here. The project treats it as a combined total **as an assumption**.
- **Audit interval and savings rate.** One secondary article claims biennial audits and a 10% annual implementation rate. This contradicts the regulation text (reg. 8(1): at least every four years; reg. 10(2)(a): at least fifty percent of the recommended savings within three years of submitting the energy investment plan, which is due within six months of approval of the audit report, reg. 10(1)). The project follows the regulation text.
- **Designation.** The definitions refer to a facility designated by the Authority under section 188 of the Energy Act, while reg. 5 classifies by consumption. How the two interact is unresolved: verify.
- **2012 regulations.** The 2025 regulations succeed the 2012 regulations. Secondary sources describing a three-year audit cycle refer to the older text.
- **Citation inconsistencies in the gazette text.** The 2025 instrument is Legal Notice 18 of 2025 (Kenya Gazette Supplement No. 10, 7 February 2025), but its reg. 1 says "2024", it records being made on 3 January 2024, and some forms cite "2020" or "2021". This project cites it as Legal Notice 18 of 2025.

## Net-metering and export

Energy (Net-Metering) Regulations, 2024 (Legal Notice 104 of 2024), checked 2026-10-13 against excerpts and re-checked 2026-10-20 against the gazette PDF (Kenya Gazette Supplement No. 121, 18 June 2024; the PDF text has some OCR noise).

- Apply to renewable energy systems below 1 MW (reg. 5(1)).
- Domestic limits are 4 kW (single-phase) and 10 kW (three-phase). Commercial and industrial systems must not exceed one megawatt and are also capped at the maximum load demand reached in the twelve months before the application (reg. 6(1)(b)), so **both limits apply**. Reg. 5(1) says "less than 1 MW" and reg. 6(1)(b)(i) says "not exceed one megawatt", so the boundary at exactly 1 MW is ambiguous.
- A person may not operate a net-metering system without a net metering system agreement with the licensee.
- An agreement runs for a renewable term of five years.
- **Export credit (reg. 10(3), (5), (6)).** The credit for each exported unit is fifty percent of the exported unit. Credited units offset the net energy supplied. Any surplus carries forward, and unused credits are forfeited at the end of the licensee's financial year. The wording does not say whether the fifty percent applies to kWh or to value; the project reads it as kWh, **as an assumption**. Earlier disagreement among secondary sources is not resolved. Amendments and tariff instruments after 18 June 2024 were not checked.
- A 2026 article reports that EPRA introduced a charge for unauthorised exports. The exact instrument, its date and the term "dumping" are **unverified**. Neither regulation text read on 2026-10-20 mentions such a charge; the net-metering text only makes operating or connecting without an agreement an offence (regs. 7(1) and 14).

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

## Sources (retrieved 2026-10-13 unless stated)

- Kenya Gazette Supplement No. 10 (Legislative Supplement No. 6), 7 February 2025, Legal Notice 18, Energy (Energy Management) Regulations, 2025. PDF supplied by the owner as a project file, read 2026-10-20.
- Kenya Gazette Supplement No. 121 (Legislative Supplement No. 47), 18 June 2024, Legal Notice 104, Energy (Net-Metering) Regulations, 2024. PDF supplied by the owner as a project file, read 2026-10-20.
- Energy (Energy Management) Regulations, 2025, Kenya Law: https://new.kenyalaw.org/akn/ke/act/ln/2025/18/eng@2025-02-07
- Energy (Net-Metering) Regulations, 2024, Kenya Law: https://new.kenyalaw.org/akn/ke/act/ln/2024/104/eng@2024-07-26
- Energy (Net-Metering) Regulations, 2024, EPRA PDF: https://www.epra.go.ke/sites/default/files/2024-11/LN104_2024.%20Net%20Metering%20Regulations.pdf
- Business Radar, EPRA energy management rules (secondary): https://www.businessradar.co.ke/blog/2026/03/11/epra-introduces-energy-management-rules-for-high-power-facilities/
- Ethical Business Africa (secondary, conflicting figures): https://ethicalbusiness.africa/2025/09/25/kenyas-energy-act-reforms-implications-for-investors/
- Africa Sustainability Matters, unauthorised export charge (secondary): https://africasustainabilitymatters.com/kenya-tightens-solar-grid-rules-as-epra-introduces-charge-for-unauthorized-electricity-exports/
