# TestAutomationFramework-Pytest
Automation testing framework using pytest 
This will:
   - Create a virtual environment if not present
   - Install all dependencies
   - Start the GUI application

3. **Using the Application:**
   - Click the 📂 button to load your CSV/Excel test data files.
   - Select the desired test case for each file.
   - Click ▶️ to run the selected tests.
   - View the summary and detailed HTML reports after execution.

## Project Structure

- `main.py` — Main PyQt5 GUI application
- `tests/` — Directory for all test classes (e.g., `test_sample.py`)
- `reports/` — Generated HTML reports
- `requirements.txt` — Python dependencies
- `launch_app.bat` — Windows batch script for setup and launch

## Writing Tests

- Place your test classes in the `tests/` directory.
- Test classes should start with `Test` and contain test methods.
- Use the `USER_INPUT_FILE` environment variable to access the loaded file in your test.

## License

MIT License

---

*Happy Testing!*
