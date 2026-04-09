# Murmur Manifesto

Murmur is a language for people who are tired of hiding intent inside machinery.

It begins with a simple suspicion: most software is doing two jobs at once.
It must tell a machine what to do, and it must tell humans what is meant.
We are absurdly good at the first part, and notoriously careless with the second.

So Murmur tilts the table.

It treats a program as a document first.
Not a comment-wrapped script. Not an opaque runtime with decorative prose stapled on top.
A real document: readable, explainable, reviewable, haunted by purpose.

Markdown carries the shape of thought.
YAML carries the executable structure.
The runtime stays small.
The meaning lives in the text.

## Why it exists

Most workflow systems eventually become one of two things:

- a maze of buttons and hidden state
- a pile of code nobody wants to read at 2:13 a.m.

Murmur wants a third path.

A Murmur file should look like procedure, notes, planning, operations, ritual, or documentation, while still being exact enough to execute.
It should let a human scan the page and understand the intention before they understand the engine.
It should let a machine act without swallowing the whole truth.

This is not nostalgia for plain text.
It is a design choice.
Plain text is inspectable, durable, diffable, and weirdly honest.

## The wager

We believe executable documents can be better than either scripts or dashboards for a large class of work.

Not all work. That would be a tedious religion.

But for workflows, procedures, automation, agent plans, handoffs, operational playbooks, and semi-structured decisions, the document is often the right unit of thought. It already contains the instructions, the explanation, the caveats, and the desired outcome. Murmur simply stops pretending those things belong in separate worlds.

## What Murmur values

### 1. Intent should be visible

If a workflow sends a message, writes a file, calls a model, or touches the network, that fact should be easy to see.
Hidden side effects are not elegant. They are how people get ambushed.

### 2. The runtime should be small

A gigantic magical system eventually becomes its own bureaucracy.
Murmur prefers a compact runtime with stable primitives and documents that carry most of the meaning.
The engine should execute. The file should explain.

### 3. Documents are not second-class

In most systems, documentation trails behind reality like a wounded ghost.
In Murmur, the document is the thing.
It can be read by a person, parsed by tooling, checked into version control, reviewed in a pull request, and executed by a runtime without being translated into a separate hidden form.

### 4. AI may assist, but it does not get custody

Murmur is friendly to AI-assisted authoring because the format is explicit, inspectable, and text-native.
But the authored document remains the source of truth.
The model is a helper, not a priesthood.

### 5. Names matter

Murmur does not aspire to sterile enterprise verbs.
Its vocabulary should feel descriptive, expressive, and a little uncanny.
Words like `weave`, `utter`, `distill`, and `heed` are not decoration. They are reminders that programming can still have texture.

## What it is not

Murmur is not a replacement for systems programming.
It is not a performance language.
It is not a demand that all ambiguity is sacred.
It is not a giant natural-language blob executed by vibes.
It is not an excuse to abandon rigor.

If the problem wants C, Rust, SQL, or a shell script, let it want those things.
Murmur is for the territory where procedure, documentation, and executable intent overlap.

## The feel of the thing

A good Murmur document should feel strangely legible.
Someone should be able to open it cold and think:

“I see what this is for.”
“I see what happens next.”
“I see where the dangerous parts are.”
“I could edit this without being initiated into a private cult.”

That feeling matters.
It is not cosmetic. It is operational.

Readable systems survive contact with reality better.

## A language disguised as procedure

Murmur looks almost innocent.
A heading. A purpose. A block of YAML. A few named steps.
But that disguise is the point.
The boundary between note, plan, checklist, playbook, and program is not as fixed as tooling has taught us to believe.

There is a fertile middle ground where a document can be both human-readable and executable without collapsing into mush.
Murmur is trying to inhabit that ground cleanly.

## For builders, operators, and careful weirdos

Murmur is for people who want automation without surrendering legibility.
For teams who review workflows in Git.
For operators who need procedures that still make sense under stress.
For AI-heavy systems that need inspectable artifacts instead of hidden prompt sludge.
For anyone who suspects that source code can be a little more honest than this.

## The promise

Not that everything becomes simple.
Not that text alone saves us.
Not that YAML suddenly becomes beautiful by divine intervention.

The promise is narrower, and more believable:

A Murmur program can look like planning, read like documentation, and execute like software.

That is enough to be interesting.
That is enough to build.
That is enough to begin.
