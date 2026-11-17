---
packages:
  botkit: patch
---

### Translation stubs for context menu commands

`pdm run i18n-stubs` no longer fails on commands whose names contain spaces or punctuation, such as the context menu command `Extract text (OCR)`, whose strings are typed by `ExtractTextOCRCommandStrings`.
