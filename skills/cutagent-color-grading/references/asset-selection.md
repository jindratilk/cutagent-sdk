# Choose a local color asset

Use a user supplied or locally licensed LUT, PowerGrade, DCTL, reference still, grain, or overlay. Confirm its rights, technical input expectation, color space, and intended use before applying it. A technical transform can conflict with existing DaVinci Resolve color management; a creative look can damage neutrals or skin even when its label sounds suitable.

Preview a small set against representative frames at the intended output transform. Compare with the asset bypassed. Use the installed CutAgent SDK or CutAgent CLI to apply only supported asset types and inspect the returned result. Treat decorative media such as grain and overlays as separate footage or Fusion elements, not as a color node effect unless the local capability expressly supports it.

Verify across the scene with `cutagent-color` and `cutagent-verification`. Record the source, license, required attribution, and any unverified camera profile or output transform.
