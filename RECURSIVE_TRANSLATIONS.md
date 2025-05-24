# Recursive Translations Folder Support

This document describes the new recursive translations folder support feature implemented for issue #67.

## Overview

Botkit now supports loading translations from a folder structure in addition to the traditional single `translations.yml` file. This allows for better organization of translations, especially for extensions with many commands and strings.

## Backward Compatibility

The existing `translations.yml` file format is still fully supported. Extensions can continue to use the single file approach without any changes.

## New Folder Structure

Extensions can now use a `translations/` folder instead of `translations.yml`. The folder structure is recursively processed, and subfolder names become keys in the translation structure.

### Example Structure

```
src/extensions/my_extension/
├── __init__.py
└── translations/
    ├── commands/
    │   ├── hello.yaml
    │   └── goodbye.yaml
    └── strings/
        └── messages.yaml
```

### File Contents

**commands/hello.yaml:**
```yaml
name:
  en-US: hello
  fr: bonjour
description:
  en-US: Say hello
  fr: Dire bonjour
strings:
  response:
    en-US: Hello, {user}!
    fr: Bonjour, {user}!
```

**commands/goodbye.yaml:**
```yaml
name:
  en-US: goodbye
  fr: au revoir
description:
  en-US: Say goodbye
  fr: Dire au revoir
strings:
  response:
    en-US: Goodbye, {user}!
    fr: Au revoir, {user}!
```

**strings/messages.yaml:**
```yaml
welcome:
  en-US: Welcome to the bot!
  fr: Bienvenue dans le bot!
error:
  en-US: An error occurred
  fr: Une erreur s'est produite
```

## How It Works

1. **Priority**: If both `translations.yml` and `translations/` exist, the file takes precedence for backward compatibility.

2. **Recursive Processing**: The system recursively processes all `.yml` and `.yaml` files in the translations folder.

3. **Key Generation**: 
   - Files in the `commands/` subfolder become command definitions
   - Files in other subfolders become strings with dot-notation keys (e.g., `strings.messages.welcome`)

4. **Structure Preservation**: The folder structure is preserved in the translation keys, allowing for organized access to translations.

## Loading Logic

The extension loading system in `src/start.py` now follows this logic:

1. Check if `translations.yml` exists → load it using `load_translation()`
2. If not, check if `translations/` folder exists → load it using `load_translation_folder()`
3. If neither exists → log a warning

## Implementation Details

- **New Functions**: 
  - `load_translation_folder()` in `src/i18n/utils.py`
  - `_load_recursive_translations()` helper function
- **Modified Files**:
  - `src/i18n/utils.py` - Added recursive loading functions
  - `src/i18n/__init__.py` - Exported new function
  - `src/start.py` - Updated extension loading logic

## Benefits

1. **Better Organization**: Large extensions can organize translations by command or category
2. **Easier Maintenance**: Smaller files are easier to edit and maintain
3. **Team Collaboration**: Multiple translators can work on different files simultaneously
4. **Backward Compatibility**: Existing extensions continue to work without changes
5. **Flexible Structure**: Extensions can organize translations however makes sense for their use case

## Migration

Existing extensions do not need to migrate. However, if you want to use the new folder structure:

1. Create a `translations/` folder in your extension
2. Create subfolders as needed (e.g., `commands/`, `strings/`)
3. Move command definitions to individual files in `commands/`
4. Move other strings to organized files in appropriate subfolders
5. Remove the old `translations.yml` file

The new system will automatically detect and load the folder structure.