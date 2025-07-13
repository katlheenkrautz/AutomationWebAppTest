## Project: Urban Routes – Automated Testing

This project is part of Sprint 8 of the TripleTen bootcamp. It focuses on automating tests for the **Urban Routes** web application, simulating the complete flow of ordering a taxi from the user's perspective.

## 📌 Project Description

The main goal is to validate the app's functionality through automated tests. The tests simulate various user actions such as selecting the pickup location, fare, payment method, and additional items, ensuring that the entire process works correctly up to driver assignment.

## 🛠️ Technologies Used

- **Python**
- **Selenium WebDriver**
- **Pytest**
- **Git & GitHub**

## ✅ Features Covered by the Tests

The automated tests cover the entire taxi ordering process, including:

- Setting the pickup address
- Selecting the "Comfort" fare
- Entering a phone number
- Adding a credit card (simulating focus loss on the CVV field)
- Sending a message to the driver
- Requesting a blanket, tissues, and 2 ice creams
- Verifying the driver search modal and driver assignment

## 🚀 How to Run the Tests

1. Clone the repository to your computer:

   ```bash
   git clone git@github.com:your-username/qa-project-Urban-Routes-es.git

2. Open the project in PyCharm or your preferred editor.

3. Replace the base URL in the data.py file with the Urban Routes server URL you received.

4. Run the tests using:

pytest

📄 Project Structure

qa-project-Urban-Routes-es/
- data.py                 # Contains server configuration and base URL
- main.py                 # Main file with test definitions
- README.md               # This file
