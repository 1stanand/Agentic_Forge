# CAS ATDD Knowledge Base

## Context Document for Forge Agentic

**Author:** Anand (CAS Domain Expert, Nucleus Software)  
**Captured by:** Knowledge session — AI/ML Engineer + Domain Expert  
**Purpose:** Source of truth for Forge Agentic agent design, RAG design, and system prompt authoring  
**Last Updated:** 2026-04-25 (Session 2 — STP, LogicalID ownership, scenario titles added)

---

## 1. What This Document Is

This is not a Gherkin tutorial. This is CAS-specific ATDD knowledge — the conventions, rules, and structural patterns used by the CAS ATDD repository at Nucleus Software. These conventions are the product of years of iteration, constraint, and pragmatic problem-solving by a 50+ person testing team working on a legacy system under real enterprise constraints.

This knowledge cannot be derived from Gherkin documentation. It must be treated as domain truth.

---

## 2. Background — Why the Conventions Exist

The CAS ATDD project started approximately 3 years ago. Key facts about its origin that explain why the conventions are what they are:

- Selenium/Java was chosen as the engine without accounting for Selenium's scaling limitations
- No automation engineers were hired for project creation — testers wrote automation
- 50 testers were assigned to write tests for features they partially understood
- 18 Lines of Business (LOBs), multiple screens, multiple stages — enormous combinatorial space
- Target of 100 test examples per tester per day was set — creating incentive to game metrics

Early naive approach: one scenario, 50 fields in examples, multiplied by 18 LOBs, multiplied by 7 stages = thousands of example rows per scenario. Impossible to write, impossible to maintain.

This pressure forced two major innovations: the **Dictionary System** and the **Ordered Flow System**. Both are non-standard extensions on top of Cucumber/Gherkin, powered by a custom test runner. Understanding why they were invented is essential to using them correctly.

---

## 3. The Two Flow Types

Every feature file in the CAS ATDD repository is either **Unordered** or **Ordered**. These are not style choices. They are execution contracts.

### 3.1 Unordered Flow

**When to use:** When scenarios can run independently — no dependency on data created by a previous scenario.

**Characteristics:**

- Each scenario is self-contained
- Has a `Background:` block
- Standard Background step: `Given user is on CAS Login Page` (single step — universal convention)
- No `@Order` tag at file level
- Dictionary system applies (see Section 4)
- Scenarios can run in parallel

**When not to use:** When the story involves state that carries across stages (e.g., KYC decision affecting Credit Approval behavior).

### 3.2 Ordered Flow

**When to use:** When scenarios must run in sequence and share application state across stages.

**Why it exists:** Selenium has no memory between tests. CAS is stateful — a decision at Stage 2 affects Stage 5. The only solution was to design scenarios that explicitly chain to the same application using `LogicalID`, sequenced by `Order.json`.

**Characteristics:**

- `@Order` tag at file level (partial flow) or `@E2EOrder` (full end-to-end lifecycle)
- No `Background:` block — ordered files must not have Background
- No dictionary system — ordered files must not use `#${...}` dictionaries
- No `<variable>` expansion in example tables (except LogicalID and standard columns)
- All scenarios chain via the prerequisite step and LogicalID
- Cannot run scenarios in parallel

**Hard rule — no mixing:**
An ordered file cannot have dictionaries. An unordered file cannot have `@Order`. These mechanisms are mutually exclusive.

### 3.3 Decision Ownership

The decision of whether a story is ordered or unordered is **not a technical decision** and **not Forge's decision**. It is made by stakeholders in the 3-amigos meeting and provided as user input before generation begins. Forge receives this as a given and enforces the correct structural rules accordingly.

---

## 4. The Dictionary System (Unordered Files Only)

### 4.1 Why It Exists

Testers needed to express combinatorial coverage (product × stage × applicant) without writing thousands of explicit example rows. The dictionary system allows a single example row with variable references to expand into the full cartesian product at runtime.

### 4.2 How It Works

**The expansion signal:** Angle-bracket syntax in the Examples table tells the runner to expand using the dictionary.

```gherkin
Examples:
    | ProductType   | ApplicationStage   |
    | <ProductType> | <ApplicationStage> |
```

`<ProductType>` and `<ApplicationStage>` are variables. The runner looks up the dictionary, finds the value list, and generates one row per combination.

**The dictionary:** A commented key-value declaration, not executable code.

```gherkin
#${ProductType:["HL","PL"]}
#${ApplicationStage:["Lead Details","DDE","Credit Approval"]}
```

Result: 2 × 3 = 6 example rows at runtime from 1 row in the file.

### 4.3 Three Dictionary Scopes

Dictionaries exist at three levels. **Nearest scope wins. Completely. No merging. No fallback.**

**File Level** — no indentation, top of file, applies to all scenarios that do not have their own dictionary:

```gherkin
#${ProductType:["HL","PL"]}
#${ApplicationStage:["Lead Details","DDE","Credit Approval"]}

Scenario Outline: ...   ← uses file level dictionary
```

**Scenario Level** — indented, sits above a specific scenario, overrides file level entirely for that scenario:

```gherkin
    #${ProductType:["SHG","HL"]}
    #${ApplicationStage:["DDE","Credit Approval"]}
    Scenario Outline: ...   ← uses scenario level, ignores file level
```

**Example Level** — sits above a specific Examples block, overrides everything for those rows:

```gherkin
Scenario Outline: ...
    #${ProductType:["SHG"]}
    #${ApplicationStage:["DDE","Credit Approval"]}
    Examples:
        | ProductType   | ApplicationStage   |
        | <ProductType> | <ApplicationStage> |   ← uses example level

    #${ProductType:["CC"]}
    #${ApplicationStage:["CCDE","Credit Approval"]}
    Examples:
        | ProductType   | ApplicationStage   |
        | <ProductType> | <ApplicationStage> |   ← uses its own example level
```

### 4.4 Scope Precedence — Visual Summary

```
File Level Dictionary
│
├── Scenario 1 (no own dict)          → uses File Level
│
├── Scenario 2 (has Scenario Level)   → uses Scenario Level only. File Level ignored.
│
└── Scenario 3 (has Scenario Level + some Examples have Example Level)
      ├── Examples block A (no own dict)   → uses Scenario Level
      └── Examples block B (has Example Level)   → uses Example Level only. Scenario Level ignored.
```

### 4.5 Mixing Rule

Within a single scenario, pick one level and stay consistent:

- All Examples blocks use Scenario Level dictionary — good
- All Examples blocks use their own Example Level dictionaries — good
- Some Examples blocks use Scenario Level, some use Example Level — discouraged (silently enforced)

Reason: Non-technical testers get confused. Consistency over cleverness.

### 4.6 Redundancy Is Acceptable

When multiple Examples blocks within a scenario share overlapping values (e.g., `Credit Approval` appears in both dictionaries), that redundancy is acceptable and encouraged. Readability takes priority over deduplication. Do not flag redundant expansion as a defect.

### 4.7 Stage-Specific Overrides

Some scenarios are locked to a specific stage by behavioral logic, not by convention. When a behavior can only physically occur at one stage, the example table uses a hardcoded value instead of variable expansion:

```gherkin
Examples:
    | ProductType   | ApplicationStage |
    | <ProductType> | KYC              |    ← Product expands, Stage does not
```

This is a domain judgment — the stage is hardcoded because the action (e.g., performing KYC) only exists at the KYC stage regardless of product. This is CAS domain knowledge, not ATDD structural knowledge.

Fully hardcoded rows (no expansion at all) are also valid for integration or edge scenarios:

```gherkin
Examples:
    | ProductType             | ApplicationStage       |
    | Credit Card Application | Card Management System |
```

---

## 5. The Ordered Flow Mechanics

### 5.1 Order.json

`Order.json` is a read-only toolchain input. It is not owned by Forge. It controls execution sequence using boolean tag expressions:

```json
"@CCDE and @OpenApplication"
"@CCDE and @AppInfo and @Guarantor"
"@CCDE and not @MoveToNext and not @Enquiry"
"@CreditApproval and @MoveToNext"
```

The runner sequences scenarios by matching their effective tag set against these expressions in order. First match wins — a scenario does not run twice even if its tags match multiple expressions.

**If a scenario's tags match no expression in Order.json — it is silently skipped.** No error. This is a critical invisible defect class.

**Forge validation rule:** Agent 8 must dry-run each ordered scenario's effective tag set against `Order.json`. If no expression matches, this is a hard ATDD failure, not a warning. A generated scenario that will be silently skipped is worse than no scenario.

### 5.2 LogicalID

`Order.json` controls sequence. `LogicalID` controls continuity.

All scenarios in an ordered flow that operate on the same application must share the same `LogicalID`. The prerequisite step uses LogicalID to find and continue the correct application.

**Convention:** `CAS_{storyID}_{intent}` — e.g., `CAS_256008_CCDE`, `CAS_256008_REJECT`, `CAS_256008_DISBURSE`. Values should be meaningful and unique. They are thread IDs — their only job is to tie scenarios to the same application.

**LogicalID in scenario titles** (recommended convention):

```gherkin
Scenario Outline: <LogicalID> : Verify Presence of Guarantor Option at <ApplicationStage>
```

This makes automation test reports readable by including the LogicalID in the report output.

### 5.3 The Prerequisite Step

Every scenario in an ordered file starts with this exact canonical step:

```gherkin
Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
```

This is the mechanism that chains scenarios. It tells the runner: find the previous scenario with this LogicalID, ensure it ran, and continue on the same application.

**Generation rule:** Forge must emit the canonical short form above. If older repository files contain a longer login-data variant, treat that as legacy repository history — do not use it as the generation standard unless the team explicitly changes this document.

### 5.4 @Order vs @E2EOrder

| Tag         | Meaning                                                             |
| ----------- | ------------------------------------------------------------------- |
| `@Order`    | Ordered file covering a partial flow (e.g., CCDE → Credit Approval) |
| `@E2EOrder` | Ordered file covering the full lifecycle (Lead Details → Disbursal) |

### 5.5 Annotation Scopes in Ordered Files

Unlike dictionaries (where nearest scope wins and others are discarded), annotations **stack across all levels**. None are discarded.

**File level** — applies to all scenarios in the file:

```
@DevTrack @GA-9.0 @Order @CAS-256008
```

**Scenario level** — stacks on top of file level for that scenario.

**Example level** — stacks on top of file and scenario level for those rows:

```gherkin
    @CCDE
    Examples:
        | LogicalID       | ApplicationStage |
        | CAS_256008_CCDE | CCDE             |
```

**Effective tag set for that example row:**
`@DevTrack + @GA-9.0 + @Order + @CAS-256008 + @CCDE`

Order.json matches against the full effective tag set. The `@CCDE` annotation is what places the scenario in the correct position in the execution sequence.

### 5.6 Recommended File-Level Annotations

Not all mandatory, but established convention:

| Tag                    | Purpose                               | Required?                    |
| ---------------------- | ------------------------------------- | ---------------------------- |
| `@Order` / `@E2EOrder` | Declares flow type                    | Mandatory for ordered files  |
| `@CAS-{storyID}`       | Links file to JIRA story              | Recommended for all files    |
| `@DevTrack`            | Tracking tag                          | Recommended                  |
| `@GA-{version}`        | Release version                       | Recommended                  |
| `@NotImplemented`      | Marks file as draft/not yet automated | Recommended during authoring |
| `@AuthoredBy-{name}`   | Authorship                            | Recommended                  |

---

## 6. Structural Rules

### 6.1 Keyword Rules

**`But` keyword — hard banned.** Never used anywhere. Files have been rejected from merge for this. Use `And` instead.

**`Scenario` vs `Scenario Outline`:**

- Any scenario with an Examples table must use `Scenario Outline:`, not `Scenario:`
- A bare `Scenario` keyword with no title and no steps is invalid

### 6.2 Then Block Rule — Hard Banned

`Then` block may have at most one `And`:

```gherkin
Then something happens           ← best
Then something happens
And one follow-up                ← acceptable
Then something happens
And one follow-up
And another thing                ← HARD BANNED — files rejected at merge
```

Reasoning: `Then` is the assertion block. Multiple `And`s after `Then` means asserting too many things in one scenario. This is a hard organizational rule, not a style preference.

### 6.3 Ordered File Structure Rules (Summary)

An ordered file:

- Has `@Order` or `@E2EOrder` at file level
- Has no `Background:` block
- Has no `#${...}` dictionaries at any level
- Has no `<variable>` expansion (except standard columns like `<LogicalID>`, `<ApplicationStage>`)
- Has example-level annotations matching Order.json expressions
- Scenarios chain via the prerequisite step and LogicalID

### 6.4 Unordered File Structure Rules (Summary)

An unordered file:

- Has no `@Order` or `@E2EOrder` tag
- Has `Background:` with `Given user is on CAS Login Page` as the standard single step
- Uses dictionary system for combinatorial expansion
- Each scenario is independently executable
- Scenarios do not reference LogicalID for chaining

---

## 7. Quality Markers

Forge uses three inline markers to signal uncertainty or defects in generated steps. These are honest signals — visible gaps are better than fabricated coverage.

| Marker                   | Meaning                                                                    |
| ------------------------ | -------------------------------------------------------------------------- |
| `[NEW_STEP_NOT_IN_REPO]` | No sufficiently grounded step found in repo — Forge generated one honestly |
| `[LOW_MATCH]`            | Step exists in repo but match is weak — review carefully                   |
| `[ROLE_GAP]`             | Step is invalid for this stage/screen/role combination per knowledge graph |

A false-positive grounded step (wrong but plausible, no marker) is worse than a `[NEW_STEP_NOT_IN_REPO]` marker. It hides the problem.

---

## 8. Repository Facts

| Fact               | Value                              |
| ------------------ | ---------------------------------- |
| Scenario Outlines  | ~18,000                            |
| Plain Scenarios    | ~651                               |
| Background blocks  | ~956                               |
| Examples blocks    | ~29,662                            |
| Step reuse rate    | ~94% (generic parameterized steps) |
| Total unique steps | 15,000+                            |
| Feature files      | 1,500+                             |

**The repo is execution-first, not documentation-first.** Scenario titles encode execution semantics — story ID, stage, product, logical ID, verification type. Do not reduce titles to plain natural-language summaries.

**The repo is action-oriented.** Steps describe what a tester physically does in CAS. They are not business outcomes or assertions in natural language.

**New steps cannot be generated freely.** The ~94% reuse rate means the repo has the right step for almost every action — it must be found, not invented. `[NEW_STEP_NOT_IN_REPO]` is the honest fallback when retrieval fails.

---

## 9. The Three Vocabularies Problem

This is the core translation challenge Forge must solve. Three different languages describe the same behavior:

| Vocabulary      | Example                                                                         |
| --------------- | ------------------------------------------------------------------------------- |
| JIRA Language   | "throw validation when adding non-Individual applicant as primary in Omni Loan" |
| Domain Language | "Applicant Type, Primary Applicant, Omni Loan, LOB constraints"                 |
| Repo Language   | "Add Applicant of Guarantor type", "Select role as Primary"                     |

No single technique bridges all three. Different agents handle different translations.

---

## 10. Coverage Thinking (What Good Coverage Looks Like)

A story tested properly is not one scenario. It is a coverage plan across multiple layers:

- **Presence checks** — is the field/button/section visible?
- **Screen structure** — is the layout correct?
- **Happy path** — does the normal flow work?
- **Validations** — mandatory fields, invalid values, wrong formats
- **Conditional logic** — fields that appear/disappear based on selections
- **Negative paths** — what happens when expected conditions are not met?
- **Boundary values** — edge cases at limits
- **Meaningful example rows** — values that actually exercise different behaviors (not placeholders)

Example rows are not placeholders. Subtype A gets different fields than Subtype B — examples must reflect actual behavioral differences.

**A single well-understood story can have 100 scenarios.** This is not excess — it is correct coverage thinking.

---

## 11. Scope Discipline

**Story scope** = what this JIRA is introducing or changing. Test deeply. Full coverage layers.

**Ambient scope** = everything else on the screen that exists but is not part of the story. Light touch only. One presence check scenario. Do not expand.

A new field on Property Details screen does not justify full coverage of Property Address, Builder Details, and every other section. Forge must stay inside the story boundary. JIRA bleeds and dependencies exist — but the story scope principle governs.

---

## 12. Design Principles for Forge (Derived from This Knowledge)

1. **Flow type is user input** — Forge never decides ordered vs unordered. It enforces the rules for whichever type it receives.

2. **Dictionary scope is structural** — Forge must detect which scope level applies per scenario/examples block and expand correctly.

3. **Annotation stacking is additive** — all levels stack. Forge must validate that effective tag combinations match at least one Order.json expression.

4. **Then + two And is a hard reject** — no exceptions, no context-sensitivity.

5. **But keyword is a hard reject** — no exceptions.

6. **Scenario keyword with Examples is wrong** — must be Scenario Outline.

7. **Bare Scenario with no steps is invalid** — flag it.

8. **Coverage before step stitching** — plan what needs testing before deciding how to express it in repo steps.

9. **Repo-authentic over invented** — find the right existing step, do not generate a new one.

10. **Visible gaps over fabricated coverage** — markers are honest signals, not failures.

---

---

## 13. STP and OpenApplication.feature

### 13.1 The Concept — Straight Through Process (STP)

For ordered flows, a story testing behavior at Credit Approval stage does not require Forge to write scenarios that manually punch an application through Lead Details → KYC → DDE → Credit Approval. That journey is handled by STP — Straight Through Process.

Pre-existing shared files in the repo handle application state setup:

- **`PickApplication.feature`** — picks an existing application from a grid
- **`OpenApplication.feature`** — moves an application from source stage to destination stage via STP

The tester (and now Forge) simply declares the LogicalIDs needed and adds them to `OpenApplication.feature`. The runner executes that file first, and the application arrives at the target stage ready for testing.

### 13.2 What Forge Does and Does Not Generate

**Forge does NOT generate `OpenApplication.feature` or `PickApplication.feature`.** These are shared infrastructure files. Forge is aware they exist and that STP handles stage traversal.

**Forge DOES generate** the story-specific scenarios that start from the target stage — assuming the application is already there via STP.

### 13.3 The Mandatory First Step — Every Ordered Scenario

Every scenario in every ordered file must start with this exact step:

```gherkin
Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
```

This is not optional. It is not situational. It is the mandatory first step of every scenario in every ordered file — always. It implicitly signals that STP has run via `OpenApplication.feature` and the application is at the correct stage.

Forge must generate this line as the first step of every ordered scenario. No exceptions.

### 13.4 LogicalID Count Is Forge's Responsibility

The number of LogicalIDs required for a story is determined by the coverage plan — not by tester input.

This is Agent 4's (Coverage Planner) responsibility. If complete coverage of a story requires 5 distinct test paths — for example, approve, reject, send back, deviation, boundary — then 5 LogicalIDs are needed. Each LogicalID is a separate application thread.

Agent 4 must output:

- How many distinct application threads are needed
- What each thread is testing — what makes it a distinct path
- A meaningful LogicalID for each thread following the convention `CAS_{storyID}_{intent}`

This LogicalID list flows into the State packet and is used by all downstream agents when composing ordered scenarios.

---

## 14. Scenario Title Rules

### 14.1 What Bad Looks Like

```gherkin
Scenario Outline: Display CDDE, recommendation, credit approval and stage
```

This is bad. It is a label — it names stages rather than describing what is being tested. It gives no information about what behavior is verified, what the expected outcome is, or what makes this scenario distinct from others.

### 14.2 What Good Looks Like

A good scenario title:

- Describes the behavior being tested, not the stages being visited
- Is specific enough that a reader knows what passes and what fails
- For ordered files, leads with `<LogicalID> :` to make test reports readable

```gherkin
Scenario Outline: <LogicalID> : Verify Guarantor option is available in Applicant Type dropdown at <ApplicationStage>
Scenario Outline: <LogicalID> : Validate Credit Approval is rejected when deviation threshold is exceeded
Scenario Outline: <LogicalID> : Confirm application moves to Disbursal after Credit Approval decision
```

### 14.3 The Rule for Agent 8

Agent 8 must flag scenario titles that:

- Only list stage names without describing behavior
- Are generic enough to apply to any scenario in the file
- Do not describe a testable outcome

Good title test: can a reader tell what this scenario is asserting without reading the steps? If no — the title is bad.

---

_End of CAS ATDD Knowledge Base_  
_This document is a living reference. Add to it as new conventions are clarified._
