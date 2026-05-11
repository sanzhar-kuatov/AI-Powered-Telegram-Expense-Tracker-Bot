# AI-Powered Telegram Expense Tracker Bot

## Notice

The bot is currently inactive.

To test how it works, please contact me directly and request access.  
I keep the bot inactive by default because it uses paid API credits, and I do not want to waste them when the bot is not being tested.

---

## Introduction

AI-Powered Telegram Expense Tracker Bot is a Telegram bot that helps users record, categorize, and track their personal expenses.

Users can send expense messages in natural language, and the bot will automatically understand the expense, classify it into the correct category, and store it in a database.

The bot can also generate Excel reports for a selected period, allowing users to see how much money they spent in different categories.

The expense classification is powered by Claude AI, so users do not need to manually choose categories for every expense.

---

## Expense Categories

The bot classifies expenses into the following categories:

- Food
- Utilities
- Home
- Transport
- Health
- Entertainment
- Clothes
- Education
- Other

---

## Built-in Commands

The bot has two main commands:

### `/start`

Creates a new user record in the database.

### `/help`

Shows a short explanation of the bot’s available features and how to use them.

---

## Main Features

### 1. Recording Expenses

Users can send a simple message describing their expense.

Example:

```text
I got pizza for 25 RM
```

The bot will automatically:

detect the expense amount
understand the expense description
classify it into the correct category
save the record in the database

For example, the message above may be classified as:

```text
Category: Food
Amount: 25 RM
Description: Pizza
```

---

### 2. Generating Excel Reports

Users can request an expense report for a specific period.

Example:
```text
Generate me a report for 19.02.2025-11.05.2026
```

The bot will generate an Excel file showing how much was spent in each category during that period.

The report helps users understand their spending habits and track expenses more easily.

---

### 3. Editing Expense Records

Users can edit an expense record if:
- the wrong amount was entered
- the AI classified the expense into the wrong category
- the user wants to correct or update the description

This makes the bot more flexible and useful, even when mistakes happen.

---

Technologies Used
- Telegram Bot API
- Claude AI
- Database for storing user expense records
- Excel report generation

## Example Use Case

A user sends:
```text
I paid 12 RM for Grab
```

The bot can classify it as:

```text
Category: Transport
Amount: 12 RM
Description: Grab
```

Later, the user can request a report and receive an Excel file with total expenses grouped by category.

## Project Purpose

The purpose of this project is to make personal expense tracking easier and faster.

Instead of manually entering expenses into a spreadsheet, users can simply send messages to a Telegram bot. The AI handles classification, and the bot organizes the data automatically.
