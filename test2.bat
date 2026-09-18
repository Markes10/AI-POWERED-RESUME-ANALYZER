@echo off
where python >nul 2>&1
if errorlevel 1 (
  echo missing
) else (
  echo found
)
