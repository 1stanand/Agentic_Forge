@DevTrack
@GA-9.0
@Epic-HdBankGA9.0
@AuthoredBy-anand.singh1
@ImplementedBy-yash.sharma
@Order
@E2EOrder
@CAS-247073
@Perishable
Feature: Committee Decision Logic Enhancement

    ######==================================== PURPOSE ====================================
    ##### - Validate enhanced committee decision logic for Minimum Approval, Decision Maker and Majority committees
    ##### - Ensure 100% participation rules are enforced where applicable
    ##### - Prevent premature verdict declaration and indefinite pending states
    ##### - Ensure verdict vs committee status behavior is correct
    ##### - Ensure backward compatibility when new configuration is disabled
    #####==================================================================================

    ######=============================== Pre-Requisites =================================
    ###### Configuration :: configuration "cas.committee.wait.pending decisions" should be true
    ######-------------------------- DATA PREPARATION POINTS------------------------------
    #####  Committees to be maintained as Sequential Committees. The Following will work for Parallel Committees as well.
    #####  Minimum Approval Committee is Maintained with 3 Members as Minimum Approval.
    #####  Decision Maker Committee is Maintained with 2 Decision Maker, Decision maker users are Row 1 and Row 2 in "LoginDetailsCAS.xlsx" under "CommitteeUser"
    #####==================================================================================

    ######====================================================================
    ###### Setting PRE-REQUISITE Scenarios
    ###### We Are Creating 24 Loans in Total
    ######      4 Product Types for Each Committee Type :: That is 12 Loans :: At Credit Approval
    ######      4 Product Types for Each Committee Type :: That is 12 Loans :: At App Update Approval
    ###### Out Of 24 Loans, 6 Loans Are Testing Configuration Off, 18 Are Testing with Configuration On
    ######====================================================================

    ######---------------------------CONTEXT----------------------------------
    ######  Application Creation Scenario: is Added in OpenApplication.Feature
    ######--------------------------------------------------------------------

  Scenario Outline: User verify the required configuration is enabled in setup LogicalID <LogicalID>
    Given user is on CAS Login Page
    And user logged in CAS with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user starts creating application of logical id "<LogicalID>"
    When user fetch property_value from configuration table of "<Property_Key>"
    Then The property_value should be "<Property_Value>"
    @CreditApproval
    Examples:
      | LogicalID            | Property_Key                        | Property_Value |
      | CAS_247073_CRED_MA_1 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_MA_2 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_MA_3 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_DM_1 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_DM_2 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_DM_3 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_GM_1 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_GM_2 | cas.committee.wait.pendingdecisions | true           |
      | CAS_247073_CRED_GM_3 | cas.committee.wait.pendingdecisions | true           |

    @CreditApproval @OtherConfig
    Examples:
      | LogicalID            | Property_Key                        | Property_Value |
      | CAS_247073_CRED_MA_4 | cas.committee.wait.pendingdecisions | false          |
      | CAS_247073_CRED_DM_4 | cas.committee.wait.pendingdecisions | false          |
      | CAS_247073_CRED_GM_4 | cas.committee.wait.pendingdecisions | false          |


  Scenario Outline: User Initiates Committee of <Committee_type> with 5 members at <ApplicationStage> LogicalID <LogicalID>
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user opens an application of "<ProductType>" product type as "indiv" applicant at "<ApplicationStage>" for "" with "" from application grid
    And user reads data from the excel file "<CommitteeApprovalWB>" under sheet "<sheetName>" and row <rowNum>
    And user selects a committee to take decision
    And user initiate committee approval
    Then committee of "<Committee_type>" should get initiated successfully
    @CreditApproval @CommitteeInitiation
    Examples:
      | LogicalID            | ProductType | ApplicationStage | CommitteeApprovalWB          | sheetName          | rowNum | Committee_type    |
      | CAS_247073_CRED_MA_1 | HL          | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |
      | CAS_247073_CRED_MA_2 | PL          | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |
      | CAS_247073_CRED_MA_3 | MAL         | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |

      | CAS_247073_CRED_DM_1 | HL          | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |
      | CAS_247073_CRED_DM_2 | PL          | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |
      | CAS_247073_CRED_DM_3 | MAL         | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |

      | CAS_247073_CRED_GM_1 | HL          | CreditApproval   | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |
      | CAS_247073_CRED_GM_2 | PL          | CreditApproval   | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |
      | CAS_247073_CRED_GM_3 | MAL         | CreditApproval   | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |

    @CreditApproval @CommitteeInitiation @OtherConfig
    Examples:
      | LogicalID            | ProductType | ApplicationStage | CommitteeApprovalWB          | sheetName          | rowNum | Committee_type    |
      | CAS_247073_CRED_MA_4 | LAP         | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |
      | CAS_247073_CRED_DM_4 | LAP         | Credit Approval  | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |
      | CAS_247073_CRED_GM_4 | LAP         | CreditApproval   | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |


  Scenario Outline: User Initiates Committee of <Committee_type> with 5 members At <FinalStage>
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    And user opens an application of "<ProductType>" product type as "indiv" applicant at "<ApplicationStage>" for "" with "<Key>" from application grid
    And user reads data from the excel file "<CommitteeApprovalWB>" under sheet "<sheetName>" and row <rowNum>
    And user selects a committee to take decision
    And user initiate committee approval
    Then committee of "<Committee_type>" should get initiated successfully
    @AppUpdateApproval @CommitteeInitiation
    Examples:
      | LogicalID           | ProductType | FinalStage          | ApplicationStage | Key     | CommitteeApprovalWB          | sheetName          | rowNum | Committee_type    |
      | CAS_247073_AUA_MA_1 | HL          | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |
      | CAS_247073_AUA_MA_2 | PL          | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |
      | CAS_247073_AUA_MA_3 | MAL         | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |

      | CAS_247073_AUA_DM_1 | HL          | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |
      | CAS_247073_AUA_DM_2 | PL          | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |
      | CAS_247073_AUA_DM_3 | MAL         | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |

      | CAS_247073_AUA_GM_1 | HL          | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |
      | CAS_247073_AUA_GM_2 | PL          | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |
      | CAS_247073_AUA_GM_3 | MAL         | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |

    @AppUpdateApproval @CommitteeInitiation @OtherConfig
    Examples:
      | LogicalID           | ProductType | Final Stage         | ApplicationStage | Key     | CommitteeApprovalWB          | sheetName          | rowNum | Committee_type    |
      | CAS_247073_AUA_MA_4 | LAP         | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 0      | Minimum Approvals |
      | CAS_247073_AUA_DM_4 | LAP         | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 1      | Decision Maker    |
      | CAS_247073_AUA_GM_4 | LAP         | App Update Approval | Disbursal Author | approve | committee_approval_grid.xlsx | committee_approval | 2      | General Majority  |


  @CommitteeApproval
  Scenario Outline: <CommitteeType> committee waits for all member votes after <MemberNumber> member while finalize the verdict as <VerdictAfterPreviousVote> until all remaining members vote LogicalID <LogicalID>
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user logout from CAS
    Given user is on CAS Login Page
    And user logged in "CAS" with specific username and password present in "LoginDetailsCAS.xlsx" under "CommitteeUser" and <MemberNumber>
    And user open committee approval grid
    And search the initiated committee approval application
    And user opens the initiated committee approval application for current user
    And user selects committee decision as "<UserDecision>"
    And user reads data from the excel file "committee_approval_grid.xlsx" under sheet "committee_approval" and row 0
    And user selects reason for committee decision as "<Reason>"
    When user click on save in committee approval
    Then committee decision should be saved successfully
    And committee verdict should be "<VerdictAfterPreviousVote>" for "<CommitteeType>"
    And user clicks on MTNS button
#    And user logout from CAS
    ######====================================================================
    ###### MINIMUM APPROVAL COMMITTEE – NEW CONFIGURATION ENABLED
    ######====================================================================
    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType     | MemberNumber | UserDecision | Reason  | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_CRED_MA_1 | HL          | Minimum Approvals | 0            | Approve      | Approve | pending                  | Approved     |
      | CAS_247073_CRED_MA_1 | HL          | Minimum Approvals | 1            | Approve      | Approve | pending                  | Approved     |
      | CAS_247073_CRED_MA_1 | HL          | Minimum Approvals | 2            | Approve      | Approve | pending                  | Approved     |
      | CAS_247073_CRED_MA_1 | HL          | Minimum Approvals | 3            | Reject       | Other   | approved                 | Approved     |
      | CAS_247073_CRED_MA_1 | HL          | Minimum Approvals | 4            | Reject       | Other   | approved                 | Approved     |

    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType     | MemberNumber | UserDecision | Reason  | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_AUA_MA_1 | HL          | Minimum Approvals | 0            | Approve      | Approve | pending                  | Approved     |
      | CAS_247073_AUA_MA_1 | HL          | Minimum Approvals | 1            | Approve      | Approve | pending                  | Approved     |
      | CAS_247073_AUA_MA_1 | HL          | Minimum Approvals | 2            | Approve      | Approve | pending                  | Approved     |
      | CAS_247073_AUA_MA_1 | HL          | Minimum Approvals | 3            | Reject       | Other   | approved                 | Approved     |
      | CAS_247073_AUA_MA_1 | HL          | Minimum Approvals | 4            | Reject       | Other   | approved                 | Approved     |


    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType     | MemberNumber | UserDecision | Reason  | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_CRED_MA_3 | MAL         | Minimum Approvals | 0            | Reject       | Other   | pending                  | Rejected     |
      | CAS_247073_CRED_MA_3 | MAL         | Minimum Approvals | 1            | Reject       | Other   | pending                  | Rejected     |
      | CAS_247073_CRED_MA_3 | MAL         | Minimum Approvals | 2            | Reject       | Other   | pending                  | Rejected     |
      | CAS_247073_CRED_MA_3 | MAL         | Minimum Approvals | 3            | Approve      | Approve | rejected                 | Rejected     |
      | CAS_247073_CRED_MA_3 | MAL         | Minimum Approvals | 4            | Approve      | Approve | rejected                 | Rejected     |

    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType     | MemberNumber | UserDecision | Reason  | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_AUA_MA_3 | MAL         | Minimum Approvals | 0            | Reject       | Other   | pending                  | Rejected     |
      | CAS_247073_AUA_MA_3 | MAL         | Minimum Approvals | 1            | Reject       | Other   | pending                  | Rejected     |
      | CAS_247073_AUA_MA_3 | MAL         | Minimum Approvals | 2            | Reject       | Other   | pending                  | Rejected     |
      | CAS_247073_AUA_MA_3 | MAL         | Minimum Approvals | 3            | Approve      | Approve | rejected                 | Rejected     |
      | CAS_247073_AUA_MA_3 | MAL         | Minimum Approvals | 4            | Approve      | Approve | rejected                 | Rejected     |

    ######====================================================================
    ###### DECISION MAKER COMMITTEE – NEW PARTICIPATION RULE
    ######====================================================================
    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType  | MemberNumber | isDecisionMaker    | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_CRED_DM_1 | PL          | Decision Maker | 0            | Decision Maker     | Approve      | Ok           | pending                  | Approved     |
      | CAS_247073_CRED_DM_1 | PL          | Decision Maker | 1            | Decision Maker     | Approve      | Ok           | pending                  | Approved     |
      | CAS_247073_CRED_DM_1 | PL          | Decision Maker | 2            | Not Decision Maker | Reject       | Not Approved | approved                 | Approved     |
      | CAS_247073_CRED_DM_1 | PL          | Decision Maker | 3            | Not Decision Maker | Reject       | Not Approved | approved                 | Approved     |
      | CAS_247073_CRED_DM_1 | PL          | Decision Maker | 4            | Not Decision Maker | Reject       | Not Approved | approved                 | Approved     |

    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType  | MemberNumber | isDecisionMaker    | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_AUA_DM_1 | PL          | Decision Maker | 0            | Decision Maker     | Approve      | Ok           | pending                  | Approved     |
      | CAS_247073_AUA_DM_1 | PL          | Decision Maker | 1            | Decision Maker     | Approve      | Ok           | pending                  | Approved     |
      | CAS_247073_AUA_DM_1 | PL          | Decision Maker | 2            | Not Decision Maker | Reject       | Not Approved | approved                 | Approved     |
      | CAS_247073_AUA_DM_1 | PL          | Decision Maker | 3            | Not Decision Maker | Reject       | Not Approved | approved                 | Approved     |
      | CAS_247073_AUA_DM_1 | PL          | Decision Maker | 4            | Not Decision Maker | Reject       | Not Approved | approved                 | Approved     |

    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType  | MemberNumber | isDecisionMaker    | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_CRED_DM_2 | HL          | Decision Maker | 0            | Decision Maker     | Approve      | Ok           | pending                  | Rejected     |
      | CAS_247073_CRED_DM_2 | HL          | Decision Maker | 1            | Decision Maker     | Reject       | Not Approved | pending                  | Rejected     |
      | CAS_247073_CRED_DM_2 | HL          | Decision Maker | 2            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_CRED_DM_2 | HL          | Decision Maker | 3            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_CRED_DM_2 | HL          | Decision Maker | 4            | Not Decision Maker | Reject       | Not Approved | rejected                 | Rejected     |

    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType  | MemberNumber | isDecisionMaker    | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_AUA_DM_2 | HL          | Decision Maker | 0            | Decision Maker     | Approve      | Ok           | pending                  | Rejected     |
      | CAS_247073_AUA_DM_2 | HL          | Decision Maker | 1            | Decision Maker     | Reject       | Not Approved | pending                  | Rejected     |
      | CAS_247073_AUA_DM_2 | HL          | Decision Maker | 2            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_AUA_DM_2 | HL          | Decision Maker | 3            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_AUA_DM_2 | HL          | Decision Maker | 4            | Not Decision Maker | Reject       | Not Approved | rejected                 | Rejected     |

    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType  | MemberNumber | isDecisionMaker    | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_CRED_DM_3 | MAL         | Decision Maker | 0            | Decision Maker     | Reject       | Not Approved | pending                  | Rejected     |
      | CAS_247073_CRED_DM_3 | MAL         | Decision Maker | 1            | Decision Maker     | Approve      | Ok           | pending                  | Rejected     |
      | CAS_247073_CRED_DM_3 | MAL         | Decision Maker | 2            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_CRED_DM_3 | MAL         | Decision Maker | 3            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_CRED_DM_3 | MAL         | Decision Maker | 4            | Not Decision Maker | Reject       | Not Approved | rejected                 | Rejected     |

    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType  | MemberNumber | isDecisionMaker    | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_AUA_DM_3 | MAL         | Decision Maker | 0            | Decision Maker     | Reject       | Not Approved | pending                  | Rejected     |
      | CAS_247073_AUA_DM_3 | MAL         | Decision Maker | 1            | Decision Maker     | Approve      | Ok           | pending                  | Rejected     |
      | CAS_247073_AUA_DM_3 | MAL         | Decision Maker | 2            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_AUA_DM_3 | MAL         | Decision Maker | 3            | Not Decision Maker | Approve      | Ok           | rejected                 | Rejected     |
      | CAS_247073_AUA_DM_3 | MAL         | Decision Maker | 4            | Not Decision Maker | Reject       | Not Approved | rejected                 | Rejected     |

    ######====================================================================
    ###### MAJORITY APPROVAL COMMITTEE – PARTICIPATION RULE ENFORCEMENT
    ######====================================================================

    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType    | MemberNumber | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_CRED_GM_1 | HL          | General Majority | 0            | approve      | Ok           | pending                  | approved     |
      | CAS_247073_CRED_GM_1 | HL          | General Majority | 1            | approve      | Ok           | pending                  | approved     |
      | CAS_247073_CRED_GM_1 | HL          | General Majority | 2            | approve      | Ok           | pending                  | approved     |
      | CAS_247073_CRED_GM_1 | HL          | General Majority | 3            | reject       | Not Approved | approved                 | approved     |
      | CAS_247073_CRED_GM_1 | HL          | General Majority | 4            | reject       | Not Approved | approved                 | approved     |

    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType    | MemberNumber | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_AUA_GM_1 | HL          | General Majority | 0            | approve      | Ok           | pending                  | approved     |
      | CAS_247073_AUA_GM_1 | HL          | General Majority | 1            | approve      | Ok           | pending                  | approved     |
      | CAS_247073_AUA_GM_1 | HL          | General Majority | 2            | approve      | Ok           | pending                  | approved     |
      | CAS_247073_AUA_GM_1 | HL          | General Majority | 3            | reject       | Not Approved | approved                 | approved     |
      | CAS_247073_AUA_GM_1 | HL          | General Majority | 4            | reject       | Not Approved | approved                 | approved     |

    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType    | MemberNumber | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_CRED_GM_2 | PL          | General Majority | 0            | reject       | Not Approved | pending                  | rejected     |
      | CAS_247073_CRED_GM_2 | PL          | General Majority | 1            | reject       | Not Approved | pending                  | rejected     |
      | CAS_247073_CRED_GM_2 | PL          | General Majority | 2            | reject       | Not Approved | pending                  | rejected     |
      | CAS_247073_CRED_GM_2 | PL          | General Majority | 3            | approve      | Ok           | rejected                 | rejected     |
      | CAS_247073_CRED_GM_2 | PL          | General Majority | 4            | approve      | Ok           | rejected                 | rejected     |

    @CreditApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType    | MemberNumber | UserDecision | Reason       | VerdictAfterPreviousVote | finalVerdict |
      | CAS_247073_AUA_GM_2 | PL          | General Majority | 0            | reject       | Not Approved | pending                  | rejected     |
      | CAS_247073_AUA_GM_2 | PL          | General Majority | 1            | reject       | Not Approved | pending                  | rejected     |
      | CAS_247073_AUA_GM_2 | PL          | General Majority | 2            | reject       | Not Approved | pending                  | rejected     |
      | CAS_247073_AUA_GM_2 | PL          | General Majority | 3            | approve      | Ok           | rejected                 | rejected     |
      | CAS_247073_AUA_GM_2 | PL          | General Majority | 4            | approve      | Ok           | rejected                 | rejected     |




    ######====================================================================
    ###### CONFIGURATION OFF – BACKWARD COMPATIBILITY
    ######====================================================================
  @OtherConfig
  Scenario Outline: <CommitteeType> committee finalizes the verdict as soon as Minimum Approvals are provided LogicalID <LogicalID>
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user logout from CAS
    And user logged in "CAS" with specific username and password present in "LoginDetailsCAS.xlsx" under "CommitteeUser" and <MemberNumber>
    And user open committee approval grid
    And search the initiated committee approval application
    And user opens the initiated committee approval application for current user
    And user selects committee decision as "<UserDecision>"
    And user selects reason for committee decision as "<Reason>"
    And user click on save in committee approval
    Then committee decision should be saved successfully
    And committee verdict should be "<VerdictAfterPreviousVote>" for "<CommitteeType>"
    And user clicks on MTNS button
    @CreditApproval @CommitteeApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType     | MemberNumber | UserDecision | Reason | VerdictAfterPreviousVote |
      | CAS_247073_CRED_MA_4 | LAP         | Minimum Approvals | 0            | approve      | Ok     | pending                  |
      | CAS_247073_CRED_MA_4 | LAP         | Minimum Approvals | 1            | approve      | Ok     | pending                  |
      | CAS_247073_CRED_MA_4 | LAP         | Minimum Approvals | 2            | approve      | Ok     | pending                  |

    @AppUpdateApproval @CommitteeApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType     | MemberNumber | UserDecision | Reason | VerdictAfterPreviousVote |
      | CAS_247073_AUA_MA_4 | LAP         | Minimum Approvals | 0            | approve      | Ok     | pending                  |
      | CAS_247073_AUA_MA_4 | LAP         | Minimum Approvals | 1            | approve      | Ok     | pending                  |
      | CAS_247073_AUA_MA_4 | LAP         | Minimum Approvals | 2            | approve      | Ok     | pending                  |

    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType  | MemberNumber | isDecisionMaker | UserDecision | Reason | VerdictAfterPreviousVote |
      | CAS_247073_CRED_DM_4 | PL          | Decision Maker | 0            | Decision Maker  | approve      | Ok     | pending                  |
    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType  | MemberNumber | isDecisionMaker | UserDecision | Reason | VerdictAfterPreviousVote |
      | CAS_247073_AUA_DM_4 | PL          | Decision Maker | 0            | Decision Maker  | approve      | Ok     | pending                  |

    @CreditApproval
    Examples:
      | LogicalID            | ProductType | CommitteeType    | MemberNumber | UserDecision | Reason | VerdictAfterPreviousVote |
      | CAS_247073_CRED_GM_4 | HL          | General Majority | 0            | approve      | Ok     | pending                  |
      | CAS_247073_CRED_GM_4 | HL          | General Majority | 1            | approve      | Ok     | pending                  |
      | CAS_247073_CRED_GM_4 | HL          | General Majority | 2            | approve      | Ok     | approved                 |

    @AppUpdateApproval
    Examples:
      | LogicalID           | ProductType | CommitteeType    | MemberNumber | UserDecision | Reason | VerdictAfterPreviousVote |
      | CAS_247073_AUA_GM_4 | HL          | General Majority | 0            | approve      | Ok     | pending                  |
      | CAS_247073_AUA_GM_4 | HL          | General Majority | 1            | approve      | Ok     | pending                  |
      | CAS_247073_AUA_GM_4 | HL          | General Majority | 2            | approve      | Ok     | approved                 |

  @OtherConfig
  Scenario Outline: In <CommitteeType> committee after decision is finalized other members can not see Committee Task In Application Manager
    Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>" with valid username and password present in "LoginDetailsCAS.xlsx" under "LoginData" and 0
    When user logout from CAS
    And user logged in "CAS" with specific username and password present in "LoginDetailsCAS.xlsx" under "CommitteeUser" and <MemberNumber>
    And user open application manager
    And user search application using application number
    Then user should not be able to see any committee tasks for "<CommitteeType>"
    @CreditApproval @CommitteeApproval @ApplicationManager
    Examples:
      | LogicalID            | ProductType | CommitteeType     | MemberNumber |
      | CAS_247073_CRED_MA_4 | LAP         | Minimum Approvals | 4            |
      | CAS_247073_CRED_DM_4 | LAP         | Decision Maker    | 2            |
      | CAS_247073_CRED_GM_4 | LAP         | General Majority  | 4            |

    @AppUpdateApproval @CommitteeApproval @ApplicationManager
    Examples:
      | LogicalID           | ProductType | CommitteeType     | MemberNumber |
      | CAS_247073_AUA_MA_4 | LAP         | Minimum Approvals | 4            |
      | CAS_247073_AUA_DM_4 | LAP         | Decision Maker    | 2            |
      | CAS_247073_AUA_GM_4 | LAP         | General Majority  | 4            |
