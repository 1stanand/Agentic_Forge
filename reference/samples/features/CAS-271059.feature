@HDB
@GA-9.0
@Epic-HDB_MAL_Development
@AuthoredBy-anand.singh1
@CAS-271059
@Order

Feature: Historical Valuations For Copied Collateral

#############################################################################################################
## -- Pre-Requisites:
## ---------- User has Authority To view and Edit The Waiver Allocation Master
## ---------- User has maker checker authority
#############################################################################################################


##########################################################################################
#### CLARIFICATIONS NEEDED FOR SCENARIOS IF THEY SHOULD BE INCLUDED
##  Validate behaviour when Config is changed to Increase eligible months
##  Validate behaviour when Config is changed to Decrease eligible months
##########################################################################################

#######################################################################################################################################
## --->>>>> Implementation Note:
## --- ALL Application IDs must be maintained in the context of the corresponding Logical ID for correct mapping validation.
##
## --->>>> Historical Data Dependency:
## --- Valuation details created in Pre_Requisite_002 are expected to be available in context and are reused here for validation.
##
## --->>>>> Test Design Consideration:
## --- Existing repository steps are used without introducing additional explicit test data.
## --- Mapping validation relies on the underlying system behavior,
##         so how data is to be validated from previous Valuations becomes Implementation Call
##
#######################################################################################################################################
########################################################################################################################
####------------------------------------------ DATA PREPARATION STEPS -----------------------------------------------###
########################################################################################################################

### --- Create an Application -- Add Collateral in it
  @DataPreparation @DDE
  Scenario Outline: [LogicalID-<LogicalID>] Pre_Requisite_001 : Add Collateral To Base Application
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user opens Collateral Page for adding new collateral at "<ApplicationStage>" stage
    And user reads data from the excel file "collateral.xlsx" under sheet "asset_details" and row <Collateral_assetDetail_rowNum>
    And user selects collateral type along with collateral sub type
    And user fills mandatory fields for given collateral sub type
    And user checks the duplicates on collateral dedupe check
    And user saves the collateral data
    And user reads Global Collateral Number generated from Collateral Page              ## New Step
    And user sets Global Collateral Number in test context                              ## New Step
    Then user is able to save the data successfully
    Examples:
    ### Collateral Of These Applications will be used to Copy Collateral in Other applications
      | LogicalID                              | ProductType | ApplicationStage | Collateral_assetDetail_rowNum |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          | DDE              |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         | DDE              |                               |

      ## These Applications Have New Collaterals, Which Will be used to validate history is not present for new Collaterals
      | CAS_271059_NEW_NO_HISTORY_PL           | PL          | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_HL           | HL          | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_MAL          | MAL         | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_LAP          | LAP         | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_CV           | CV          | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_CEQ          | CEQ         | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_Omni         | Omni        | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_Agri         | Agri        | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_MHF          | MHF         | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_CC           | CC          | DDE              |                               |
      | CAS_271059_NEW_NO_HISTORY_EDU          | EDU         | DDE              |                               |


## -- Create More Applications with Copying Same Collateral - Create Valuation History
  @DataPreparation @DDE
  Scenario Outline: [LogicalID-<LogicalID>][RevisitCount-<RevisitCount>] Pre_Requisite_002 : Chain Collateral History
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user opens an application of "<ProductType>" product type as "indiv" applicant at "DDE" for "" with "" from application grid
    And set Application ID in the thread context
    And user opens Collateral Page
    And user searches for an existing internal collateral using Global Collateral Number
    And user links the collateral with the application
    And user saves the collateral data

    And user open collateral investigation page
    And user opens application after searching the created application       ## New Step
    And user clicks on initiate valuation valuation button
    And user selects valuation type as "Empaneled Valuer"
    And user selects valuation agency
    And user initiate valuation for collateral investigation

    And user open collateral investigation verification page
    And user opens application after searching the created application       ## New Step
    And user fills all required fields of "Valuation"
    And user "Save&Proceed" the "Valuation" details

    And user open collateral investigation completion page
    And user opens application after searching the created application       ## New Step
    And user completes collateral Valuation                                                           ## New Step

    Then user should be able to see "Success" pop-up notifier with Message "Collateral Valuation Completed Successfully"
    Examples:
      | LogicalID                              | ProductType | RevisitCount |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          | 4            |

      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |              |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         | 1            |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         | 2            |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         | 3            |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         | 4            |


########################################################################################################################
####----------------------------------------- MANIPULATE GOLDEN DB DATA ---------------------------------------------###
########################################################################################################################

  @DataPreparation @DDE
  Scenario Outline: [LogicalID-<LogicalID>] Pre_Requisite_003 : Update Historical Valuation Dates Through DB Manipulation
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user reads all Application ID and Global Collateral Number from test context                                                ## New Step
    When user identifies valuation record for application sequence "<ApplicationSequence>" using Global Collateral Number           ## New Step
    And user updates valuation date in database by "<ValuationDateOffsetInMonths>" months for the identified valuation record       ## New Step
    And user commits the database transaction                                                                                       ## New Step
    Then user is able to update valuation date successfully in database                                                             ## New Step
    And updated valuation record is available for further execution                                                                 ## New Step
    Examples:
      | LogicalID                            | ProductType   | ApplicationSequence | ValuationDateOffsetInMonths |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL | Personal Loan | 1                   | 2                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL | Personal Loan | 2                   | 4                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL | Personal Loan | 3                   | 7                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL | Personal Loan | 4                   | 9                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL | Personal Loan | 5                   | 12                          |

      | CAS_271059_COPIED_HISTORICAL_COLL_HL | Home Loan     | 1                   | 2                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL | Home Loan     | 2                   | 4                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL | Home Loan     | 3                   | 7                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL | Home Loan     | 4                   | 9                           |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL | Home Loan     | 5                   | 12                          |


########################################################################################################################
####-------------------------------------- PREPARE TESTABLE APPLICATIONS --------------------------------------------###
########################################################################################################################

  @DataPreparation @DDE
  Scenario Outline: [LogicalID-<LogicalID>] Pre_Requisite_004 : Generate Test Application to be used in tests
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user opens an application of "<ProductType>" product type as "indiv" applicant at "DDE" for "" with "" from application grid
    And set Application ID in the thread context
    When user opens Collateral Page

    And user add new collateral details
    And user reads data from the excel file "collateral.xlsx" under sheet "asset_details" and row <Collateral_assetDetail_rowNum>
    And user selects collateral type along with collateral sub type
    And user fills mandatory fields for given collateral sub type
    And user checks the duplicates on collateral dedupe check
    And user saves the collateral data

    And user searches for an existing internal collateral using Global Collateral Number
    And user links the collateral with the application
    And user saves the collateral data
    Then user is able to save the data successfully
    Examples:
      | LogicalID                              | ProductType | Collateral_assetDetail_rowNum |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |                               |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |                               |

########################################################################################################################
####------------------------------------------ STORY TEST CASES START -----------------------------------------------###
########################################################################################################################


###------------------------------------------------- TEST SECTIONS --------------------------------------------------###


########################################################################################################################
####----------------------------------------------- CII TEST CASES --------------------------------------------------###
########################################################################################################################

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_001 : CII : Validate Application ID column is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    When user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    Then user should be able to validate Application ID column is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CII : Validate Application ID is displayed against each valuation entry in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate Application ID is displayed against each valuation entry in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CII : Validate historical valuation records are fetched only for matching copied collateral reference
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate historical valuation records are fetched only for matching copied collateral reference
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CII : Validate no blank historical valuation row is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate no blank historical valuation row is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_003 : CII : Validate historical valuation records display application id different from current application id
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate historical valuation records display application id different from current application id
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_004 : CII : Validate multiple eligible historical valuation records are displayed as separate rows in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate multiple eligible historical valuation records are displayed as separate rows in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_005 : CII : Validate first row shows current application number in "Application Number" Column
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate first row shows current application number in "Application Number" Column
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_005 : CII : Validate multiple eligible historical valuation records are sorted in separate rows in descending order in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate multiple eligible historical valuation records are sorted by historical application numbers are sorted based on valuation dates in descending order
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_006 : CII : Validate only historical valuation records within configured validity period are displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate only historical valuation records within configured validity period are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_007 : CII : Validate historical valuation records outside configured validity period are not displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate historical valuation records outside configured validity period are not displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_008 : CII : Validate historical valuation records are displayed in read only mode in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate historical valuation records are displayed in read only mode in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_009 : CII : Validate historical valuation records display valuation agency valuation date valuation amount collateral reference and application id in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate historical valuation records display following columns in show history grid
      | Valuation Agency  |
      | Evaluated By      |
      | Evaluation Method |
      | Valuation Date    |
      | Evaluated Value   |
      | Status            |
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CII : Validate historical valuation rows are displayed with correct mapping of application id and valuation details in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate historical valuation rows are displayed with correct mapping of application id and valuation details in show history grid
      | Valuation Agency  |
      | Evaluated By      |
      | Evaluation Method |
      | Valuation Date    |
      | Evaluated Value   |
      | Status            |
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CII : Validate latest eligible historical valuation record is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate latest eligible historical valuation record is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CII : Validate oldest eligible historical valuation record is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate oldest eligible historical valuation record is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CII
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CII : Validate no historical valuation records are displayed for new collaterals
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    When user opens application after searching the created application with "New Collateral"
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    And user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                      | ProductType |
      | CAS_271059_NEW_NO_HISTORY_PL   | PL          |
      | CAS_271059_NEW_NO_HISTORY_HL   | HL          |
      | CAS_271059_NEW_NO_HISTORY_MAL  | MAL         |
      | CAS_271059_NEW_NO_HISTORY_LAP  | LAP         |
      | CAS_271059_NEW_NO_HISTORY_CV   | CV          |
      | CAS_271059_NEW_NO_HISTORY_CEQ  | CEQ         |
      | CAS_271059_NEW_NO_HISTORY_Omni | Omni        |
      | CAS_271059_NEW_NO_HISTORY_Agri | Agri        |
      | CAS_271059_NEW_NO_HISTORY_MHF  | MHF         |
      | CAS_271059_NEW_NO_HISTORY_CC   | CC          |
      | CAS_271059_NEW_NO_HISTORY_EDU  | EDU         |


  @CII @MoveToNext
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CII : Validate Application Can be moved to Next Stage from CII
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    When user opens application after searching the created application       ## New Step
    And user clicks on initiate valuation valuation button
    And user selects valuation type as "Empaneled Valuer"
    And user selects valuation agency
    And user initiate valuation for collateral investigation
    Then application should move to "CIV" stage
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

      | CAS_271059_NEW_NO_HISTORY_PL           | PL          |
      | CAS_271059_NEW_NO_HISTORY_HL           | HL          |
      | CAS_271059_NEW_NO_HISTORY_MAL          | MAL         |
      | CAS_271059_NEW_NO_HISTORY_LAP          | LAP         |
      | CAS_271059_NEW_NO_HISTORY_CV           | CV          |
      | CAS_271059_NEW_NO_HISTORY_CEQ          | CEQ         |
      | CAS_271059_NEW_NO_HISTORY_Omni         | Omni        |
      | CAS_271059_NEW_NO_HISTORY_Agri         | Agri        |
      | CAS_271059_NEW_NO_HISTORY_MHF          | MHF         |
      | CAS_271059_NEW_NO_HISTORY_CC           | CC          |
      | CAS_271059_NEW_NO_HISTORY_EDU          | EDU         |


########################################################################################################################
####------------------------------------------ OTHER CONFIG CASES - CII ---------------------------------------------###
########################################################################################################################

  @CII @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_011 : CII : Validate no historical valuation records are displayed when all previous valuations lie outside configured validity period
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_011 : CII : Validate no blank historical valuation row is displayed in show history grid when no eligible historical valuation exists
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate no blank historical valuation row is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_012 : CII : Validate no historical valuation records are displayed when "valid month" configuration is disabled
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CII @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_013 : CII : Validate no historical valuation records are displayed when "valid month" configuration is not defined
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    And user open collateral investigation page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    When user checks for values in show history grid for "Valuation" at CII
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |



########################################################################################################################
####----------------------------------------------- CIV TEST CASES --------------------------------------------------###
########################################################################################################################

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_001 : CIV : Validate Application ID column is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user open collateral investigation verification page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    Then user should be able to validate Application ID column is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CIV : Validate Application ID is displayed against each valuation entry in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate Application ID is displayed against each valuation entry in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CIV : Validate historical valuation records are fetched only for matching copied collateral reference
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate historical valuation records are fetched only for matching copied collateral reference
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CIV : Validate no blank historical valuation row is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate no blank historical valuation row is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_003 : CIV : Validate historical valuation records display application id different from current application id
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate historical valuation records display application id different from current application id
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_004 : CIV : Validate multiple eligible historical valuation records are displayed as separate rows in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate multiple eligible historical valuation records are displayed as separate rows in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_005 : CIV : Validate first row shows current application number in "Application Number" Column
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate first row shows current application number in "Application Number" Column
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_005 : CIV : Validate multiple eligible historical valuation records are sorted in separate rows in descending order in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate multiple eligible historical valuation records are sorted by historical application numbers are sorted based on valuation dates in descending order
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_006 : CIV : Validate only historical valuation records within configured validity period are displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate only historical valuation records within configured validity period are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_007 : CIV : Validate historical valuation records outside configured validity period are not displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate historical valuation records outside configured validity period are not displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_008 : CIV : Validate historical valuation records are displayed in read only mode in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate historical valuation records are displayed in read only mode in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_009 : CIV : Validate historical valuation records display valuation agency valuation date valuation amount collateral reference and application id in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate historical valuation records display following columns in show history grid
      | Valuation Agency  |
      | Evaluated By      |
      | Evaluation Method |
      | Valuation Date    |
      | Evaluated Value   |
      | Status            |
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIV : Validate historical valuation rows are displayed with correct mapping of application id and valuation details in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate historical valuation rows are displayed with correct mapping of application id and valuation details in show history grid
      | Valuation Agency  |
      | Evaluated By      |
      | Evaluation Method |
      | Valuation Date    |
      | Evaluated Value   |
      | Status            |
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIV : Validate latest eligible historical valuation record is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate latest eligible historical valuation record is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIV : Validate oldest eligible historical valuation record is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate oldest eligible historical valuation record is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIV
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIV : Validate no historical valuation records are displayed for new collaterals
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user open collateral investigation verification page
    And user opens application after searching the created application with "New Collateral"
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    And user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                      | ProductType |
      | CAS_271059_NEW_NO_HISTORY_PL   | PL          |
      | CAS_271059_NEW_NO_HISTORY_HL   | HL          |
      | CAS_271059_NEW_NO_HISTORY_MAL  | MAL         |
      | CAS_271059_NEW_NO_HISTORY_LAP  | LAP         |
      | CAS_271059_NEW_NO_HISTORY_CV   | CV          |
      | CAS_271059_NEW_NO_HISTORY_CEQ  | CEQ         |
      | CAS_271059_NEW_NO_HISTORY_Omni | Omni        |
      | CAS_271059_NEW_NO_HISTORY_Agri | Agri        |
      | CAS_271059_NEW_NO_HISTORY_MHF  | MHF         |
      | CAS_271059_NEW_NO_HISTORY_CC   | CC          |
      | CAS_271059_NEW_NO_HISTORY_EDU  | EDU         |


  @CIV @MoveToNext
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIV : Validate Application Can be moved to Next Stage from CIV
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"

    When user open collateral investigation verification page
    And user opens application after searching the created application       ## New Step
    And user fills all required fields of "Valuation"
    And user "Save&Proceed" the "Valuation" details


    Then application should move to "CIC" stage
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

      | CAS_271059_NEW_NO_HISTORY_PL           | PL          |
      | CAS_271059_NEW_NO_HISTORY_HL           | HL          |
      | CAS_271059_NEW_NO_HISTORY_MAL          | MAL         |
      | CAS_271059_NEW_NO_HISTORY_LAP          | LAP         |
      | CAS_271059_NEW_NO_HISTORY_CV           | CV          |
      | CAS_271059_NEW_NO_HISTORY_CEQ          | CEQ         |
      | CAS_271059_NEW_NO_HISTORY_Omni         | Omni        |
      | CAS_271059_NEW_NO_HISTORY_Agri         | Agri        |
      | CAS_271059_NEW_NO_HISTORY_MHF          | MHF         |
      | CAS_271059_NEW_NO_HISTORY_CC           | CC          |
      | CAS_271059_NEW_NO_HISTORY_EDU          | EDU         |


########################################################################################################################
####--------------------------------------------- OTHER CONFIG CASES -CIV -------------------------------------------###
########################################################################################################################

  @CIV @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_011 : CIV : Validate no historical valuation records are displayed when all previous valuations lie outside configured validity period
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_011 : CIV : Validate no blank historical valuation row is displayed in show history grid when no eligible historical valuation exists
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate no blank historical valuation row is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_012 : CIV : Validate no historical valuation records are displayed when "valid month" configuration is disabled
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIV @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_013 : CIV : Validate no historical valuation records are displayed when "valid month" configuration is not defined
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIV
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |



########################################################################################################################
####----------------------------------------------- CIC TEST CASES --------------------------------------------------###
########################################################################################################################

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_001 : CIC : Validate Application ID column is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user open collateral investigation completion page
    And user opens application after searching the created application
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    Then user should be able to validate Application ID column is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CIC : Validate Application ID is displayed against each valuation entry in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate Application ID is displayed against each valuation entry in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CIC : Validate historical valuation records are fetched only for matching copied collateral reference
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate historical valuation records are fetched only for matching copied collateral reference
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_002 : CIC : Validate no blank historical valuation row is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate no blank historical valuation row is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_003 : CIC : Validate historical valuation records display application id different from current application id
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate historical valuation records display application id different from current application id
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_004 : CIC : Validate multiple eligible historical valuation records are displayed as separate rows in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate multiple eligible historical valuation records are displayed as separate rows in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_005 : CIC : Validate first row shows current application number in "Application Number" Column
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate first row shows current application number in "Application Number" Column
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_005 : CIC : Validate multiple eligible historical valuation records are sorted in separate rows in descending order in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate multiple eligible historical valuation records are sorted by historical application numbers are sorted based on valuation dates in descending order
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_006 : CIC : Validate only historical valuation records within configured validity period are displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate only historical valuation records within configured validity period are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_007 : CIC : Validate historical valuation records outside configured validity period are not displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate historical valuation records outside configured validity period are not displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_008 : CIC : Validate historical valuation records are displayed in read only mode in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate historical valuation records are displayed in read only mode in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_009 : CIC : Validate historical valuation records display valuation agency valuation date valuation amount collateral reference and application id in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate historical valuation records display following columns in show history grid
      | Valuation Agency  |
      | Evaluated By      |
      | Evaluation Method |
      | Valuation Date    |
      | Evaluated Value   |
      | Status            |
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIC : Validate historical valuation rows are displayed with correct mapping of application id and valuation details in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate historical valuation rows are displayed with correct mapping of application id and valuation details in show history grid
      | Valuation Agency  |
      | Evaluated By      |
      | Evaluation Method |
      | Valuation Date    |
      | Evaluated Value   |
      | Status            |
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIC : Validate latest eligible historical valuation record is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate latest eligible historical valuation record is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIC : Validate oldest eligible historical valuation record is displayed in show history grid
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate oldest eligible historical valuation record is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


  @CIC
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIC : Validate no historical valuation records are displayed for new collaterals
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user open collateral investigation completion page
    And user opens application after searching the created application with "New Collateral"
    And user clicks on "View Details"
    And user clicks on "Show History" for "Valuation"
    And user clicks on "Completed"
    And user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                      | ProductType |
      | CAS_271059_NEW_NO_HISTORY_PL   | PL          |
      | CAS_271059_NEW_NO_HISTORY_HL   | HL          |
      | CAS_271059_NEW_NO_HISTORY_MAL  | MAL         |
      | CAS_271059_NEW_NO_HISTORY_LAP  | LAP         |
      | CAS_271059_NEW_NO_HISTORY_CV   | CV          |
      | CAS_271059_NEW_NO_HISTORY_CEQ  | CEQ         |
      | CAS_271059_NEW_NO_HISTORY_Omni | Omni        |
      | CAS_271059_NEW_NO_HISTORY_Agri | Agri        |
      | CAS_271059_NEW_NO_HISTORY_MHF  | MHF         |
      | CAS_271059_NEW_NO_HISTORY_CC   | CC          |
      | CAS_271059_NEW_NO_HISTORY_EDU  | EDU         |


  @CIC @MoveToNext
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_010 : CIC : Validate Application Can be moved to Next Stage from CIC
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"

    When user open collateral investigation completion page
    And user opens application after searching the created application       ## New Step
    And user completes collateral Valuation                                                           ## New Step


    Then application should move to "CIC" stage
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

      | CAS_271059_NEW_NO_HISTORY_PL           | PL          |
      | CAS_271059_NEW_NO_HISTORY_HL           | HL          |
      | CAS_271059_NEW_NO_HISTORY_MAL          | MAL         |
      | CAS_271059_NEW_NO_HISTORY_LAP          | LAP         |
      | CAS_271059_NEW_NO_HISTORY_CV           | CV          |
      | CAS_271059_NEW_NO_HISTORY_CEQ          | CEQ         |
      | CAS_271059_NEW_NO_HISTORY_Omni         | Omni        |
      | CAS_271059_NEW_NO_HISTORY_Agri         | Agri        |
      | CAS_271059_NEW_NO_HISTORY_MHF          | MHF         |
      | CAS_271059_NEW_NO_HISTORY_CC           | CC          |
      | CAS_271059_NEW_NO_HISTORY_EDU          | EDU         |


########################################################################################################################
####--------------------------------------------- OTHER CONFIG CASES -CIC -------------------------------------------###
########################################################################################################################

  @CIC @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_011 : CIC : Validate no historical valuation records are displayed when all previous valuations lie outside configured validity period
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_011 : CIC : Validate no blank historical valuation row is displayed in show history grid when no eligible historical valuation exists
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate no blank historical valuation row is displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_012 : CIC : Validate no historical valuation records are displayed when "valid month" configuration is disabled
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |

  @CIC @OtherConfig
  Scenario Outline: [LogicalID-<LogicalID>] : CAS_271059_013 : CIC : Validate no historical valuation records are displayed when "valid month" configuration is not defined
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
    When user checks for values in show history grid for "Valuation" at CIC
    Then user should be able to validate no historical valuation records are displayed in show history grid
    Examples:
      | LogicalID                              | ProductType |
      | CAS_271059_COPIED_HISTORICAL_COLL_PL   | PL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_HL   | HL          |
      | CAS_271059_COPIED_HISTORICAL_COLL_MAL  | MAL         |
      | CAS_271059_COPIED_HISTORICAL_COLL_LAP  | LAP         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CV   | CV          |
      | CAS_271059_COPIED_HISTORICAL_COLL_CEQ  | CEQ         |
      | CAS_271059_COPIED_HISTORICAL_COLL_Omni | Omni        |
      | CAS_271059_COPIED_HISTORICAL_COLL_Agri | Agri        |
      | CAS_271059_COPIED_HISTORICAL_COLL_MHF  | MHF         |
      | CAS_271059_COPIED_HISTORICAL_COLL_CC   | CC          |
      | CAS_271059_COPIED_HISTORICAL_COLL_EDU  | EDU         |


