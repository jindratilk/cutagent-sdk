# Compositing, masks, and depth

Read this when building layered geometry, materials, attached labels, or spatial scenes. Inspect exact node ports in the installed public reference before authoring an unfamiliar branch.

## Alpha and layer order

For foreground-over-background, connect the base to `Merge.Background` and the layer to `Merge.Foreground`. Connect the result onward to another Merge or MediaOut. A correct node that is not on this final branch cannot affect the picture.

A Background with `TopLeftAlpha = 0` supplies a transparent canvas. Use `TopLeftAlpha`, not an assumed generic `Alpha` input. A colored Background connected to a RectangleMask or EllipseMask through `EffectMask` produces a native shape. Use the mask's `Mask` output. A full opaque background accidentally included in a component branch can hide everything beneath it.

Merge `Blend` controls the visibility of the assembled foreground. Use it for whole-element fades so fill, text, and decoration remain coherent. Text shading alpha affects a specific shading element; it is a different control. Examine checkerboard/alpha and a contrasting background when a supposedly transparent overlay appears black.

## Mask ownership

Decide what the mask limits: source geometry, the processed effect, or the complete foreground composite. These yield different results. A shape blurred after masking grows beyond its original boundary. A blur constrained by a later mask remains clipped. To create a reveal, apply a dedicated reveal mask to the assembled branch or its final Merge; keep the original shape mask responsible for geometry.

Keep mask format and pixel aspect aligned with the image. Derive corner radius, border width, and stroke thickness from visible scale and native units. Do not assume a number corresponds to pixels. Inspect curves at full size for faceting, angular joins, and thin-line aliasing. For procedural paths, separate point positions and tangent handles; smooth spatial handles create smooth geometry, while temporal easing changes how quickly it is revealed.

## Material construction

Build a shadow from a duplicated silhouette, an offset, a blur, and restrained opacity behind the object. Build a glow from a softer, wider duplicate behind a crisp core. The crisp branch preserves shape and text contrast. Keep these branches linked to the same source geometry and shared transform.

A glass panel requires background context: a restrained translucent fill, a clipped softened background contribution, a subtle edge/highlight, and legible foreground type. A bright rectangle with heavy blur is not sufficient. Discover available displacement/refraction inputs before using them; reduce distortion before sacrificing legibility.

Work with a small palette and compare the exported result with the intended appearance. Color management and viewing transforms can change apparent brightness and saturation. Diagnose those boundaries before compensating with arbitrary extreme values. Do not convert the whole scene to grayscale merely because a default shading input was omitted.

## Shared transforms

Assemble text, fill, and accent over transparency, then pass the assembled image through one Transform. This keeps children attached during translation, rotation, and scale. Leave the final opaque canvas outside the group. A transform's pivot affects rotation/scale; its center affects placement. Set a deliberate pivot when an element should hinge from an edge.

For screen-space UI over a 3D render, composite after Renderer3D. For a label physically attached to a 3D object, place text/image geometry in the scene and share the object's transform before rendering. Do not animate two unrelated transforms and assume they will stay attached under perspective.

## Native 3D structure

Use this conceptual graph, then discover the exact supported nodes and ports:

```text
Camera + geometry + materials + lights
                → Merge3D → Renderer3D → screen-space treatment → MediaOut
```

Use Text3D for extruded scene lettering when available; use TextPlus feeding ImagePlane3D for a flat textured label in space. Place flat labels slightly in front of a surface to avoid coplanar flicker. Check camera framing, clipping, geometry orientation, lighting, renderer settings, and alpha before adding camera motion. Keep object scale, distance, and focal behavior mutually consistent.

The typed SDK only accepts registry-verified node/port pairs. A familiar Fusion node may be available through native `.setting` while absent from the typed registry. Use the supported public route; do not invent an SDK node or bypass type checks. Verify perspective/occlusion at multiple times when depth is part of the claim.
