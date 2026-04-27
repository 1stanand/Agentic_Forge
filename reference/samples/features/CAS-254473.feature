@DevTrack
@GA-9.0
@Epic-CorporateLoans
@AuthoredBy-anand.singh1
@NotImplemented
@CAS-254473
Feature: Corporate Loans - Deviation Policy (Facility-wise)
  #${ProductType:["MULF"]}
  #${ApplicationStage:["DDE","Credit Approval","Tranche Approval","Disbursal"]}
  ###########################################################################
  # BUSINESS RULES (summary for readers)
  # 1. Deal-level deviations appear ABOVE facility-level deviations.
  # 2. Deal/Application Number shown for deal-level deviations — DEAL ID in case of Deal deviation.
  #    FIRST column will be Deal/Facility ID (visible everywhere).
  # 3. Deal/Facility ID column MUST remain visible across Deviation Table, Raise Manual Deviation,
  #    CAM Report, Approval screens and Deviation History.
  # 4. Facility Initiation → bifurcation occurs → only facility-level deviations visible.
  # 5. Manual deviation:
  #     - Facility LOV: optional (non-mandatory)
  #     - Single facility per deviation (no multi-select). Each deviation maps to exactly one facility → one row.
  #     - No facility selected → deviation recorded at deal-level.
  ###########################################################################
  Background:
    Given user opens an application of "<ProductType>" product type at "<ApplicationStage>" with multiple facilities
    And deviation rules are configured for deal-level and facility-level
  ###########################################################################
  # RERUN POLICY (early functional verification)
  # Functional Rerun verifies that deviations for the current stage populate the grid
  ###########################################################################
  @Positive
  Scenario Outline: Rerun Deviation Policy populates and refreshes deviations for "<ApplicationStage>"
    When user navigates to the deviation screen under "<ApplicationStage>" for "<ProductType>"
    And user clicks the "Rerun Policy" button
    Then system should populate the deviation grid with mapped deviations (deal-level and facility-level where applicable)
    And Deal/Facility ID column should be visible as the first column
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 1: New Column Visibility
  ###########################################################################
  @Positive
  Scenario Outline: New column Deal Facility ID should be available in deviation table at "<ApplicationStage>"
    When user navigates to the deviation table under "<ApplicationStage>" for "<ProductType>"
    Then user should see a column named "Deal/Facility ID" in the first position of the table
    And the header should be visible across pagination and after rerun
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  @Positive
  Scenario Outline: System should display Deal ID in Deal Facility ID Column
    When user views the deviation grid under "<ApplicationStage>" for "<ProductType>"
    Then Deal/Facility ID column should display Deal/Application Number for deal deviations in the first column
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  @Positive
  Scenario Outline: System should display Facility IDs in Deal Facility ID Column
    When user views the deviation grid under "<ApplicationStage>" for "<ProductType>"
    Then Deal/Facility ID column should display Facility ID Number for facility deviations in the first column
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 2: Deal-level & Facility-level Segregation & Sorting
  ###########################################################################
  @Positive
  Scenario Outline: System should display deal-level deviations above facility-level deviations and sort by deviation level at "<ApplicationStage>"
    When user views the deviation grid under "<ApplicationStage>" for "<ProductType>"
    Then system should show deal-level deviations first followed by facility-level deviations
    And within deal-level and facility-level groups deviations should be sorted by deviation level (descending)
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 3: Raise Manual Deviation - Positive (Deal-level)
  ###########################################################################
  @Positive
  Scenario Outline: User should be able to raise a deal-level deviation by leaving Facility LOV empty at "<ApplicationStage>"
    Given user is on the deviation screen under "<ApplicationStage>" for "<ProductType>"
    When user clicks the "Add Deviation" button
    And the Add Deviation popup should open
    And user selects Deviation Name from Deviation LOV
    And user leaves Facility LOV empty
    And user clicks "Save" on Add Deviation popup
    Then system should show a success message "Deviation saved successfully"
    And the new deviation row should appear in the deviation grid with Deal/Facility ID showing Deal/Application Number in the first column
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 4: Raise Manual Deviation - Positive (Facility-level)
  ###########################################################################
  @Positive
  Scenario Outline: User should be able to raise a facility-level deviation by selecting a Facility in LOV at "<ApplicationStage>"
    Given user is on the deviation screen under "<ApplicationStage>" for "<ProductType>"
    When user clicks the "Add Deviation" button
    And the Add Deviation popup should open
    And user selects Deviation Name from Deviation LOV
    And user selects Facility "<FacilityID>" from Facility LOV
    And user clicks "Save" on Add Deviation popup
    Then system should show a success message "Deviation saved successfully"
    And the new deviation row should appear in the deviation grid with Deal/Facility ID showing "<FacilityID>" in the first column
    Examples:
      | ApplicationStage   | ProductType   | FacilityID |
      | <ApplicationStage> | <ProductType> | F001       |
  ###########################################################################
  # SCENARIO 5: Duplicate Deviation - Prevention
  # Step A: Create baseline deviation
  # Step B: Attempt duplicate and expect validation
  ###########################################################################
  @Positive
  Scenario Outline: Precondition - User raises deviation "<DeviationName>" for Facility "<FacilityID>" at "<ApplicationStage>"
    Given user is on the deviation screen under "<ApplicationStage>" for "<ProductType>"
    When user clicks the "Add Deviation" button
    And the Add Deviation popup should open
    And user selects Deviation Name "<DeviationName>" from Deviation LOV
    And user selects Facility "<FacilityID>" from Facility LOV
    And user clicks "Save"
    Then system should create the deviation and show "Deviation saved successfully"
    Examples:
      | ApplicationStage   | ProductType   | DeviationName | FacilityID |
      | <ApplicationStage> | <ProductType> | LIMIT_EXCEED  | F002       |
  @Negative
  Scenario Outline: System should prevent raising the same deviation "<DeviationName>" again for Facility "<FacilityID>" at "<ApplicationStage>"
    Given a deviation "<DeviationName>" exists for Facility "<FacilityID>" in the application under "<ApplicationStage>" for "<ProductType>"
    When user clicks the "Add Deviation" button
    And the Add Deviation popup opens
    And user selects Deviation Name "<DeviationName>" from Deviation LOV
    And user selects Facility "<FacilityID>" from Facility LOV
    And user clicks "Save"
    Then system should block the save and display validation message "Duplicate deviation not allowed for selected facility"
    And no new row should be created in the deviation grid
    Examples:
      | ApplicationStage   | ProductType   | DeviationName | FacilityID |
      | <ApplicationStage> | <ProductType> | LIMIT_EXCEED  | F002       |
  ###########################################################################
  # SCENARIO 6: Invalid Facility Selection
  ###########################################################################
  @Negative
  Scenario Outline: System should block selecting a facility not belonging to the application at "<ApplicationStage>"
    Given user is on the Add Deviation popup under "<ApplicationStage>" for "<ProductType>"
    When user attempts to select facility "<InvalidFacility>" from Facility LOV
    Then system should not find "<InvalidFacility>" in LOV and should show "No Data Available"
    Examples:
      | ApplicationStage   | ProductType   | InvalidFacility |
      | <ApplicationStage> | <ProductType> | FX999           |
  ###########################################################################
  # SCENARIO 7: Facility LOV - Pagination / Large List
  ###########################################################################
  @Positive
  Scenario Outline: Facility LOV should support pagination or scrolling for large number of facilities at "<ApplicationStage>"
    When user opens Facility LOV from Add Deviation popup under "<ApplicationStage>" for "<ProductType>"
    Then system should allow scrolling / pagination in the LOV
    And system should load LOV values dynamically as user scrolls / paginates
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 8: System-Originated Deviations For Multiple Facilities
  # If system rule detects same deviation for multiple facilities, system creates separate rows (one per facility)
  ###########################################################################
  @Positive
  Scenario Outline: System-generated deviations for multiple facilities should create separate rows per facility at "<ApplicationStage>"
    Given system rules are executed under "<ApplicationStage>" for "<ProductType>"
    And the system identifies deviation "<DeviationName>" applicable for Facility "<FacilityA>" and Facility "<FacilityB>"
    When user navigates to deviation table
    Then system should create two separate deviation rows in the deviation grid: one for "<FacilityA>" and one for "<FacilityB>"
    And Deal/Facility ID column should show respective Facility IDs in the first column
    Examples:
      | ApplicationStage   | ProductType   | DeviationName    | FacilityA | FacilityB |
      | <ApplicationStage> | <ProductType> | INTEREST_MISALGN | F003      | F004      |
  ###########################################################################
  # SCENARIO 9: Approval / Reject / Forward - Literal Steps
  ###########################################################################
  #${ApplicationStage:["DDE","Credit Approval"]}
  @Positive
  Scenario Outline: User should be able to Approve a deviation from Approval screen at "<ApplicationStage>"
    Given there is a deviation row "<DeviationName>" for "<FacilityID>" visible in the approval tab under "<ApplicationStage>" for "<ProductType>"
    When user selects the deviation row "<DeviationName>"
    And user clicks the "Approve" button
    Then system should mark the deviation as "Approved"
    And the deviation should remain visible in the deviation table (status = Approved)
    Examples:
      | ApplicationStage   | ProductType   | DeviationName  | FacilityID |
      | <ApplicationStage> | <ProductType> | TENOR_MISMATCH | F001       |
  #${ApplicationStage:["DDE","Credit Approval"]}
  @Positive
  Scenario Outline: User should be able to Reject a deviation from Approval screen at "<ApplicationStage>"
    Given there is a deviation row "<DeviationName>" for "<FacilityID>" visible in the approval tab under "<ApplicationStage>" for "<ProductType>"
    When user selects the deviation row "<DeviationName>"
    And user clicks the "Reject" button
    Then system should mark the deviation as "Rejected"
    And the deviation should remain visible in the deviation table (status = Rejected)
    Examples:
      | ApplicationStage   | ProductType   | DeviationName | FacilityID |
      | <ApplicationStage> | <ProductType> | LIMIT_EXCEED  | F001       |
  ###########################################################################
  # SCENARIO 10: Deviation History (with preconditions)
  ###########################################################################
  @Positive
  Scenario Outline: Deviation History should display deal-level and facility-level deviations when there are approved or rejected deviations at "<ApplicationStage>"
    Given application has deviations that are Approved / Rejected under "<ApplicationStage>" for "<ProductType>"
    When user navigates to View History under "<ApplicationStage>"
    Then system should display deviation history records for both deal-level and facility-level deviations
    And Deal/Facility ID column should be visible in the first column
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 11: CAM Report Display
  # Applicable for credit/tranche/disbursal reporting
  ###########################################################################
  #${ApplicationStage:["Credit Approval","Tranche Approval","Disbursal"]}
  @Positive
  Scenario Outline: CAM Report should show Deal Facility ID for all deviations at "<ApplicationStage>"
    When user opens CAM Report for "<ApplicationStage>" for "<ProductType>"
    Then system should display Deal/Facility ID next to the Deviation column as the first identifier
    And system should show Deal/Application Number for deal-level deviations in Deal/Facility ID column
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 12: Sorting Logic on History (explicit)
  ###########################################################################
  @Positive
  Scenario Outline: Deviation History should follow confirmed sorting logic at "<ApplicationStage>"
    When user reviews the history table under "<ApplicationStage>" for "<ProductType>"
    Then system should display deal-level deviations at the top sorted by deviation level
    And system should display facility-level deviations below them sorted by deviation level
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 13: Post-Bifurcation Behavior (Critical)
  ###########################################################################
  #${ApplicationStage:["Tranche Approval","Disbursal"]}
  @Positive
  Scenario Outline: Only facility-level deviations should be visible after Facility Initiation stage (post-bifurcation)
    Given application is in a post-bifurcation stage for "<ProductType>"
    When user views the deviation grid under "<ApplicationStage>"
    Then system should display only facility-level deviations in the deviation grid
    And system should not display any deal-level deviations
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 14: Facility Filter on specific screens (Credit Approval, Tranche Initiation, Tranche Approval)
  # Filters deviations by selected facility
  # Note: This block applies only to the listed stages
  ###########################################################################
  #${ApplicationStage:["Credit Approval","Tranche Initiation","Tranche Approval"]}
  @Positive
  Scenario Outline: Facility filter dropdown should show deviations only for selected facility at "<ApplicationStage>"
    Given user is on the deviation table under "<ApplicationStage>" for "<ProductType>"
    When user selects Facility "<FacilityID>" from the facility filter dropdown
    Then the deviation table should refresh and display only deviations mapped to "<FacilityID>"
    And Deal/Facility ID column should show "<FacilityID>" in the first column for each displayed row
    Examples:
      | ApplicationStage   | ProductType   | FacilityID |
      | <ApplicationStage> | <ProductType> | F007       |
  ###########################################################################
  # SCENARIO 15: Negative - No Facilities configured (discarded in review)
  # (Kept commented for reference; test discarded as per 3 Amigos)
  ###########################################################################
  # NOTE: This test is intentionally discarded because the application context requires at least one facility.
  # @Edge
  # Scenario Outline: Facility LOV should show "No Data available" when no facilities configured at "<ApplicationStage>"
  #     When user opens the Facility LOV under Raise Manual Deviation at "<ApplicationStage>"
  #     Then system should show "No Data available"
  #     Examples:
  #       | ApplicationStage   | ProductType   |
  #       | <ApplicationStage> | <ProductType> |
  ###########################################################################
  # SCENARIO 16: Misc UI Validations (column persistence, pagination, filter retention)
  ###########################################################################
  @Positive
  Scenario Outline: Deal Facility ID column and other grid columns should persist after pagination and rerun at "<ApplicationStage>"
    When user paginates the deviation grid under "<ApplicationStage>" for "<ProductType>"
    And user clicks "Rerun Policy"
    Then Deal/Facility ID column should remain the first column and visible
    And sorting and filter selections should persist where applicable
    Examples:
      | ApplicationStage   | ProductType   |
      | <ApplicationStage> | <ProductType> |
