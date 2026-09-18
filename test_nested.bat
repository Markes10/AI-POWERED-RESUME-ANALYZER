@echo off
where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo missing
    exit /b 1
  ) else (
    set PY_CMD=py
  )
) else (
  set PY_CMD=python
)
echo done
