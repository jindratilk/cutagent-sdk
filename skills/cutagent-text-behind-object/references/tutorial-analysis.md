# Text-behind-object route selection

All successful variants share the same visual model: original plate, editable text, and a foreground-only layer above the text. Choose the foreground route from the silhouette and movement.

## Tracked subject matte

Use for people, hair, hands, vehicles, foliage, products with irregular edges, or moving cameras. Seed the complete subject, not only a high-contrast detail, and review the full crossing interval. A tracked matte is accepted only when the isolated foreground and final composite both hold over time.

## Original Fusion masks

Use for static architecture, screens, signs, simple products, or predictable geometric occluders. Combine a small number of editable shapes when necessary, but prefer one coherent silhouette over several masks that fight each other. The bundled mask assets are starting geometry; adapt their shape, softness, timing, and source fit to the shot.

## External alpha

Use only when the native matte cannot meet the shot's quality bar and the user accepts an external isolation step. Keep the final plate, editable text, and foreground alpha layered in DaVinci Resolve. Report the external source honestly.

## Proof

Review all-on frames at early, middle, and late positions; foreground-only frames at the same positions; a foreground-disabled comparison at maximum overlap; and a short temporal preview. Reject detail-only mattes, broad background selection, text leaks, edge drift, scale mismatch, flashes, and duplicate-layer pops.
