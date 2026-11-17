---
packages:
  botkit: patch
---

### Remove the "Run x instead" button from command not found errors

The `nice_errors` extension still suggests the closest command when a prefix command is not found, but no longer attaches a button that runs it. The unused `run_x_instead` translation is removed.
