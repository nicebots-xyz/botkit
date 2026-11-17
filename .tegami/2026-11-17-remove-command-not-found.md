---
packages:
  botkit: patch
---

### Remove the command not found handler

The `nice_errors` extension no longer handles `CommandNotFound` for prefix commands. The closest command suggestion and its "Run x instead" button are removed, along with the `error_command_not_found` and `run_x_instead` translations.
