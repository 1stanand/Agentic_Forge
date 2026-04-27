@DevTrack
@GA-9.0
@Epic-Epic-HD-Bank-GA-9.0
@AuthoredBy-anand.singh1
@NotImplemented
@Order
@CAS-256008
Feature: Credit Card Application – Guarantor Integration Across Application Lifecycle

  # Purpose:
  # - Ensure Guarantor can be captured as an applicant type in Credit Card applications
  # - Ensure Guarantor participates in compliance, verification, decisioning and integrations


###============= GUARANTOR OPTION VISIBILITY =============================

  Scenario Outline: At <ApplicationStage> : Verify Presence of Guarantor Option on Applicant Details Page in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens an application of "<ApplicationStage>" stage present in context from application grid
    And user opens applicant info page of "<ApplicationStage>"
    And user checks values for 'Applicant Type' dropdown
    Then user should be able to see 'Guarantor' present in that field
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CCDE             |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Recommendation   |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CreditApproval   |

###============= ADD EXISTING INDIVIDUAL CUSTOMER AS GUARANTOR =============================

  Scenario Outline: At <ApplicationStage> : Add Existing Individual Customer as Guarantor in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user adds another new existing individual applicant with applicant type as "Guarantor" and application id at "<ApplicationStage>"
    Then additional existing individual applicant with applicant type as "Guarantor" should be displayed in applicant information page
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CCDE             |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Recommendation   |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CreditApproval   |

###============= EDIT INDIVIDUAL GUARANTOR – IDENTIFICATION DETAILS =============================

  Scenario Outline: At <ApplicationStage> : Edit Identification Details of "Individual" Guarantor to add <IdentificationType> in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens applicant information page of "<ApplicationStage>"
    And user views and edit applicant details for "Individual" "Guarantor" applicant type
    And user open identification details accordion
    And user "Delete" for identification details
    And user reads data from the excel file "personal_information_end_flow.xlsx" under sheet "identification_details" and row <rowNum>
    And user add "all" identification details of type "<IdentificationType>"
    Then Identification type of type "<IdentificationType>" should be added successfully
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | IdentificationType        | rowNum |
      | CAS_256008_CC | CCDE             | Voter's ID                |        |
      | CAS_256008_CC | CCDE             | Aadhar No.                |        |
      | CAS_256008_CC | CCDE             | PAN                       |        |
      | CAS_256008_CC | CCDE             | KYC Identification Number |        |
      | CAS_256008_CC | CCDE             | PASSPORT                  |        |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | IdentificationType        | rowNum |
      | CAS_256008_CC | Recommendation   | Voter's ID                |        |
      | CAS_256008_CC | Recommendation   | Aadhar No.                |        |
      | CAS_256008_CC | Recommendation   | PAN                       |        |
      | CAS_256008_CC | Recommendation   | KYC Identification Number |        |
      | CAS_256008_CC | Recommendation   | PASSPORT                  |        |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | IdentificationType        | rowNum |
      | CAS_256008_CC | CreditApproval   | Voter's ID                |        |
      | CAS_256008_CC | CreditApproval   | Aadhar No.                |        |
      | CAS_256008_CC | CreditApproval   | PAN                       |        |
      | CAS_256008_CC | CreditApproval   | KYC Identification Number |        |
      | CAS_256008_CC | CreditApproval   | PASSPORT                  |        |



###============= GUARANTOR VIEW VALIDATION =============================
  Scenario Outline: At <ApplicationStage> : Validate Guarantor Details Can Be Viewed in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens an application of "<ApplicationStage>" stage present in context from application grid
    And user opens applicant information page of "<ApplicationStage>"
    Then user should be able to see guarantor details in application

    @CCDE
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CCDE             |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Recommendation   |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Credit Approval  |

    @KYC
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | KYC              |

    @CardManagement
    Examples:
      | LogicalID     | ApplicationStage       |
      | CAS_256008_CC | Card Management System |


###============= EDIT INDIVIDUAL GUARANTOR – ADDRESS DETAILS =============================

  Scenario Outline: At <ApplicationStage> : Edit Address Details of "Individual" Guarantor to add <AddressType> in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens applicant information page of "<ApplicationStage>"
    And user views and edit applicant details for "Individual" "Guarantor" applicant type
    And user opens address details tab of personal information page
    And user add "<AddressType>" in personal information
    And user edits "<AddressType>" details
    Then "<AddressType>" should be edited successfully
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | AddressType                |
      | CAS_256008_CC | CCDE             | Additional Address         |
      | CAS_256008_CC | CCDE             | Alternate Business Address |
      | CAS_256008_CC | CCDE             | Office/ Business Address   |
      | CAS_256008_CC | CCDE             | Permanent Address          |
      | CAS_256008_CC | CCDE             | Residential Address        |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | AddressType                |
      | CAS_256008_CC | Recommendation   | Additional Address         |
      | CAS_256008_CC | Recommendation   | Alternate Business Address |
      | CAS_256008_CC | Recommendation   | Office/ Business Address   |
      | CAS_256008_CC | Recommendation   | Permanent Address          |
      | CAS_256008_CC | Recommendation   | Residential Address        |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | AddressType                |
      | CAS_256008_CC | Credit Approval  | Additional Address         |
      | CAS_256008_CC | Credit Approval  | Alternate Business Address |
      | CAS_256008_CC | Credit Approval  | Office/ Business Address   |
      | CAS_256008_CC | Credit Approval  | Permanent Address          |
      | CAS_256008_CC | Credit Approval  | Residential Address        |

###============= EDIT INDIVIDUAL GUARANTOR – EMPLOYMENT DETAILS =============================
  Scenario Outline: At <ApplicationStage> : Edit Employment Financial plus Liability Details of "Individual" Guarantor to add <OccupationType> in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens applicant information page of "<ApplicationStage>"
    And user views and edit applicant details for "Individual" "Guarantor" applicant type
    And user open Employment Details page on the basis of "<ApplicationStage>"
    And user deletes the employment details
    And user reads data from the excel file "employment_details.xlsx" under sheet "home" and row <EMP_ROW_NUM>
    And user fill employment details with Occupation Type as "<OccupationType>"
    And user open financial details for "<OccupationType>"
    And user reads data from the excel file "financial_details.xlsx" under sheet "liability_details" and row <FIN_ROW_NUM>
    And user fill "multiple" liability details
    And user Save and Compute the financial details
    And user waits for notification message
    Then liability details added successfully

    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | OccupationType | EMP_ROW_NUM | FIN_ROW_NUM |
      | CAS_256008_CC | CCDE             | Salaried       |             |             |
      | CAS_256008_CC | CCDE             | SEP            |             |             |
      | CAS_256008_CC | CCDE             | SENP           |             |             |
      | CAS_256008_CC | CCDE             | Agriculture    |             |             |
      | CAS_256008_CC | CCDE             | Others         |             |             |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | OccupationType | EMP_ROW_NUM | FIN_ROW_NUM |
      | CAS_256008_CC | Recommendation   | Salaried       |             |             |
      | CAS_256008_CC | Recommendation   | SEP            |             |             |
      | CAS_256008_CC | Recommendation   | SENP           |             |             |
      | CAS_256008_CC | Recommendation   | Agriculture    |             |             |
      | CAS_256008_CC | Recommendation   | Others         |             |             |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | OccupationType | EMP_ROW_NUM | FIN_ROW_NUM |
      | CAS_256008_CC | CreditApproval   | Salaried       |             |             |
      | CAS_256008_CC | CreditApproval   | SEP            |             |             |
      | CAS_256008_CC | CreditApproval   | SENP           |             |             |
      | CAS_256008_CC | CreditApproval   | Agriculture    |             |             |
      | CAS_256008_CC | CreditApproval   | Others         |             |             |


###============= COPY APPLICATION WITH INDIVIDUAL GUARANTOR =============================

  Scenario Outline: From <ApplicationStage> : Copy Credit Card Application with Individual Guarantor using <CopyParameter>
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user reads data from the excel file "copy_application.xlsx" under sheet "credit" and row 34
    When user navigates to copy application screen
    And user search the application using "<CopyParameter>" of "Individual" type on "<ApplicationStage>" of "Credit Card Application" for "" with "" on copy application screen
    And user copy the application
    And generated application number should be available on "CCDE" stage in application grid
    And user opens an application of "CCDE" stage present in context from application grid
    And user opens applicant info page of "CCDE"
    Then additional existing individual applicant with applicant type as "Guarantor" should be displayed in applicant information page
    @CCDE
    Examples:
      | LogicalID     | CopyParameter           | ApplicationStage |
      | CAS_256008_CC | Application Number      | CCDE             |
      | CAS_256008_CC | CIF Number              | CCDE             |
      | CAS_256008_CC | Customer Number         | CCDE             |
      | CAS_256008_CC | Customer Name           | CCDE             |
      | CAS_256008_CC | Application Form Number | CCDE             |

    @Recommendation
    Examples:
      | LogicalID     | CopyParameter           | ApplicationStage |
      | CAS_256008_CC | Application Number      | Recommendation   |
      | CAS_256008_CC | CIF Number              | Recommendation   |
      | CAS_256008_CC | Customer Number         | Recommendation   |
      | CAS_256008_CC | Customer Name           | Recommendation   |
      | CAS_256008_CC | Application Form Number | Recommendation   |

    @CreditApproval
    Examples:
      | LogicalID     | CopyParameter           | ApplicationStage |
      | CAS_256008_CC | Application Number      | CreditApproval   |
      | CAS_256008_CC | CIF Number              | CreditApproval   |
      | CAS_256008_CC | Customer Number         | CreditApproval   |
      | CAS_256008_CC | Customer Name           | CreditApproval   |
      | CAS_256008_CC | Application Form Number | CreditApproval   |



###============= ADD EXISTING NON-INDIVIDUAL CUSTOMER AS GUARANTOR =============================

  Scenario Outline: At <ApplicationStage> : Add Existing Non-Individual Customer as Guarantor in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user adds another existing non individual applicant with applicant type as "<Applicant_Type>" and application id at "<ApplicationStage>"
    Then additional existing non individual applicant with applicant type as "<Applicant_Type>" should be displayed in applicant information page
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | CCDE             | Guarantor      |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | Recommendation   | Guarantor      |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | CreditApproval   | Guarantor      |


    ###============= EDIT NON INDIVIDUAL GUARANTOR – IDENTIFICATION DETAILS =============================

  Scenario Outline: At <ApplicationStage> : Edit Identification Details of "Non-Individual" Guarantor to add <IdentificationType> in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens applicant information page of "<ApplicationStage>"
    And user views and edit applicant details for "Non-Individual" "Guarantor" applicant type
    And user open identification details accordion
    And user "Delete" for identification details
    And user reads data from the excel file "personal_information_end_flow.xlsx" under sheet "identification_details" and row <rowNum>
    And user add "all" identification details of type "<IdentificationType>"
    Then Identification type of type "<IdentificationType>" should be added successfully
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | IdentificationType        | rowNum |

      | CAS_256008_CC | CCDE             | TIN_No                    |        |
      | CAS_256008_CC | CCDE             | Shop/Establishment Number |        |
      | CAS_256008_CC | CCDE             | UDYAM                     |        |
      | CAS_256008_CC | CCDE             | Trade License No.         |        |
      | CAS_256008_CC | CCDE             | Unique ID Number          |        |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | IdentificationType        | rowNum |
      | CAS_256008_CC | Recommendation   | TIN_No                    |        |
      | CAS_256008_CC | Recommendation   | Shop/Establishment Number |        |
      | CAS_256008_CC | Recommendation   | UDYAM                     |        |
      | CAS_256008_CC | Recommendation   | Trade License No.         |        |
      | CAS_256008_CC | Recommendation   | Unique ID Number          |        |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | IdentificationType        | rowNum |
      | CAS_256008_CC | CreditApproval   | TIN_No                    |        |
      | CAS_256008_CC | CreditApproval   | Shop/Establishment Number |        |
      | CAS_256008_CC | CreditApproval   | UDYAM                     |        |
      | CAS_256008_CC | CreditApproval   | Trade License No.         |        |
      | CAS_256008_CC | CreditApproval   | Unique ID Number          |        |



###============= EDIT NON INDIVIDUAL GUARANTOR – ADDRESS DETAILS =============================

  Scenario Outline: At <ApplicationStage> : Edit Address Details of "Non-Individual" Guarantor to add <AddressType> in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens applicant information page of "<ApplicationStage>"
    And user views and edit applicant details for "Non-Individual" "Guarantor" applicant type
    And user opens address details tab of personal information page
    And user add "<AddressType>" in personal information
    And user edits "<AddressType>" details
    Then "<AddressType>" should be edited successfully
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | AddressType                |
      | CAS_256008_CC | CCDE             | Additional Address         |
      | CAS_256008_CC | CCDE             | Alternate Business Address |
      | CAS_256008_CC | CCDE             | Office/ Business Address   |
      | CAS_256008_CC | CCDE             | Permanent Address          |
      | CAS_256008_CC | CCDE             | Residential Address        |
      | CAS_256008_CC | CCDE             | Additional Address         |
      | CAS_256008_CC | CCDE             | Alternate Business Address |
      | CAS_256008_CC | CCDE             | Office/ Business Address   |
      | CAS_256008_CC | CCDE             | Permanent Address          |
      | CAS_256008_CC | CCDE             | Residential Address        |


    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | AddressType                |
      | CAS_256008_CC | Recommendation   | Additional Address         |
      | CAS_256008_CC | Recommendation   | Alternate Business Address |
      | CAS_256008_CC | Recommendation   | Office/ Business Address   |
      | CAS_256008_CC | Recommendation   | Permanent Address          |
      | CAS_256008_CC | Recommendation   | Residential Address        |
      | CAS_256008_CC | Recommendation   | Additional Address         |
      | CAS_256008_CC | Recommendation   | Alternate Business Address |
      | CAS_256008_CC | Recommendation   | Office/ Business Address   |
      | CAS_256008_CC | Recommendation   | Permanent Address          |
      | CAS_256008_CC | Recommendation   | Residential Address        |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | AddressType                |
      | CAS_256008_CC | CreditApproval   | Additional Address         |
      | CAS_256008_CC | CreditApproval   | Alternate Business Address |
      | CAS_256008_CC | CreditApproval   | Office/ Business Address   |
      | CAS_256008_CC | CreditApproval   | Permanent Address          |
      | CAS_256008_CC | CreditApproval   | Residential Address        |
      | CAS_256008_CC | CreditApproval   | Additional Address         |
      | CAS_256008_CC | CreditApproval   | Alternate Business Address |
      | CAS_256008_CC | CreditApproval   | Office/ Business Address   |
      | CAS_256008_CC | CreditApproval   | Permanent Address          |
      | CAS_256008_CC | CreditApproval   | Residential Address        |



###============= COPY APPLICATION WITH NON-INDIVIDUAL GUARANTOR =============================

  Scenario Outline: From <ApplicationStage> : Copy Credit Card Application with Non-Individual Guarantor using <CopyParameter>
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user reads data from the excel file "copy_application.xlsx" under sheet "credit" and row 34
    When user navigates to copy application screen
    And user search the application using "<CopyParameter>" of "Non-Individual" type on "<ApplicationStage>" of "Credit Card Application" for "" with "" on copy application screen
    And user copy the application
    And generated application number should be available on "CODE" stage in application grid
    And user opens an application of "CODE" stage present in context from application grid
    And user opens applicant info page of "CCDE"
    Then additional existing individual applicant with applicant type as "Guarantor" should be displayed in applicant information page
    @CCDE
    Examples:
      | LogicalID     | CopyParameter           | ApplicationStage |
      | CAS_256008_CC | Application Number      | CCDE             |
      | CAS_256008_CC | CIF Number              | CCDE             |
      | CAS_256008_CC | Customer Number         | CCDE             |
      | CAS_256008_CC | Customer Name           | CCDE             |
      | CAS_256008_CC | Application Form Number | CCDE             |

    @Recommendation
    Examples:
      | LogicalID     | CopyParameter           | ApplicationStage |
      | CAS_256008_CC | Application Number      | Recommendation   |
      | CAS_256008_CC | CIF Number              | Recommendation   |
      | CAS_256008_CC | Customer Number         | Recommendation   |
      | CAS_256008_CC | Customer Name           | Recommendation   |
      | CAS_256008_CC | Application Form Number | Recommendation   |

    @CreditApproval
    Examples:
      | LogicalID     | CopyParameter           | ApplicationStage |
      | CAS_256008_CC | Application Number      | CreditApproval   |
      | CAS_256008_CC | CIF Number              | CreditApproval   |
      | CAS_256008_CC | Customer Number         | CreditApproval   |
      | CAS_256008_CC | Customer Name           | CreditApproval   |
      | CAS_256008_CC | Application Form Number | CreditApproval   |



###============= DELETE BOTH ADDED GUARANTORS =============================
  Scenario Outline: At <ApplicationStage> : Delete Guarantor Applicant in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user removes all another applicant present in the application
    Then application should not display additional applicants added at "<ApplicationStage>"
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CCDE             |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Recommendation   |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CreditApproval   |

###============= ADD NEW NON-INDIVIDUAL CUSTOMER AS GUARANTOR =============================
  Scenario Outline: At <ApplicationStage> : Add New Non-Individual Customer as Guarantor in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user reads data from the excel file "personal_information.xlsx" under sheet "home" and row 0
    When user adds another non individual applicant with applicant type as "<Applicant_Type>" at "<ApplicationStage>"
    Then Additional non individual applicant with applicant type as "<Applicant_Type>" should be displayed in applicant information page
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | CCDE             | Guarantor      |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | Recommendation   | Guarantor      |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | CreditApproval   | Guarantor      |


###============= VALIDATION – NON-INDIVIDUAL GUARANTOR SWAP RESTRICTION =============================

  Scenario Outline: At <ApplicationStage> : Validate That Non-Individual Guarantor Cannot Be Swapped with Primary Applicant in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user opens applicant info page of "<ApplicationStage>"
    When user swaps the primary applicant with "<AnotherApplicant>"
    Then primary applicant is not swap with proper error message
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | AnotherApplicant |
      | CAS_256008_CC | CCDE             | Guarantor        |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | AnotherApplicant |
      | CAS_256008_CC | Recommendation   | Guarantor        |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | AnotherApplicant |
      | CAS_256008_CC | CreditApproval   | Guarantor        |


###============= ADD NEW INDIVIDUAL CUSTOMER AS GUARANTOR =============================
  Scenario Outline: At <ApplicationStage> : Add New Individual Customer as Guarantor in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user reads data from the excel file "personal_information.xlsx" under sheet "home" and row 0
    When user removes all another applicant present in the application
    And user adds another individual applicant with applicant type as "<Applicant_Type>" for "<ApplicationStage>" stage
    Then additional individual applicant with applicant type as "<Applicant_Type>" should be displayed in applicant information page
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | CCDE             | Guarantor      |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | Recommendation   | Guarantor      |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | Applicant_Type |
      | CAS_256008_CC | CreditApproval   | Guarantor      |

###============= SWAP INDIVIDUAL GUARANTOR WITH PRIMARY =============================

  Scenario Outline: At <ApplicationStage> : Swap Primary Applicant with Individual Guarantor in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user opens applicant info page of "<ApplicationStage>"
    When user swaps the primary applicant with "<AnotherApplicant>"
    Then primary applicant should be swapped successfully
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | AnotherApplicant |
      | CAS_256008_CC | CCDE             | Guarantor        |
    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | AnotherApplicant |
      | CAS_256008_CC | Recommendation   | Guarantor        |
    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | AnotherApplicant |
      | CAS_256008_CC | CreditApproval   | Guarantor        |


###============= ACTIVITY LOG VALIDATION ============================= TO BE CONFIRMED BY PMG
  Scenario Outline: At <ApplicationStage> : Validate Activity Log Entry for Guarantor Details in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user opens an application of "<ApplicationStage>" stage present in context from application grid
    When user opens the activity tab
    Then user should be able to see Guarantor Details Entry created in Entry
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CCDE             |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | recommendation   |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Credit Approval  |

###============= CARD DETAILS VALIDATION – GUARANTOR RESTRICTION =============================

  Scenario Outline: At <ApplicationStage> : Validate That Guarantor Is Not Available as Add-On Applicant in Credit Card Application For <CardType>
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user reads data from the excel file "credit_card_loan_end_flow.xlsx" under sheet "card_details" and row <CardDetails_rowNum>
    When user opens an application of "<ApplicationStage>" stage present in context from application grid
    And user navigates to card details
    And user add new "<CardType>" with "All" fields
    And user checks for Guarantor in Add On Applicants
    Then guarantor should not be present in operations

    @CCDE
    Examples:
      | LogicalID     | ApplicationStage | CardDetails_rowNum | CardType     |
      | CAS_256008_CC | CCDE             | 2                  | Primary Card |
      | CAS_256008_CC | CCDE             | 3                  | Add-On Card  |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage | CardDetails_rowNum | CardType     |
      | CAS_256008_CC | Recommendation   | 2                  | Primary Card |
      | CAS_256008_CC | Recommendation   | 3                  | Add-On Card  |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage | CardDetails_rowNum | CardType     |
      | CAS_256008_CC | CreditApproval   | 2                  | Primary Card |
      | CAS_256008_CC | CreditApproval   | 3                  | Add-On Card  |



###============= DOCUMENT VISIBILITY VALIDATION =============================

  Scenario Outline: At <ApplicationStage> : Validate Guarantor Document Visibility in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user opens an application of <ApplicationStage> stage present in context from application grid
    When user navigates to Document Tab
    Then user can see guarantor documents
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CCDE             |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | RECOMMENDATION   |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Credit Approval  |


###============= DOCUMENT ACTION VALIDATION =============================

  Scenario Outline: At <ApplicationStage> : Validate Guarantor Document Actions in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user opens an application of <ApplicationStage> stage present in context from application grid
    When user selects the document with document status
      | document.xlsx | home | 360 |
      | document.xlsx | home | 361 |
      | document.xlsx | home | 362 |
      | document.xlsx | home | 363 |
    And user adds multiple additional documents
      | document.xlsx | home | 476 |
      | document.xlsx | home | 477 |
      | document.xlsx | home | 478 |
    And user selects the document with document status
      | document.xlsx | home | 476 |
      | document.xlsx | home | 477 |
      | document.xlsx | home | 478 |
    And user submit the documents with wait
    Then documents page should be saved successfully
    @CCDE
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | CCDE             |

    @Recommendation
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Recommendation   |

    @CreditApproval
    Examples:
      | LogicalID     | ApplicationStage |
      | CAS_256008_CC | Credit Approval  |




###============= GUARANTOR VISIBLE AT FII =============================
  Scenario Outline: At FII : Validate Guarantor's <FII_Fields> Details Visibility in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens an application of "FII" stage present in context from application grid
    Then On this page the grid displays "<FII_Fields>" for each applicant
    @FII
    Examples:
      | LogicalID     | FII_Fields                  |
      | CAS_256008_CC | Neo Cust ID                 |
      | CAS_256008_CC | Type                        |
      | CAS_256008_CC | Applicant Name              |
      | CAS_256008_CC | Last Verification Date      |
      | CAS_256008_CC | Current Verification Status |

###============= FII INITIATION FOR GUARANTOR =============================
  @FII
  Scenario Outline: At FII : Validate Guarantor's FII can Be Initiated Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens an application of "FII" stage present in context from application grid
    And user open Initiate Verification screen
    And user Initiate Verification
    And Initiate Verification Initiated
    And user open Field Investigation Verification page
    And user opens an application present in context from FIV grid
    And user fill all mandatory fields for Field investigation verification
    And user saves Field investigation verification
    And Field investigation verification saved successfully
    And user open Field Investigation Completion page
    And user approve FIC
    Then FI flow gets approve successfully
    And user moves to next stage
    Examples:
      | LogicalID     |
      | CAS_256008_CC |



###============= GUARANTOR KYC AT KYC STAGE =============================
  Scenario Outline: At KYC : Validate <Applicant_Type> KYC can be done in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user opens an application of "KYC" stage present in context from application grid
    And user reads data from the excel file "credit_approval.xlsx" under sheet "kyc_details" and row 8
    When user fills kyc check details for "<Applicant_Type>"
    Then Kyc Check Details should be saved successfully

    @KYC
    Examples:
      | LogicalID     | Applicant_Type |
      | CAS_256008_CC | Guarantor      |
      | CAS_256008_CC | Primary        |

###============= GUARANTOR VISIBILITY FROM ENQUIRY SCREEN =============================
  Scenario Outline: At <ApplicationStage> : Validate <Applicant_Type> Guarantor's <TAB> are Visible from Enquiry in Credit Card Application
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user navigates to Enquiry screen menu option
    And user searches for an application on enquiry screen
    And user clicks on stage hyperlink on enquiry screen
    And user opens applicant information page of "<ApplicationStage>"
    And user views and edit applicant details for "<Applicant_Type>" "Guarantor" applicant type
    And user clicks on "<TAB>" tab in customer details
    Then user should be able to view captured "<TAB>" details in disabled mode

    @CCDE
    Examples:
      | LogicalID     | Applicant_Type | ApplicationStage | TAB                  |
      | CAS_256008_CC | Non-Individual | CCDE             | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | CCDE             | Contact Person       |
      | CAS_256008_CC | Non-Individual | CCDE             | Monthly Data         |
      | CAS_256008_CC | Non-Individual | CCDE             | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | CCDE             | Contact Person       |

      | CAS_256008_CC | Individual     | CCDE             | Personal Information |
      | CAS_256008_CC | Individual     | CCDE             | Employment Details   |
      | CAS_256008_CC | Individual     | CCDE             | Financial Details    |

    @KYC
    Examples:
      | LogicalID     | Applicant_Type | ApplicationStage | TAB                  |
      | CAS_256008_CC | Non-Individual | KYC              | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | KYC              | Contact Person       |
      | CAS_256008_CC | Non-Individual | KYC              | Monthly Data         |
      | CAS_256008_CC | Non-Individual | KYC              | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | KYC              | Contact Person       |

      | CAS_256008_CC | Individual     | KYC              | Personal Information |
      | CAS_256008_CC | Individual     | KYC              | Employment Details   |
      | CAS_256008_CC | Individual     | KYC              | Financial Details    |

    @Recommendation
    Examples:
      | LogicalID     | Applicant_Type | ApplicationStage | TAB                  |
      | CAS_256008_CC | Non-Individual | Recommendation   | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | Recommendation   | Contact Person       |
      | CAS_256008_CC | Non-Individual | Recommendation   | Monthly Data         |
      | CAS_256008_CC | Non-Individual | Recommendation   | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | Recommendation   | Contact Person       |

      | CAS_256008_CC | Individual     | Recommendation   | Personal Information |
      | CAS_256008_CC | Individual     | Recommendation   | Employment Details   |
      | CAS_256008_CC | Individual     | Recommendation   | Financial Details    |

    @CreditApproval
    Examples:
      | LogicalID     | Applicant_Type | ApplicationStage | TAB                  |
      | CAS_256008_CC | Non-Individual | Credit Approval  | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | Credit Approval  | Contact Person       |
      | CAS_256008_CC | Non-Individual | Credit Approval  | Monthly Data         |
      | CAS_256008_CC | Non-Individual | Credit Approval  | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | Credit Approval  | Contact Person       |

      | CAS_256008_CC | Individual     | Credit Approval  | Personal Information |
      | CAS_256008_CC | Individual     | Credit Approval  | Employment Details   |
      | CAS_256008_CC | Individual     | Credit Approval  | Financial Details    |

    @CardManagement
    Examples:
      | LogicalID     | Applicant_Type | ApplicationStage       | TAB                  |
      | CAS_256008_CC | Non-Individual | Card Management System | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | Card Management System | Contact Person       |
      | CAS_256008_CC | Non-Individual | Card Management System | Monthly Data         |
      | CAS_256008_CC | Non-Individual | Card Management System | Creditor Debtor      |
      | CAS_256008_CC | Non-Individual | Card Management System | Contact Person       |

      | CAS_256008_CC | Individual     | Card Management System | Personal Information |
      | CAS_256008_CC | Individual     | Card Management System | Employment Details   |
      | CAS_256008_CC | Individual     | Card Management System | Financial Details    |


###============= Move Application To NEXT STAGE =============================
  @MoveToNext
  Scenario Outline: At <SourceStage> : Move Application From "<SourceStage>" to "<DestStage>"
    Given all prerequisite are performed in previous scenario of "Credit Card Application" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user moves application from "<SourceStage>" stage to application of "Credit Card Application" product type as "" applicant at "<DestStage>" for "" with "" stage without opening it
    Then Application should move to "<DestStage>" Stage
    @CCDE
    Examples:
      | LogicalID     | SourceStage | DestStage |
      | CAS_256008_CC | CCDE        | KYC       |

    @KYC
    Examples:
      | LogicalID     | SourceStage | DestStage      |
      | CAS_256008_CC | KYC         | Recommendation |

    @Recommendation
    Examples:
      | LogicalID     | SourceStage    | DestStage       |
      | CAS_256008_CC | Recommendation | Credit Approval |

    @CreditApproval
    Examples:
      | LogicalID     | SourceStage     | DestStage              |
      | CAS_256008_CC | Credit Approval | Card Management System |



