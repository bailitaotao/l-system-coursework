#let student = "Haoyang Tao"
#let programme = "MSc Games Programming"
#let module-name = "Mathematics and Graphics for Computer Games 1"
#let submission-date = "2026-11-24"

#set document(title: "Branch Studies", author: student)
#let ink = rgb("#20362c")
#let secondary = rgb("#53695d")
#let accent = rgb("#2c6646")
#let rule = rgb("#bac9bc")
#set page(
  paper: "a4",
  margin: (x: 30mm, top: 23mm, bottom: 20mm),
  header: [
    #text(size: 8pt, fill: secondary)[BRANCH STUDIES  /  L-SYSTEM STUDIO]
    #v(2pt)
    #line(length: 100%, stroke: 0.5pt + rule)
  ],
  footer: [
    #line(length: 100%, stroke: 0.5pt + rule)
    #v(2pt)
    #text(size: 8pt, fill: secondary)[L-System coursework #h(1fr) #context counter(page).display("1")]
  ],
)
#set text(lang: "en", size: 11pt, fill: ink)
#set par(leading: 0.60em, spacing: 0.80em)
#show heading.where(level: 1): set text(size: 23pt, weight: "regular", fill: ink)
#show figure.caption: set text(size: 9pt, fill: secondary)
#show link: set text(fill: accent)

#let cover-field(label, value) = grid(
  columns: (34mm, 1fr), gutter: 4mm, align: horizon,
  text(size: 10pt, fill: secondary, label),
  block(width: 100%, height: 8mm, stroke: (bottom: 0.5pt + rule), value),
)

#let plate(file, height, alt, caption) = figure(
  image("gallery/" + file, width: 100%, height: height, fit: "contain", alt: alt),
  caption: caption,
)

#v(5mm)
#text(size: 10pt, fill: accent)[COMPUTATIONAL GEOMETRY  /  COURSEWORK 1]
#v(4mm)
#text(size: 42pt)[Branch Studies]
#v(1mm)
#text(size: 17pt, fill: secondary)[A two-dimensional L-system studio]
#v(7mm)
#align(center, image("gallery/06-plant-f.png", height: 105mm, alt: "Plant F at generation five."))
#v(7mm)
#cover-field[Student][#student]
#cover-field[Programme][#programme]
#cover-field[Module][#module-name]
#cover-field[Submission date][#submission-date]
#cover-field[GitHub repository][#link("https://github.com/bailitaotao/l-system-coursework")[github.com/bailitaotao/l-system-coursework]]

#pagebreak()

= Objective and interaction

Branch Studies explores a question that can be tested with a single drawing. How much of a plant's appearance comes from the order of its instructions, and how much comes from the numbers used to draw them? The program opens with Plant A at generation five. A visitor can read its short rule below the canvas, step backwards until only one line remains, and advance again until the stem carries thousands of small shoots. The same window also draws a pair of continuous curves. Together these examples address the eight configurations requested in the coursework brief @brief.

The controls support two different comparisons. Pressing a number selects a file and restores that specimen's reference settings. This makes it possible to recover a known result after changing several values. The generation controls instead preserve the selected specimen and its drawing settings. A visitor interested in the angle of a branch can therefore hold the generation constant, change the angle and inspect the new silhouette. The status line identifies the current specimen and gives the number of segments, which helps distinguish a change in geometry from an increase in the amount of geometry.

Each preset is a small JSON document @json-doc. It contains the initial word, the replacement rules, the reference generation, the starting direction, the turn angle and the length of one step. Keeping these values together makes a model editable with an ordinary text editor. For example, a visitor can change the reference angle in the first configuration, save it, and press 1 in the running application to read the new value. The program resolves the configuration directory relative to its source file, so a different working directory does not change which specimen is loaded.

#plate("app-window.png", 108mm,
  "The desktop studio showing Plant A and its controls.",
  [The running studio with Plant A loaded.],
)

#pagebreak()

= From symbols to branches

A production describes the next generation of a symbol. In Plant A the initial word is F. Its one production gives five occurrences of F interspersed with turns and brackets. The program reads the whole old word in order and looks up each symbol in the rule dictionary. It collects the pieces and joins them into a new string. Only after that pass can a newly produced F take part in another replacement. A symbol with no rule passes through unchanged. This preserves the brackets inserted in early generations as the structures inside them become longer @plants.

This repeated substitution is the first mathematical idea in the project. If $omega_n$ is the complete instruction word at generation $n$, and $h$ means “replace each symbol using the production rules”, then the generations are defined by

$ omega_0 = "F", quad omega_(n+1) = h(omega_n). $

For Plant A, each F produces five new F symbols. Since turns and brackets produce no F symbols, the number of drawable steps obeys $N_0 = 1$ and $N_(n+1) = 5 N_n$, giving $N_n = 5^n$. At generation five this predicts $5^5 = 3,125$ line segments. This count is a useful check, but it does not specify where the branches appear; their order and the turtle's state determine the shape.

The drawing pass starts at the origin with an initial heading. F advances one step in that direction and records a segment between the old and new positions. The horizontal displacement is the step length multiplied by the cosine of the heading, and the vertical displacement uses the sine. The interface displays degrees, and the interpreter converts to radians for these calculations. A plus sign adds the turn angle and a minus sign subtracts it. The final projection reverses the vertical direction so that a heading of ninety degrees appears upwards on the screen.

The second mathematical idea is to interpret the word as a sequence of transformations of a turtle state. Write its position as $(x_k,y_k)$, its heading in radians as $theta_k$, its step length as $L$, and its displayed turn angle as $alpha$ degrees. First convert the turn to radians, $delta = alpha pi / 180$. For each F, the next point is

$ x_(k+1) = x_k + L cos(theta_k), quad y_(k+1) = y_k + L sin(theta_k). $

For a turn, the heading changes by $theta_(k+1) = theta_k + delta$ for + and $theta_(k+1) = theta_k - delta$ for -. These equations are exactly the coordinate updates used by the interpreter. The screen drawing negates the vertical coordinate at projection time, because screen pixels increase downwards.

The bracketed part of the first rule provides a small test of the interpreter. Immediately after its first forward step, the opening bracket saves the current position and direction. The turtle turns left and draws one line. The closing bracket restores both saved values without leaving a mark. The next forward command therefore continues up the original stem. Saving only the position would produce the correct starting point but the wrong direction for that stem. A stack also handles nested branches because the inner branch returns to its own fork before the outer branch resumes. The same instructions are sufficient for all six plant specimens.

In state notation, an opening bracket pushes the current triple $(x,y,theta)$ onto a last-in, first-out stack; the matching closing bracket pops that triple back into the active state. The current path is therefore restored to the exact fork point and heading. Nested brackets work because the most recent saved state is restored first. This is the key implementation detail behind branching: the turtle does not need to find a branch start geometrically; it remembers it when it encounters an opening bracket.

#plate("01-plant-a.png", 107mm,
  "An upright branching stem with progressively finer side shoots.",
  [Plant A at generation five. Each fork returns to its saved position and heading.],
)

#pagebreak()

= Six reference plants

The first three specimens rewrite F directly. At their target generations, plants A and B both contain 3,125 forward commands. Their drawings nevertheless differ markedly. In A, the last F lies on the continuing axis after the second side shoot has been completed. In B, the final forward step is enclosed in brackets. Its endpoint is visited, but the interpreter returns to the saved fork before continuing with the following symbol. The reference angles also differ. Counting the commands alone therefore gives an incomplete check of the result. Checking the way shoots rejoin the stem reveals errors that leave the total unchanged.

Plant C supplies a more demanding example of the same method. Its production contains eight forward commands, and four full replacements give 4,096 visible line segments. Several of those instructions occur inside the same bracket pair. A turn outside the pair changes the direction that will be stored when the next pair opens. Moving a minus sign across a bracket would preserve every forward command and still change the outline. The figure allows the placement of the main stem and the relative density of the crown to be compared with the supplied reference @brief @plants.

The lower three specimens begin with X. In this interpreter X has no drawing action, so their generation zero contains no line. The window explains that state, and stepping forward reveals the first F. In later generations the rule for F doubles an existing length, while the rule for X introduces future growing points. D and E each reach 4,118 segments at generation seven. Their different arrangements of the same number of segments make a useful second comparison. F reaches 1,488 segments at generation five, with nested brackets giving a distinct asymmetric crown. In the plate each drawing has been fitted separately so that its internal structure remains visible.

#plate("six-plants.png", 105mm,
  "Two rows of plant specimens A to F.",
  [The six required plants at the generations and angles given in the brief.],
)

#pagebreak()

= Parameter experiments

Three controls change drawing geometry independently of the generation. The angle experiment shown below uses a single word from generation four of Plant A. It has 625 forward commands. At fifteen degrees both shoots stay close to the main stem. At the reference angle of 25.7 degrees, gaps open between the larger branches. At forty degrees the crown spreads to the sides and more small shoots point away from the vertical. All three images have the same number of lines. This is a practical way to distinguish a turn applied at every fork from a change to the production itself.

The length control changes the distance travelled by every forward command. At a fixed generation, doubling that distance doubles the distance between corresponding points in the drawing. The default view uses the reference plant to set its scale, then centres the current geometry. This allows the difference in size to remain visible. A sufficiently large drawing may extend beyond the canvas. The Fit current drawing option recalculates the view from its current bounds. With Fit enabled, changing every length by the same factor can produce almost the same displayed silhouette because the view compensates for the change.

Initial heading gives a different result again. Turning the heading by twenty five degrees rotates the whole plant about its starting point in model coordinates. The angles between adjoining branches remain the same. Recentring the drawing can move the apparent position of the root on screen, so branch orientation is a better comparison than its pixel position. An optional colour mode assigns a shade to each segment according to the number of saved branch states. It makes nested forks easier to follow when shoots overlap. The colour describes bracket depth, and a higher generation can still contain segments drawn at depth zero.

#plate("angle-study.png", 69mm,
  "Plant A drawn at 15, 25.7 and 40 degrees.",
  [Generation four at three turn angles. Each specimen is fitted to its panel.],
)

#pagebreak()

= Curves, verification and limits

The two freely chosen configurations test how far the interpreter generalises. One side of a Koch snowflake uses four forward strokes and turns of sixty degrees to replace a single line @plants. At generation four it produces 256 segments. In the traditional bounded construction each new stroke is one third as long as the one it replaces. This program keeps the user's step length constant across generations. At a given generation the displayed curve therefore has the same shape up to a uniform scale, while its extent in model coordinates grows. The distinction matters when comparing two generations using the fixed reference view.

The dragon curve starts from FX and uses the two auxiliary letters X and Y to organise its turns @dragon. Only F leaves a visible mark. At ten generations the result contains 1,024 straight segments connected at right angles. Since the word has no brackets, depth colouring assigns every segment the same shade. This behaviour provides a quick check that the colour is driven by saved states rather than the number of turns or the position of a symbol in the word.

The desktop application uses Tkinter for its input and drawing surface @tk-doc. Verification exercised the actual number keys for all eight presets and compared each canvas segment count with the expected value. Plant A was stepped down from five generations to zero and back up. Both directions of all three parameter controls were checked, and each exported reference drawing contained the same number of SVG paths as the screen contained line segments. These checks establish specific properties of the implementation. They cannot establish pixel equality with the printed reference, whose scale and line weights differ.

The main practical limit is growth in the length of the word. Each drawn segment also becomes one canvas item. Stepping is bounded by the selected reference generation, and the engine rejects an expansion beyond its symbol budget. For these eight specimens, explicit words make intermediate results easy to inspect and explain. A later version intended for much larger plants could interpret expansions as a stream, which would reduce the memory required for the word while leaving the cost of displaying all the visible branches to be addressed.

#plate("two-curves.png", 60mm,
  "The Koch curve beside the right-angled dragon curve.",
  [The two additional configurations share the same drawing instructions.],
)

#pagebreak()

#bibliography("report/references.bib", style: "ieee", title: [References])
