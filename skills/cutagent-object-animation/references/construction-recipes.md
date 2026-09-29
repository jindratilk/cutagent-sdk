# Object-animation construction recipes

These topologies and timing models describe original rigs. Resolve exact tool and input identifiers through the installed public CutAgent SDK and CLI reference and live inspection.

## Build one object before animating it

Assemble the object's internal layers at rest, then move the completed object through one parent:

```text
image or UI source -> crop/matte -> object style -----\
backing shape ---------------------------------------- layered Merges -> parent Transform -> output
border, shadow, or label -----------------------------/
```

Place a shadow relative to the card before the parent Transform so it follows the card. If a label must stay fixed in the screen while the object moves, keep it outside the parent deliberately; otherwise group it. Choose the parent pivot from perceived mechanics: center for a pop, hinge edge for a panel, contact point for a pinned card.

## Entrance, hold, and exit keys

Separate arrival, settling, and the reading hold when a soft settle is wanted:

```text
offscreen start -> near-rest -> small overshoot -> exact rest -> hold end -> offscreen end
```

A useful initial phase split is 0%, 12%, 18%, 24%, 78%, and 100% of clip duration. Repeat the exact-rest values at hold end so the object remains still from 24% to 78%, rather than drifting out of overshoot through the reading hold. This is a starting model, not a fixed preset. Heavy objects can omit overshoot and take longer to arrive; light icons can reach near-rest quickly and settle once. For an entrance-only object, remove the exit pose and hold exact rest through the end.

Shape the entrance curve with fast early travel and gentle braking. Keep the hold completely constant. Start the exit with enough acceleration that it reads as a new action rather than a continuation of residual wobble.

For a duration-adaptable rig, anchor entrance and exit phases to their respective ends and stretch only the hold between them using the supported native timing structure. When a clip becomes shorter, remove stagger and secondary motion first; do not squeeze both endpoints until the object never rests.

## Direction pairs

Represent direction as start and end positions around one exact settled point:

- Right-to-left continuation: start beyond right edge, rest in frame, end beyond left edge.
- Right-in/right-out presentation: start beyond right edge, rest, return beyond right edge.
- Bottom-in hold: start below the safe frame, rest, no exit travel.

Base offscreen values on the object's bounds, not a universal coordinate. Include blur, shadow, and rotation extents when calculating when it is fully outside the frame.

## Velocity-linked squash and blur

Apply deformation after the parent motion transform when it should describe the whole object's speed:

```text
assembled object -> parent motion -> velocity deformation -> motion blur -> Merge over plate
```

At peak horizontal speed, slightly lengthen X and compress Y; reverse axes for vertical motion. Return both to neutral at rest. Preserve approximate visual area and use a small range for screenshots and logos so content remains recognizable. If exact velocity cannot drive the deformation through the supported interface, key the deformation near the fastest and impact frames rather than inventing an unsupported expression route.

Motion blur rises with travel and falls to zero before the reading hold. A short impact shake belongs after the settle point and decays rapidly. Do not put perpetual noise upstream of a readable UI card.

## Review samples

Inspect at least the first visible frame, peak travel, overshoot or impact, exact rest, exit launch, and last visible frame. Confirm the object's children share one trajectory and that crop, shadow, and alpha edges remain coherent. Then review at normal speed to judge weight; evenly spaced frame samples cannot prove the curve feels natural.
