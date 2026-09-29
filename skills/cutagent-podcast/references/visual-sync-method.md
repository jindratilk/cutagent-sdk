# Visual sync method

Use visual synchronization only when camera scratch audio is absent or unreliable.

Find the same unambiguous event in every source: a slate close, hand clap, flash, screen change, or shared clock. Match the complete event sequence when repeated claps or flashes exist; one coincidental peak is weak evidence. Record the exact source frame for each camera and microphone relationship.

If all cameras are already start-aligned, preserve that relationship. If they are not, use a supported source-offset or synchronization route that owns the native multicam timing. Do not repair camera sync by shifting only the external microphones, and do not hand-edit native multicam internals.

After applying the relationship, compare the same action at the beginning and several later points. Constant early alignment does not rule out drift. Verify source identity separately from timing: a perfectly synchronized microphone assigned to the wrong person is still a failed plan.

When an approved manually synchronized timeline exists, preserve it and refine only the proven mismatch. Use the public CutAgent technical skills `cutagent-multicam`, `cutagent-editing`, and `cutagent-verification` for the current executable route and evidence.
