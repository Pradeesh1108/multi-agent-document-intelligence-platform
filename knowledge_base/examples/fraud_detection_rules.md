# Fraud Detection Rules

## Overview
This document defines fraud detection rules and risk indicators for document processing.

## High-Risk Indicators

### Financial Fraud Signals
- Transaction amount exceeding $100,000 from new accounts (< 30 days old)
- Multiple large transactions within a short period (> 3 transactions over $10,000 in 24 hours)
- Transactions originating from high-risk countries
- Mismatched billing and shipping addresses
- Sudden change in transaction patterns for established accounts
- Round-number transactions (e.g., exactly $50,000) are suspicious for invoice fraud

### Document Fraud Signals
- Invoice with no matching purchase order
- Duplicate invoice numbers from different vendors
- Vendor not found in approved vendor list
- Invoice amount significantly deviating from historical average (> 200%)
- Rush payment requests bypassing normal approval workflow
- Negative amounts or credits without corresponding original transaction

### Identity Fraud Signals
- Email domains that closely resemble known company domains (typosquatting)
- New vendor setup with only PO Box address
- Changed bank account details on existing vendor accounts
- Documents with inconsistent dates or formatting
- Multiple accounts linked to the same contact information

## Risk Scoring Guidelines

### Score Range: 0.0 to 1.0
- 0.0 - 0.2: Low Risk — Standard processing, no additional review needed
- 0.2 - 0.5: Medium Risk — Flag for secondary review, process with monitoring
- 0.5 - 0.7: High Risk — Requires manual approval before processing
- 0.7 - 1.0: Critical Risk — Block processing, escalate to fraud team immediately

### Score Calculation Factors
- Base score starts at 0.1 (baseline risk)
- Each high-risk indicator adds 0.1 - 0.3 based on severity
- Multiple indicators compound (multiplicative, not additive)
- Known trusted entities reduce score by 0.1
- Historical clean record reduces score by 0.05

## High-Risk Countries
Countries with elevated fraud risk for transaction monitoring:
- Nigeria, Ghana, Romania, India (for card-not-present transactions)
- Countries under sanctions: North Korea, Iran, Syria, Cuba, Crimea region

## Response Procedures

### Low Risk (Score < 0.2)
- Process normally
- Log for audit trail

### Medium Risk (Score 0.2 - 0.5)
- Process with enhanced monitoring
- Send notification to compliance team
- Add to weekly review queue

### High Risk (Score 0.5 - 0.7)
- Hold processing pending review
- Notify fraud team within 4 hours
- Request additional verification from submitter

### Critical Risk (Score > 0.7)
- Block all processing immediately
- Alert fraud team and management
- Preserve all evidence
- File Suspicious Activity Report (SAR) if applicable
