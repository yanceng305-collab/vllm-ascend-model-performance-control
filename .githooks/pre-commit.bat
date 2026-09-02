@echo off
REM Pre-commit hook for Machine-Verified Formal Result Gate
REM Per Decision D-023
REM
REM Validates Formal Results before commit to prevent transcription errors.
REM Blocks commit if validation fails.

REM Check if any Result files are being committed
git diff --cached --name-only --diff-filter=ACM > %TEMP%\git-staged-files.txt
findstr /R "RESULT-.*\.md$" %TEMP%\git-staged-files.txt > %TEMP%\result-files.txt 2>nul
findstr /V /C:"CORRECTION" /C:"USER-MEASURED" %TEMP%\result-files.txt > %TEMP%\result-files-filtered.txt 2>nul

if not exist %TEMP%\result-files-filtered.txt (
    REM No Result files being committed, allow commit
    exit /b 0
)

for /f %%i in (%TEMP%\result-files-filtered.txt) do set RESULT_FILE=%%i
if "%RESULT_FILE%"=="" (
    REM No Result files being committed, allow commit
    exit /b 0
)

echo =====================================================
echo Machine-Verified Formal Result Gate (D-023)
echo Validating Formal Results before commit...
echo =====================================================

REM Check if validated Evidence JSON exists
if not exist validated-evidence.json (
    echo.
    echo VALIDATION FAILED
    echo.
    echo FORMAL_RESULT_VALIDATION_FAILED:
    echo   validated-evidence.json not found
    echo.
    echo Before committing Results, you must:
    echo   1. Run: python scripts/validate_evidence.py ^<evidence-dir^> ^> validated-evidence.json
    echo   2. Ensure validation passes
    echo   3. Then commit Results
    echo.
    exit /b 1
)

REM Detect model name from Result files (default to GLM-5.2-W8A8)
set MODEL_NAME=GLM-5.2-W8A8

set VALIDATION_FAILED=0

REM Validate each Result file
for /f "delims=" %%f in (%TEMP%\result-files-filtered.txt) do (
    echo.
    echo Validating: %%f
    
    python scripts/validate_result.py "%%f" validated-evidence.json "%MODEL_NAME%"
    if errorlevel 1 (
        echo   FAIL: Validation failed
        set VALIDATION_FAILED=1
    ) else (
        echo   PASS: Validation successful
    )
)

echo.
echo =====================================================

if %VALIDATION_FAILED%==1 (
    echo COMMIT BLOCKED: One or more Results failed validation
    echo.
    echo FORMAL_RESULT_VALIDATION_FAILED
    echo.
    echo Fix validation errors before committing.
    echo See error messages above for details.
    echo.
    exit /b 1
) else (
    echo All Results validated successfully
    echo Proceeding with commit...
    echo.
    exit /b 0
)
