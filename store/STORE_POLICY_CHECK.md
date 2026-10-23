# Microsoft Store policy self-check (MEDHĀ)
| Policy area | MEDHĀ | Status |
|---|---|---|
| 10.2 Security — app must not download/execute code without user action | compiles/runs only the user's own file on Ctrl+F5; extensions = themes/snippets/grammars only (no code) | OK — say this in "Notes for certification" |
| 10.1 Distinct value / accurate description | listing claims only features in FINAL_REPORT.md table | OK |
| 10.5 Personal information / privacy policy | none collected; policy URL required | host store/privacy-policy.md first |
| Bundled third-party software | GCC, MinGW-w64, JDK, Python, Qt — licenses in THIRD_PARTY_LICENSES.md | OK |
| runFullTrust restricted capability | needed for a Win32 desktop app; explain in submission notes | OK |
Notes for certification (paste): "MEDHĀ is an educational IDE. It compiles and runs only source files the user opens, after the user presses Run. Compilers are bundled for offline use."
