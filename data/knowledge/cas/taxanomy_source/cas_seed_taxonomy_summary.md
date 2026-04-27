# CAS Seed Taxonomy - Extraction Summary

Source: FinnOne Neo CAS - Online Help_1.pdf

- Pages processed: 766
- Stage headings extracted: 57
- Candidate screen/tab/section names extracted: 375
- Product/LOB hints extracted from PDF: 14
- Curated business LOBs after domain correction: 18
- Facility types separated from ProductTypes: 5


## Manual Domain Correction Applied

The PDF extraction produced useful product hints, but the clean bootstrap taxonomy now uses the domain-expert CAS LOB model as the authoritative ProductType/LOB layer.

### Curated CAS LOBs

- Home Loan — aliases/codes: HL, ML, Mortgage Loan
- Personal Loan — PL
- Auto Loan — MAL, Movable Asset Loan, Consumer Vehicle Loan
- Commercial Vehicle Loan — CV
- Commercial Equipment Loan — CEQ
- Farm Equipment Loan — FE, Tractor, Farm Equipment Loan
- Agriculture Loan — Agri
- Education Loan — Edu
- Loan Against Property — LAP
- Micro Housing Finance — MHF
- Finance Against Property — FAS, FOS
- Corporate Loan — MULF, Multi Facility Loan
- Self Help Group — SHG
- Joint Liability Group — JLG
- Gold Loan
- Omni Loan
- Consumer Durable — CD, Proposal
- Credit Card — CC

### Facility Types

These are **not ProductTypes**. They belong under Corporate Loan / Multi Facility workflows:

- Bill Discounting
- Bank Guarantee
- Letter of Credit
- Business Loans
- Cash Credit

### Composite LOB Rule

Omni Loan is treated as a composite LOB. It may contain sub-loans such as Auto Loan, Home Loan, Personal Loan, Commercial Vehicle Loan, and Credit Card. During chunking, preserve both `lob_hint = "Omni Loan"` and a detected `sub_lob_hint` when available.

### Context-Sensitive Alias Warning

`CC` should map to **Credit Card** in ProductType/LOB context. In facility/limit context under Corporate Loan, `CC` may mean **Cash Credit**. The corrected taxonomy keeps this as context-sensitive and does not map `CC = Cash Credit` globally.


## Stages

- **Leads** (pp. 4-8) | applicability: Credit Card, Finance Product
- **Proposals** (pp. 8-26) | applicability: Consumer Durable Finance
- **Lead Conversion Stage** (pp. 26-40) | applicability: All Product Types, Finance Product
- **Lead Details** (pp. 40-173) | applicability: FAS
- **Login Acceptance** (pp. 174-176) | applicability: Any Finance Product Type, Credit Card, Finance Product
- **Sales Queue** (pp. 177-179)
- **Credit Card Data Entry (CCDE)** (pp. 179-225) aliases: CCDE, Credit Card Data Entry | applicability: Credit Card
- **Know Your Customer (KYC)** (pp. 225-269) aliases: KYC, Know Your Customer | applicability: Credit Card, FAS, JLG, SHG
- **Credit Bureau Referral Activity** (pp. 269-275)
- **Detailed Data Entry (DDE)** (pp. 276-372) aliases: DDE, Detailed Data Entry | applicability: Commercial Vehicle, Consumer Vehicle, FAS, Home Loan
- **DDEQC** (pp. 372-381) | applicability: FAS
- **Gold Valuation** (pp. 381-384) | applicability: FAS
- **Pre Sanction Visit (PSV)** (pp. 385-388) aliases: PSV, Pre Sanction Visit | applicability: SHG
- **Account Updation** (pp. 388-392) | applicability: SHG
- **Policy Referral/Execution** (pp. 392-396)
- **Collateral Investigation Initiation (CII)** (pp. 396-398) aliases: CII, Collateral Investigation Initiation
- **Collateral Investigation Verification** (pp. 398-402) | applicability: Commercial Vehicle, Consumer Vehicle
- **Valuation Completion** (pp. 402-404)
- **Collateral Investigation Completion (CIC)** (pp. 404-405) aliases: CIC, Collateral Investigation Completion
- **Field Investigation Initiation (FII)** (pp. 406-411) aliases: FII, Field Investigation Initiation
- **FI Allocation Grid** (pp. 411-412)
- **Agent Field Investigation Verification** (pp. 412-413)
- **Field Investigation Verification (FIV)** (pp. 413-415) aliases: FIV, Field Investigation Verification
- **Field Investigation Completion (FIC)** (pp. 415-419) aliases: FIC, Field Investigation Completion
- **Recommendation (Loans)** (pp. 419-431)
- **Recommendation (Credit Card)** (pp. 431-435) | applicability: Credit Card
- **Credit Approval (Loans)** (pp. 435-468) | applicability: All Product Types, Consumer Durable Finance
- **Credit Approval (Consumer Finance)** (pp. 468-472)
- **Credit Approval (Credit Card)** (pp. 472-480) | applicability: Credit Card
- **Asset Validation Stage** (pp. 480-485) | applicability: FAS
- **Incomplete Collateral Details Activity (ICD)** (pp. 485-495) aliases: ICD, Incomplete Collateral Details | applicability: Personal Loan
- **Reconsideration** (pp. 495-506)
- **Operations Check** (pp. 506-510) | applicability: Credit Card
- **Post Approval Activity** (pp. 510-550) | applicability: Finance Product, Gold Loan
- **Facility Initiation** (pp. 550-557)
- **FDE** (pp. 557-563)
- **Tranche Initiation** (pp. 563-590)
- **Tranche Approval** (pp. 590-602) | applicability: Credit Card, JLG, SHG
- **Curing** (pp. 602-647)
- **Application Tranche VAP Linking** (pp. 647-651)
- **RCU Initiation** (pp. 651-655) | applicability: All Product Types
- **RCU Verification** (pp. 655-656) | applicability: All Product Types
- **RCU Referral** (pp. 656-657) | applicability: All Product Types
- **Disbursal Initiation** (pp. 657-715) | applicability: All Product Types, Home Loan
- **Disbursal Author** (pp. 715-721) | applicability: Credit Card, JLG, SHG
- **Subsequent Disbursal** (pp. 721-724)
- **DCC Scheduling** (pp. 724-727) | applicability: FAS, JLG, SHG, SHG/JLG
- **DCC Execution** (pp. 727-730) | applicability: FAS, JLG, SHG, SHG/JLG
- **Sales Queue Disbursal** (pp. 731-751) | applicability: FAS, Finance Product
- **Send To Card Management System** (pp. 751-752) | applicability: Credit Card
- **Raise Query** (pp. 752-754)
- **Response Query** (pp. 754-754)
- **Unquery** (pp. 754-755)
- **Reassign Query** (pp. 755-756)
- **Deviation Approval Sheet** (pp. 756-757)
- **Renewal Recommendation** (pp. 757-762) | applicability: Finance Product
- **Renewal Approval** (pp. 762-766) | applicability: Finance Product

## Top reusable screens/sections by stage count

- **More Actions on Application**: 30 stage(s)
- **Workflow History Records**: 28 stage(s)
- **Documents**: 17 stage(s)
- **Applicant Information**: 8 stage(s)
- **Asset Details**: 8 stage(s)
- **Bank/Credit Card Details >> Bank Details**: 8 stage(s)
- **Sourcing Details**: 8 stage(s)
- **Bank/Credit Card Details**: 7 stage(s)
- **VAP Details**: 7 stage(s)
- **Asset Details >> Invoice Details**: 6 stage(s)
- **Asset Details >> Vehicle Details**: 6 stage(s)
- **Collateral Details**: 6 stage(s)
- **Communication Details**: 6 stage(s)
- **FAS Details**: 6 stage(s)
- **Insurance Details**: 6 stage(s)
- **Repayment Parameters >> Insurance Details**: 6 stage(s)
- **Application Details**: 5 stage(s)
- **Asset Details >> Summary**: 5 stage(s)
- **Bank Details**: 5 stage(s)
- **Bank/Credit Card Details >> Card Details**: 5 stage(s)
- **Collateral Details tab >> Other Details**: 5 stage(s)
- **Customer Details**: 5 stage(s)
- **Decision Details**: 5 stage(s)
- **Finance Details**: 5 stage(s)
- **Mudra Loan**: 5 stage(s)
- **Personal Information**: 5 stage(s)
- **Receipt Details >> Receivables To Be Collected**: 5 stage(s)
- **Repayment Schedule**: 5 stage(s)
- **Applicants grid**: 4 stage(s)
- **Asset Details >> Address Details**: 4 stage(s)
- **Asset Details >> Collateral Details**: 4 stage(s)
- **Asset Details >> Consolidated Summary**: 4 stage(s)
- **Asset Requested Details**: 4 stage(s)
- **Business Details**: 4 stage(s)
- **Collateral Details tab >> Builder Details**: 4 stage(s)
- **Collateral Details tab >> Insurance**: 4 stage(s)
- **Collateral Details tab >> Lien Details**: 4 stage(s)
- **Collateral Details tab >> Ownership Details**: 4 stage(s)
- **Collateral Details tab >> Property & Registration Details**: 4 stage(s)
- **Collateral Details tab >> Property Address**: 4 stage(s)
- **Collateral Details tab >> Seller Details**: 4 stage(s)
- **Communication Details >> Additional Communication Details**: 4 stage(s)
- **Communication Details >> Communication Preferences**: 4 stage(s)
- **Customer Details >> Identification**: 4 stage(s)
- **Customer Details >> Organization Address**: 4 stage(s)
- **Customer Details child**: 4 stage(s)
- **Deal Limit Details**: 4 stage(s)
- **Eligibility Policy**: 4 stage(s)
- **Employment Details**: 4 stage(s)
- **Facility Details**: 4 stage(s)
- **Financial Details**: 4 stage(s)
- **Financial Details >> Asset Details**: 4 stage(s)
- **Financial Details >> File Upload and Preview**: 4 stage(s)
- **Financial Details >> Income Details**: 4 stage(s)
- **Financial Details >> Liability Details**: 4 stage(s)
- **Financial Details >> Other Income Details**: 4 stage(s)
- **Financial Details >> Previous**: 4 stage(s)
- **Group Information**: 4 stage(s)
- **Identification**: 4 stage(s)
- **LAN Linking Details**: 4 stage(s)
- **Market Information details**: 4 stage(s)
- **Member Information**: 4 stage(s)
- **Partners & Directors Details**: 4 stage(s)
- **Property Details**: 4 stage(s)
- **Receipt Details**: 4 stage(s)
- **References**: 4 stage(s)
- **Sourcing Details >> Promo Code Details**: 4 stage(s)
- **Sourcing Details >> Subsidy**: 4 stage(s)
- **Underwriter Decision tab >> Miscellaneous Information**: 4 stage(s)
- **Applicant Details**: 3 stage(s)
- **Applicant information**: 3 stage(s)
- **Applicant's Profile**: 3 stage(s)
- **Application Tranches**: 3 stage(s)
- **Approval Checklist**: 3 stage(s)
- **Approval Sheet**: 3 stage(s)
- **Approve Deviations**: 3 stage(s)
- **Collateral Details >> Investigation Details**: 3 stage(s)
- **Collateral Details >> Investigation Details tab >> Valuation**: 3 stage(s)
- **Collateral Details >> Investigation Details tab >> Verification**: 3 stage(s)
- **Collateral Details tab >> Address Details**: 3 stage(s)
