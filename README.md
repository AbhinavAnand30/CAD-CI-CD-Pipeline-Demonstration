# CI/CD Build Quality Analyzer

A Python-based Build Quality Analyzer integrated with a complete **CI/CD pipeline using GitHub Actions and AWS Lambda**.

The project automatically validates Python code through linting, automated testing, and code coverage before deploying the validated application to AWS Lambda.

---

## Project Overview

This project demonstrates the implementation of a complete Continuous Integration and Continuous Deployment pipeline.

The application analyzes CI/CD build information and provides important metrics such as:

- Build success rate
- Failed and successful builds
- Average build duration
- Overall test pass rate
- Deployment readiness
- Individual build test pass rate

The CI/CD pipeline automatically performs code quality checks and tests whenever changes are pushed to GitHub. If all checks pass, the application is automatically deployed to AWS Lambda.

---

## Architecture

```text
CI/CD DEPLOYMENT PIPELINE
=========================

Developer
    |
    | git push
    v
GitHub Repository
    |
    v
GitHub Actions
    |
    +-------------------+
    |                   |
    v                   v
Ruff Lint        Pytest + Coverage
    |                   |
    +---------+---------+
              |
         Tests Pass
              |
              v
        GitHub OIDC
              |
              v
           AWS IAM
              |
              v
         AWS Lambda
              |
              v
       CADDemoFunction


BUILD MONITORING
================

Build Status Request
        |
        v
   API Gateway
        |
        v
CICDBuildStatusHandler
        |
        +-------------------+
        |                   |
        v                   v
    DynamoDB           PagerDuty
        |              (if FAILED)
        |                   |
        v                   v
 CloudWatch Logs       Incident
