<!--
SPDX-License-Identifier: MIT
Copyright: 2024-2026 NiceBots.xyz
-->

# Defining Help Pages in Botkit

This guide will walk you through the process of defining help pages for your Botkit
extensions. Help pages provide users with information about your bot's commands,
features, and usage examples.

## Prerequisites

Before you begin, ensure you have:

1. A basic understanding of YAML syntax
2. Familiarity with the Botkit extension system
3. An existing Botkit extension that you want to document

## Understanding the Help System

The Botkit help system organizes documentation into categories and pages. Each category
contains multiple pages, and each page documents a specific command or feature.

### Key Components

The help system consists of several key components:

1. **Categories**: Groups of related help pages (e.g., "Moderation", "Fun", "Utility")
2. **Pages**: Individual documentation pages for specific commands or features
3. **Translations**: Multi-language support for help content

## Help Page Structure

Help pages are defined using YAML files. Each YAML file represents a category and
contains definitions for all pages within that category.

### Class Structure

The help system uses the following classes to represent help content:

- `HelpTranslation`: The root class containing all categories
- `HelpCategoryTranslation`: Represents a category of help pages
- `HelpPageTranslation`: Represents an individual help page

## Creating Help Pages

### Step 1: Create a YAML File

Create a YAML file for your help category in the `src/extensions/help/pages/` directory.
For example, if you're documenting moderation commands, you might create
`moderation.yml`:

```bash
touch src/extensions/help/pages/moderation.yml
```

### Step 2: Define the Category

Open the YAML file and define the category structure:

```yaml
name:
  en-US: Moderation
  es-ES: Moderación
description:
  en-US: Commands for server moderation
  es-ES: Comandos para moderación del servidor
order: 1 # Lower numbers appear first in the category list
pages:
  # Pages will be defined here
```

The `name` and `description` fields support multiple languages, and the `order` field
determines the position of this category in the list.

### Step 3: Define Pages

Within the `pages` section, define each help page:

```yaml
pages:
  ban:
    title:
      en-US: Ban Command
      es-ES: Comando de Prohibición
    description:
      en-US: Bans a user from the server
      es-ES: Prohíbe a un usuario del servidor
    category:
      en-US: Moderation
      es-ES: Moderación
    quick_tips:
      - en-US: You can specify a reason for the ban
        es-ES: Puedes especificar una razón para la prohibición
      - en-US: Banned users can be unbanned later
        es-ES: Los usuarios prohibidos pueden ser readmitidos más tarde
    examples:
      - en-US: "/ban @user Spamming"
        es-ES: "/ban @usuario Spam"
      - en-US: "/ban @user"
        es-ES: "/ban @usuario"
    related_commands:
      - ban
```

Each page includes:

- `title`: The name of the command or feature
- `description`: A brief description of what it does
- `category`: The category this page belongs to (should match the category name)
- `quick_tips` (optional): A list of helpful tips for using the command
- `examples` (optional): Example usages of the command
- `related_commands` (optional): List of commands that will be linked to this page using
  discord slash command mentions

<!-- prettier-ignore -->
> [!NOTE]
> All text fields support multiple languages using language codes as keys.

### Step 4: Make Your YAML File Available

The help system automatically loads all `.yml` files from the
`src/extensions/help/pages` directory. Make sure your file is properly formatted and
placed in this directory.

<!-- prettier-ignore -->
> [!NOTE]
> All help files should be placed in the `src/extensions/help/pages` directory, not inside individual extension directories.

## Example: Complete Help Category

Here's a complete example of a help category for moderation commands:

```yaml
name:
  en-US: Moderation
  es-ES: Moderación
description:
  en-US: Commands for server moderation
  es-ES: Comandos para moderación del servidor
order: 1
pages:
  ban:
    title:
      en-US: Ban Command
      es-ES: Comando de Prohibición
    description:
      en-US: Bans a user from the server
      es-ES: Prohíbe a un usuario del servidor
    category:
      en-US: Moderation
      es-ES: Moderación
    quick_tips:
      - en-US: You can specify a reason for the ban
        es-ES: Puedes especificar una razón para la prohibición
      - en-US: Banned users can be unbanned later
        es-ES: Los usuarios prohibidos pueden ser readmitidos más tarde
    examples:
      - en-US: "/ban @user Spamming"
        es-ES: "/ban @usuario Spam"
      - en-US: "/ban @user"
        es-ES: "/ban @usuario"
    related_commands:
      - kick
      - unban

  kick:
    title:
      en-US: Kick Command
      es-ES: Comando de Expulsión
    description:
      en-US: Kicks a user from the server
      es-ES: Expulsa a un usuario del servidor
    category:
      en-US: Moderation
      es-ES: Moderación
    quick_tips:
      - en-US: Kicked users can rejoin with a new invite
        es-ES: Los usuarios expulsados pueden volver a unirse con una nueva invitación
    examples:
      - en-US: "/kick @user Disruptive behavior"
        es-ES: "/kick @usuario Comportamiento disruptivo"
    related_commands:
      - ban
```

## How the Help System Works

When a user requests help using the `/help` command, the help system:

1. Loads all help categories and pages from YAML files
2. Organizes them by category
3. Displays a paginated view with categories in a dropdown menu
4. Shows pages within the selected category

The system automatically handles pagination, localization, and UI elements like "Tips &
Tricks" and "Usage Examples" sections.

## Advanced: Understanding How Help Pages Are Loaded

The help system automatically loads all help pages from the `src/extensions/help/pages`
directory when the bot starts. This is handled by the following code in
`src/extensions/help/pages/__init__.py`:

```python
# iterate over .y[a]ml files in the same directory as this file
categories: list[HelpCategoryTranslation] = []

for file in chain(Path(__file__).parent.glob("*.yaml"), Path(__file__).parent.glob("*.yml")):
    with open(file, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    categories.append(HelpCategoryTranslation(**data))

categories.sort(key=lambda item: item.order)

help_translation = HelpTranslation(categories=categories)
```

This code:

1. Finds all `.yml` and `.yaml` files in the `src/extensions/help/pages` directory
2. Loads each file as a YAML document
3. Creates a `HelpCategoryTranslation` object for each file
4. Sorts the categories by their `order` value
5. Creates a `HelpTranslation` object containing all categories

<!-- prettier-ignore -->
> [!IMPORTANT]
> Remember that all help pages must be placed in the `src/extensions/help/pages` directory, not within individual extension directories.

## Conclusion

By following this guide, you've learned how to create help pages for your Botkit
extensions. Well-documented commands improve user experience and make your bot more
accessible to new users.

<!-- prettier-ignore -->
> [!TIP]
> Keep your help pages concise, clear, and up-to-date with your bot's functionality.

<!-- prettier-ignore -->
> [!IMPORTANT]
> Always provide examples for complex commands to help users understand how to use them correctly.
