# Design and layout

Read this when translating a brief into a scene or improving an unconvincing result. Treat node count as an implementation detail; visual hierarchy and meaningful movement determine quality.

## Build the settled frame first

Identify one primary message, a supporting visual mechanism, and a small number of secondary details. Establish a dominant focal region and deliberate negative space. Work in the delivery aspect ratio, with margins derived from the actual frame. For responsive variants, recompute layout anchors and line breaks rather than cropping a wide composition into a tall frame.

Use a compact design specification: background color, primary and secondary type, accent color, margin, inter-item gap, major shape sizes, and timing phases. Let these shared values govern multiple nodes. For a diagram, define a data model of nodes and edges before drawing; for an interface scene, define the hierarchy of panels, controls, states, and feedback before animating.

Choose a compositional grammar suited to the request:

| Scene | Useful structure | Motion that explains it |
| --- | --- | --- |
| Editorial title | One dominant phrase, quiet supporting line, restrained accent | Accent establishes position, title arrives, long reading hold |
| Diagram | Distinct entities, clear connectors, one highlighted relation | Reveal source, trace relationship, then expose consequence |
| Interface explanation | A legible panel, one active control, visible state change | A single action causes a coordinated response |
| Data story | Scale, labels, values, and one emphasized comparison | Reveal context before changes; maintain a readable baseline |
| Abstract brand scene | Repeated geometry with controlled variation | Shared motion rules with one focal exception |

## Typography

Use TextPlus for editable 2D lettering. Set `StyledText`, an available `Font` and `Style`, size, placement, and deliberate foreground color. Verify the exact installed face/style through public discovery or native readback; a plausible family name can silently fall back. Confirm glyph coverage for accented text and symbols.

Establish hierarchy through size, weight, spacing, and placement before adding glow or multiple colors. A useful initial hierarchy is one clearly dominant size with a secondary size around half to two-thirds as large; adjust for actual copy, font metrics, and viewing distance. Keep the reading order unambiguous. Break lines at meaningful phrase boundaries and avoid a single stranded word. Test the longest realistic text when building a reusable template.

`TextPlus.Size` is not a pixel font size. Judge it in the composition and preserve the actual text payload. Avoid shrinking all text to fit a crowded scene; reduce secondary detail or distribute information over time. Keep a quiet region behind the primary phrase. Use a downstream Transform to move a text group without changing its typesetting.

For rich character styling, use the installed supported template/text route or inspect a captured StyledTextCLS structure. Do not guess numeric character-style codes or Unicode index conventions. A styling modifier may own the actual text instead of a literal `StyledText` on the TextPlus node.

## Panels, diagrams, and richer scenes

A card consists of a masked fill, optional edge or shadow, accent/label, content, and a shared transform. Build on transparent pixels and merge the assembled card onto the canvas. Derive label anchors from the card's bounds so resizing does not leave text floating independently.

For repeated components, vary content while keeping radius, padding, border weight, type alignment, and entrance logic consistent. Separate shape geometry from motion. For a diagram, make the connectors visually subordinate to the entities; align arrow endpoints with their targets and keep labels off intersections. Native editable geometry should explain a relationship rather than imitate a screenshot of an interface.

Use richer content to clarify the idea: a changing counter paired with a growing bar, a path paired with a destination, a panel that rearranges its contents, or a set of cards that forms a larger structure. Add only details that survive the intended viewing scale. Keep photographic assets subordinate when the user's request is native motion design.

## Reference interpretation

Describe the reference in measurable relationships: dominant shape size, margin, line lengths, type hierarchy, warm/cool balance, edge softness, depth, and motion rhythm. Preserve those relationships while adapting content. Do not equate a screenshot match at one frame with a successful animation.

Review the scene at full resolution and at likely delivery size. Check optical centering, unintended tangencies, clipping, thin strokes, text contrast, and whether all attention goes to the intended subject. Fix hierarchy and spacing before surface polish.
