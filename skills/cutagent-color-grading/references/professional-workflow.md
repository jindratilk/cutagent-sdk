# Professional color workflow

Use this reference for cinematic grades, log footage, skin-tone work, product color, shot matching, or a review of an existing grade.

## Correction before look

1. Identify the source profile and intended display.
2. Normalize only when the input transform is known.
3. Set exposure from scopes and scene intent.
4. Balance temperature and tint with trustworthy neutral or skin anchors.
5. Shape contrast, black density, and highlight rolloff.
6. Build saturation density and hue separation.
7. Match shots before adding independent style.
8. Add a reducible look, local light shaping, and finish.

The point of separate stages is reversibility and diagnosis, not a large node count. Each stage must change the active image path and have one visible responsibility.

## Scene judgment

For people, protect believable skin and separate the subject from the background with light, not a halo. For products, preserve brand color, labels, whites, and material texture. For landscapes, separate sky, land, water, and foreground depth without radioactive foliage or cyan shadows. For screen and webcam footage, avoid unnecessary log transforms and aggressive contrast.

Motivated light may be warm, cool, green, neon, or mixed. Do not neutralize it merely because parade channels differ. Use the most trustworthy shared anchors when matching: skin, wardrobe, walls, pavement, tabletop, sky, practicals, or product packaging.

## Creative palette

Describe the look as relationships, not preset names: warm highlights against restrained cool shadows; dense greens with neutral skin; soft highlight rolloff with deep but open blacks; muted surroundings around one brand color. Build only the relationships supported by the footage.

Keep the look easy to reduce. A LUT or PowerGrade is a taste layer, not a technical correction. Local windows should reinforce light already suggested by the scene. Grain, glow, halation, and texture belong after the image reads correctly without them.

## Review rubric

Revise when skin turns green, magenta, sunburned, waxy, or plastic; neutrals gain an accidental tint; saturated colors clip; shadows reveal distracting noise; highlights flatten; local shaping creates halos; adjacent shots lose shared anchors; or the look becomes more noticeable than the subject.

Correct the largest visible mismatch revealed by the first pass; stop when the requested look and continuity are achieved. Use the public CutAgent technical skills `cutagent-color` for technical execution and evidence.
