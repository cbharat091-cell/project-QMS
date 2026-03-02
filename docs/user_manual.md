# MedQMS User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [User Authentication](#user-authentication)
3. [Document Review](#document-review)
4. [AI Output Approval](#ai-output-approval)
5. [Change Control](#change-control)
6. [Performance Monitoring](#performance-monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements
- Modern web browser (Chrome, Firefox, Edge, Safari)
- OpenAI API key (for AI-powered features)

### Accessing the System
1. Open `index.html` in a web browser
2. The application loads with the Document Review tab active

---

## User Authentication

### Login
1. Click the **Login** button in the top-right corner
2. Enter your username
3. Enter your password
4. Select your role from the dropdown:
   - **Administrator**: Full access to all features
   - **QA Reviewer**: Can review and approve AI outputs
   - **RA Reviewer**: Can review and approve AI outputs
   - **Viewer**: Read-only access

> **Note**: This is a demo system - any credentials work for testing.

### Logout
1. Click the **Logout** button in the top-right corner
2. Your session will be ended

---

## Document Review

### Uploading a Document
1. Click on the upload area or drag-and-drop a file
2. Supported formats: `.txt`, `.md`
3. The document content will be displayed in the preview

### Running a Review

#### Option 1: Keyword-Based Review
1. Uncheck "Use AI-Powered Review"
2. Click **Review Document**
3. View results in the compliance check section

#### Option 2: AI-Powered Review
1. Enter your OpenAI API key in the API Key field
2. Click **Save Key** (the key is stored locally)
3. Ensure "Use AI-Powered Review" is checked
4. Click **Review Document**
5. Wait for the AI analysis to complete

### Understanding Results

#### Score Overview
- **Overall Score**: 0-100% compliance rating
- **Status**: Pass (≥60%) or Needs Improvement (<60%)
- **Passed/Failed**: Number of checks that passed

#### Compliance Check Results
The system checks against 22 compliance categories:
1. Document control metadata
2. Purpose and scope
3. Roles and responsibilities
4. Process flow and steps
5. Risk management
6. CAPA and nonconformance
7. Records and retention
8. ISO 13485 Compliance
9. Design and Development Controls
10. Production and Process Controls
11. Medical Device Reporting (MDR)
12. Labeling and Traceability
13. Risk Management (ISO 14971)
14. Equipment Qualification
15. Environmental Controls
16. AI Governance and Compliance
17. WHO Prequalification (WHO PQ)
18. CE Marking Compliance
19. IVDR Compliance
20. Cybersecurity Risk Assessment
21. Change Control Management
22. Performance Monitoring

#### Gaps and Recommendations
- **Identified Gaps**: Areas that need improvement
- **Recommendations**: Specific suggestions for addressing gaps

---

## AI Output Approval

All AI-generated outputs require review and approval by authorized personnel.

### Review Workflow
1. After running an AI review, scroll to the **AI Output Review Workflow** section
2. Review the compliance assessment
3. Choose an action:
   - **Approve**: Accept the AI output
   - **Reject**: Reject the output
   - **Request Revision**: Send back for changes

### Electronic Signature
- Enter your full name in the signature field
- This serves as your electronic signature
- All approval decisions are timestamped

### Pending Approvals Tab
1. Click the **AI Output Approval** tab
2. View all pending approvals
3. See status of previous reviews

---

## Change Control

### Submitting a Change Request
1. Click the **Change Control** tab
2. Fill in the form:
   - **Change Type**: Select the type (Algorithm, Model, Data, Process, Security)
   - **Priority**: Select priority level
   - **Change Description**: Describe what needs to change
   - **Impact Assessment**: Explain the impact on the system
3. Click **Submit Change Request**

### Viewing Change Requests
- All submitted requests appear in the history
- Status shows: Pending, Approved, Rejected

---

## Performance Monitoring

### Dashboard Metrics
1. Click the **Performance** tab
2. View key metrics:
   - **Total Reviews**: Number of documents reviewed
   - **Average Score**: Mean compliance score
   - **Approval Rate**: Percentage of approved reviews
   - **System Uptime**: System availability

### Score Trend
- Visual chart shows compliance score over time
- Helps identify trends in document quality

---

## Troubleshooting

### Common Issues

#### "Please enter your OpenAI API key"
- Ensure you've entered and saved your API key
- The key starts with `sk-`

#### "You do not have permission to approve outputs"
- Login with a role that has approval privileges (Admin, QA Reviewer, RA Reviewer)

#### AI Review Fails
- Check your API key is valid
- Check you have credits in your OpenAI account
- Try again later if rate limited

#### Document Won't Upload
- Ensure file format is `.txt` or `.md`
- Check file size is reasonable

### Getting Help
For additional support, contact your system administrator.

---

## Appendix: Compliance Standards

### Supported Standards
- **ISO 13485:2016**: Medical devices QMS
- **WHO PQ**: WHO Prequalification
- **CE Marking**: European Conformity
- **IVDR**: In Vitro Diagnostic Regulation
- **FDA 21 CFR Part 820**: Quality System Regulation
- **ISO 14971**: Risk Management for Medical Devices

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**MedQMS - AI-Powered Medical Device QMS Reviewer**

