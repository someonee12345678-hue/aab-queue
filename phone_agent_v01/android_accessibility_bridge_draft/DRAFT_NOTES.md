# AAB-001 accessibility bridge prototype notes

This is a separate, unbuilt copy of the AAB-001 v0.1 Android source with an inactive-by-default Accessibility Service draft added. The original source archive was preserved.

## Included

- A user-triggered capture using Android's Accessibility button while ChatGPT is foregrounded.
- Text preview/edit screen. Captured text stays in process memory and can be cleared.
- A Termux staging attempt only when Termux exposes exactly one visible, enabled, editable accessibility node.
- No automatic Enter action, no shell `RUN_COMMAND` permission, no network permission, no background capture, no GitHub connection, and no worker activation.

## Not established

- Whether the ChatGPT app exposes complete assistant replies in its accessibility tree.
- Whether the installed Termux terminal exposes an editable node suitable for `ACTION_SET_TEXT`.
- Whether this project compiles or works on the owner's phone. It has not been built or tested.

If staging cannot identify the single expected input node, the service clears the pending text and reports that nothing was staged. The Accessibility Service remains off until the owner enables it in Android Settings; it should not be enabled as part of this draft.
