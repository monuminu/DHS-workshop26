"""Build the DHS 2026 "Agentic AI" companion lecture deck.

Extends the provided Analytics Vidhya x DataHack Summit template by duplicating its
branded slides (so backgrounds + logos carry over) and injecting fresh content +
the 6 workshop diagrams (reused from docs/assets/).

Template slides (0-indexed):
    0 = title      (dark neon bg)        -> light text
    1 = section    (white bg, title only) -> dark text   [duplicate for dividers]
    2 = content    (white bg, title+body)  -> dark text   [duplicate for content]
    3 = closing    (dark "Thank You" bg)  -> light text

Run:  python slides/build_deck.py
Out:  slides/DHS-2026-Agentic-AI.pptx
"""

from __future__ import annotations

import copy
import os

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.expanduser(
    "~/Downloads/DHS 2026 Workshop Presentation (Tentative).pptx"
)
ASSETS = os.path.join(ROOT, "docs", "assets")
OUT = os.path.join(HERE, "DHS-2026-Agentic-AI.pptx")

# --- brand palette --------------------------------------------------------
INK = RGBColor(0x18, 0x18, 0x18)       # near-black body text on white
GRAY = RGBColor(0x44, 0x44, 0x44)      # secondary text
INDIGO = RGBColor(0x4B, 0x3F, 0xC4)    # matches the diagrams' indigo
MAGENTA = RGBColor(0xD6, 0x24, 0x9F)   # brand magenta
CYAN = RGBColor(0x10, 0x9A, 0xB5)      # brand cyan (darkened for white-bg legibility)
PURPLE = RGBColor(0x6B, 0x3F, 0xA0)    # brand purple
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CARD_BG = RGBColor(0xF3, 0xF1, 0xFB)   # very light purple card fill
FONT = "Arial"

# slide canvas (inches)
SW, SH = 10.0, 5.625
DIAG_RATIO = 1.5  # all diagrams are 3:2

# template slide indices
T_TITLE, T_SECTION, T_CONTENT, T_CLOSING = 0, 1, 2, 3


# ============================ low-level helpers ============================
def duplicate_slide(prs: Presentation, src_index: int):
    """Deep-copy slide `src_index` (XML + part relationships) and append it.

    Copies the picture/background relationships so the branded background image
    is preserved on the new slide.
    """
    src = prs.slides[src_index]
    # Use the source slide's own layout so inherited bits line up.
    blank = src.slide_layout
    new = prs.slides.add_slide(blank)

    # Remove the placeholder shapes that add_slide created from the layout,
    # so we start from an empty shape tree and clone the source's shapes.
    for shp in list(new.shapes):
        shp._element.getparent().remove(shp._element)

    # Clone every shape element from the source.
    for shp in src.shapes:
        new.shapes._spTree.append(copy.deepcopy(shp._element))

    # Re-create relationships referenced by the cloned XML (images, etc.) so the
    # branded background image carries over. We preserve the *exact* rId the
    # cloned <a:blip r:embed="rIdN"/> elements point at by constructing the
    # _Relationship directly (python-pptx 1.0.x has no public rId-preserving API).
    from pptx.opc.constants import RELATIONSHIP_TARGET_MODE as RTM
    from pptx.opc.package import _Relationship

    dst_rels = new.part.rels
    for rId, rel in src.part.rels.items():
        if "image" in rel.reltype and rId not in dst_rels._rels:
            dst_rels._rels[rId] = _Relationship(
                dst_rels._base_uri,
                rId,
                rel.reltype,
                target_mode=RTM.INTERNAL,
                target=rel.target_part,
            )
    return new


def _set_run(run, text, size, color, bold=False, italic=False):
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def clear_textbox_keep_first(shape):
    """Empty a textbox down to a single blank paragraph/run we can write to."""
    tf = shape.text_frame
    # keep first paragraph, drop the rest
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    p0 = tf.paragraphs[0]
    for r in p0.runs[1:]:
        r._r.getparent().remove(r._r)
    if not p0.runs:
        p0.add_run()
    return tf


def set_title(slide, text, *, color=INK, size=26):
    """Find the template's title textbox (contains '<<...Title...>>') and set it.

    Falls back to the first non-background textbox.
    """
    target = None
    for shp in slide.shapes:
        if shp.has_text_frame and "Title" in shp.text_frame.text:
            target = shp
            break
    if target is None:
        for shp in slide.shapes:
            if shp.has_text_frame and shp.shape_type != 13:
                target = shp
                break
    tf = clear_textbox_keep_first(target)
    _set_run(tf.paragraphs[0].runs[0], text, size, color, bold=True)
    return target


def remove_body_placeholders(slide, keep_shape=None):
    """Drop the template's stray 'Text1/Text2/Text3' body textbox and empty
    placeholders so they don't show through our content.

    `keep_shape` is the title textbox we already populated (its text no longer
    contains '<<...Title...>>', so we must protect it explicitly).
    """
    keep_el = keep_shape._element if keep_shape is not None else None
    for shp in list(slide.shapes):
        if shp.shape_type == 13:  # picture (background) -> keep
            continue
        if shp._element is keep_el:   # the title we just set -> keep
            continue
        if not shp.has_text_frame:
            continue
        txt = shp.text_frame.text
        if "Title" in txt:  # an as-yet-unset title box -> keep
            continue
        # remove empty placeholders and the Text1|Text2|Text3 sample box
        shp._element.getparent().remove(shp._element)


def add_textbox(slide, x, y, w, h, *, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    return box


def add_bullets(slide, x, y, w, h, items, *, size=15, color=INK, gap=6,
                bullet_color=INDIGO):
    """items: list of (text) or (text, level). Renders dash bullets."""
    box = add_textbox(slide, x, y, w, h)
    tf = box.text_frame
    first = True
    for it in items:
        text, level = (it if isinstance(it, tuple) else (it, 0))
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = level
        p.space_after = Pt(gap)
        # bullet glyph
        rb = p.add_run()
        _set_run(rb, ("•  " if level == 0 else "–  "),
                 size, bullet_color, bold=True)
        rt = p.add_run()
        _set_run(rt, text, size if level == 0 else size - 1,
                 color if level == 0 else GRAY)
    return box


def add_picture_fit(slide, path, *, x, y, max_w, max_h):
    """Place an image scaled to fit inside (max_w, max_h), centered in that box."""
    iw, ih = Image.open(path).size
    ratio = iw / ih
    w = max_w
    h = w / ratio
    if h > max_h:
        h = max_h
        w = h * ratio
    cx = x + (max_w - w) / 2
    cy = y + (max_h - h) / 2
    return slide.shapes.add_picture(path, Inches(cx), Inches(cy),
                                    Inches(w), Inches(h))


def add_caption(slide, x, y, w, text, *, size=11, color=GRAY, align=PP_ALIGN.CENTER):
    box = add_textbox(slide, x, y, w, 0.3)
    p = box.text_frame.paragraphs[0]
    p.alignment = align
    _set_run(p.add_run(), text, size, color, italic=True)
    return box


def add_rounded(slide, x, y, w, h, fill):
    from pptx.enum.shapes import MSO_SHAPE
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_pill(slide, x, y, w, h, text, fill, *, tcolor=WHITE, size=12):
    shp = add_rounded(slide, x, y, w, h, fill)
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_top = Pt(2)
    tf.margin_bottom = Pt(2)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _set_run(p.add_run(), text, size, tcolor, bold=True)
    return shp


# ============================ slide builders ==============================
def title_slide(prs):
    s = prs.slides[T_TITLE]  # already the first slide; just fill it
    title = "Agentic AI: Building, Optimizing\n& Operationalizing Agents"
    # The title slide has duplicated textbox sets; set both matching ones.
    for shp in s.shapes:
        if not shp.has_text_frame:
            continue
        t = shp.text_frame.text
        if "Session Title" in t:
            tf = clear_textbox_keep_first(shp)
            _set_run(tf.paragraphs[0].runs[0], title, 24, WHITE, bold=True)
        elif "Speaker Name" in t:
            tf = clear_textbox_keep_first(shp)
            _set_run(tf.paragraphs[0].runs[0], "Manoranjan Rajguru", 15, WHITE, bold=True)
        elif "Designation" in t:
            tf = clear_textbox_keep_first(shp)
            _set_run(tf.paragraphs[0].runs[0], "Microsoft", 13,
                     RGBColor(0xCC, 0xCC, 0xCC))


def section_slide(prs, label, subtitle=None):
    s = duplicate_slide(prs, T_SECTION)
    title_shape = set_title(s, label, color=INK, size=30)
    remove_body_placeholders(s, keep_shape=title_shape)
    # move the title down to a divider position and widen it
    title_shape.left = Inches(0.55)
    title_shape.top = Inches(2.0)
    title_shape.width = Inches(9.0)
    # accent rule above the title
    add_rounded(s, 0.6, 1.75, 1.6, 0.06, MAGENTA)
    if subtitle:
        sb = add_textbox(s, 0.6, 2.85, 8.5, 0.6)
        _set_run(sb.text_frame.paragraphs[0].add_run(), subtitle, 16, PURPLE)
    return s


def content_slide(prs, title, *, title_color=INK):
    s = duplicate_slide(prs, T_CONTENT)
    title_shape = set_title(s, title, color=title_color, size=24)
    remove_body_placeholders(s, keep_shape=title_shape)
    return s


def text_and_diagram(prs, title, bullets, diagram, caption=None):
    """Left: bullets. Right: diagram."""
    s = content_slide(prs, title)
    add_bullets(s, 0.55, 1.35, 4.55, 3.9, bullets, size=14, gap=7)
    if diagram:
        add_picture_fit(s, os.path.join(ASSETS, diagram),
                        x=5.25, y=1.25, max_w=4.45, max_h=3.5)
        if caption:
            add_caption(s, 5.25, 4.8, 4.45, caption)
    return s


def diagram_hero(prs, title, diagram, bullets_below=None, caption=None):
    """Big centered diagram with optional one-line takeaways underneath."""
    s = content_slide(prs, title)
    add_picture_fit(s, os.path.join(ASSETS, diagram),
                    x=2.3, y=1.15, max_w=5.4, max_h=3.2)
    if caption:
        add_caption(s, 2.3, 4.35, 5.4, caption)
    if bullets_below:
        add_bullets(s, 0.6, 4.6, 8.8, 0.9, bullets_below, size=12, gap=2)
    return s


# ============================ deck assembly ===============================
def build():
    prs = Presentation(TEMPLATE)

    # --- keep refs to the 4 originals; we'll re-order at the end ----------
    # 1) Title (fill in place)
    title_slide(prs)

    # 2) Agenda
    s = content_slide(prs, "The Day — From One LLM Call to a Full Agent")
    rows = [
        ("M1", "Your First Agent", "the agent loop, streaming"),
        ("M2", "Tools & Function Calling", "give the agent hands"),
        ("M3", "Context Engineering", "sessions, memory, compaction"),
        ("M4", "The Agent Harness  ★", "create_harness_agent — batteries included"),
        ("M5", "Multi-Agent Orchestration", "sequential, concurrent, handoff…"),
        ("M6", "Evaluating & Optimizing", "measure quality, gate CI"),
        ("M7", "Operationalizing", "tracing, middleware, guardrails"),
        ("M8", "Capstone & Hosting", "combine it all; A2A, Functions"),
    ]
    y = 1.3
    for code, name, desc in rows:
        add_pill(s, 0.55, y, 0.7, 0.34, code, INDIGO, size=12)
        bx = add_textbox(s, 1.4, y - 0.02, 8.1, 0.4, anchor=MSO_ANCHOR.MIDDLE)
        p = bx.text_frame.paragraphs[0]
        _set_run(p.add_run(), f"{name}  ", 14, INK, bold=True)
        _set_run(p.add_run(), f"— {desc}", 12, GRAY)
        y += 0.43
    add_caption(s, 0.55, y + 0.02, 9.0,
                "Labs are hands-on Jupyter notebooks · live at monuminu.github.io/DHS-workshop26",
                align=PP_ALIGN.LEFT)

    # 3) Section: Foundations
    section_slide(prs, "Foundations", "What is an agent, and why now?")

    # 4) What is an agent
    text_and_diagram(
        prs, "From an LLM Call to an Agent",
        [
            "An LLM alone is text-in, text-out — no memory, no actions.",
            "An agent wraps the model in a loop that adds three powers:",
            ("Tools — it can act, not just talk", 1),
            ("Memory — it remembers across turns", 1),
            ("Control flow — it plans and repeats until done", 1),
            "Agent = model + instructions + tools + a loop.",
        ],
        "agent-anatomy.png",
        caption="The anatomy of an agent",
    )

    # 5) The agent loop
    s = content_slide(prs, "The Agent Loop (ReAct)")
    add_bullets(s, 0.55, 1.35, 8.9, 1.4, [
        "Every agent.run() executes a reason → act → observe loop:",
        ("1 · Send conversation + available tools to the model", 1),
        ("2 · If the model calls a tool, run it and feed the result back", 1),
        ("3 · Repeat until the model returns a final answer", 1),
    ], size=14, gap=6)
    # simple flow boxes
    flow = [("REASON", INDIGO), ("ACT (tool)", MAGENTA), ("OBSERVE", CYAN), ("ANSWER", PURPLE)]
    fx = 0.7
    for i, (lbl, col) in enumerate(flow):
        add_pill(s, fx, 3.3, 1.85, 0.7, lbl, col, size=13)
        fx += 2.1
        if i < len(flow) - 1:
            ar = add_textbox(s, fx - 0.27, 3.42, 0.3, 0.4)
            _set_run(ar.text_frame.paragraphs[0].add_run(), "→", 20, GRAY, bold=True)
    add_caption(s, 0.55, 4.4, 8.9,
                "With no tools the loop is a single hop; add tools (M2) and it iterates.",
                align=PP_ALIGN.LEFT)

    # 6) Why Microsoft Agent Framework
    s = content_slide(prs, "Why the Microsoft Agent Framework")
    add_bullets(s, 0.55, 1.35, 4.7, 3.9, [
        "Open-source SDK — the successor to Semantic Kernel + AutoGen.",
        "Two core capabilities: Agents and Workflows.",
        "Code-first and fully programmable.",
        "Provider-agnostic — one interface, many backends.",
        "Python and C#.",
    ], size=14, gap=8)
    providers = ["Azure AI Foundry", "OpenAI", "Azure OpenAI", "Anthropic",
                 "Ollama", "AWS Bedrock", "Google Gemini"]
    py = 1.45
    add_textbox(s, 5.35, 1.05, 4.2, 0.3)
    _set_run(s.shapes[-1].text_frame.paragraphs[0].add_run(),
             "Swap with one env var:", 13, INK, bold=True)
    for i, pv in enumerate(providers):
        col = [INDIGO, MAGENTA, CYAN, PURPLE][i % 4]
        add_pill(s, 5.35 + (i % 2) * 2.25, py + (i // 2) * 0.55, 2.1, 0.42, pv, col, size=11)
    add_caption(s, 5.35, py + 4 * 0.55 + 0.05, 4.2,
                "MODEL_PROVIDER=…  → notebook code never changes", align=PP_ALIGN.LEFT)

    # 7) Section: Context Engineering
    section_slide(prs, "Context Engineering", "Deciding what the model sees")

    # 8) Context engineering
    text_and_diagram(
        prs, "Context Engineering",
        [
            "The model only sees what fits in its context window.",
            "Engineering that window is where real quality comes from.",
            ("Sessions — carry history across turns", 1),
            ("Context providers — inject facts before each run", 1),
            ("Memory — persist what matters", 1),
            ("Compaction — summarize so you never overflow", 1),
        ],
        "context-engineering.png",
        caption="What goes into the window each turn",
    )

    # 9) Section: The Agent Harness
    section_slide(prs, "The Agent Harness  ★", "Everything, assembled")

    # 10) The harness + diagram
    text_and_diagram(
        prs, "create_harness_agent — Batteries Included",
        [
            "Re-assembling the same machinery every time? The harness packages it.",
            "One factory call wires up:",
            ("Tool loop · history + persistence · compaction", 1),
            ("Todos (planning) · plan/execute modes", 1),
            ("Durable memory · skills · OpenTelemetry", 1),
            "Every battery can be disabled or replaced.",
        ],
        "agent-harness.png",
        caption="The 8 batteries of the harness",
    )

    # 11) Tools & function calling
    s = content_slide(prs, "Tools & Function Calling")
    add_bullets(s, 0.55, 1.35, 8.9, 2.3, [
        "A tool is a typed Python function + a docstring + the @tool decorator.",
        "The model decides when to call it; the framework runs it and loops.",
        "Approval gates put a human in the loop for risky actions:",
        ("approval_mode=\"always_require\" pauses for confirmation", 1),
        ("approval_mode=\"never_require\" runs automatically (demos)", 1),
    ], size=14, gap=7)
    for i, (lbl, col) in enumerate([("@tool", INDIGO), ("model calls it", MAGENTA),
                                    ("run + feed back", CYAN), ("approve?", PURPLE)]):
        add_pill(s, 0.7 + i * 2.1, 4.05, 1.85, 0.62, lbl, col, size=12)
    add_caption(s, 0.55, 4.85, 8.9,
                "Tools are the agent's hands — small, well-described, single-purpose.",
                align=PP_ALIGN.LEFT)

    # 12) Section: Orchestration
    section_slide(prs, "Multi-Agent Orchestration", "When one agent isn't enough")

    # 13) Orchestration patterns
    diagram_hero(
        prs, "Five Orchestration Patterns",
        "orchestration-patterns.png",
        bullets_below=[
            "Sequential · Concurrent · Handoff · Group Chat · Magentic — start with the simplest that fits.",
        ],
        caption="Specialized agents collaborating",
    )

    # 14) Section: Optimize & Operate
    section_slide(prs, "Optimize & Operate", "From demo to production")

    # 15) Evaluation
    text_and_diagram(
        prs, "Evaluating & Optimizing Agents",
        [
            "A demo that works once isn't a product.",
            "Measure quality so you can improve it on purpose:",
            ("Define checks (keyword, custom, model-graded)", 1),
            ("Run them over a query set", 1),
            ("Inspect failures → improve → re-run", 1),
            "raise_for_status() makes a regression break CI.",
        ],
        "evaluation-loop.png",
        caption="The evaluation loop",
    )

    # 16) Observability & ops
    text_and_diagram(
        prs, "Operationalizing — See Inside the Agent",
        [
            "Agents are non-deterministic and call external tools.",
            "Middleware = a control point around every model call:",
            ("Usage tracking (tokens / cost)", 1),
            ("Guardrails (redaction, injection checks)", 1),
            "OpenTelemetry gives end-to-end traces to any backend.",
        ],
        "observability.png",
        caption="Tracing, usage & guardrails",
    )

    # 17) Hands-on / resources
    s = content_slide(prs, "Hands-On — Build It Yourself")
    add_bullets(s, 0.55, 1.35, 8.9, 1.7, [
        "8 self-contained lab notebooks — M1 through M8.",
        "Provider-agnostic: pick a backend, the code stays the same.",
        "Runnable without an instructor — revisit anytime.",
    ], size=15, gap=8)
    add_rounded(s, 0.7, 3.25, 8.6, 1.0, CARD_BG)
    bx = add_textbox(s, 0.95, 3.42, 8.1, 0.7, anchor=MSO_ANCHOR.MIDDLE)
    p = bx.text_frame.paragraphs[0]
    _set_run(p.add_run(), "Live workshop site:  ", 15, INK, bold=True)
    _set_run(p.add_run(), "monuminu.github.io/DHS-workshop26", 15, INDIGO, bold=True)
    p2 = bx.text_frame.add_paragraph()
    _set_run(p2.add_run(), "github.com/microsoft/agent-framework  ·  learn.microsoft.com/agent-framework",
             12, GRAY)

    # 18) Closing — reuse the template's "Thank You"
    # (already the last original slide; leave as-is)

    # --- re-order: move the two originals that should bookend the deck ----
    _reorder(prs)

    prs.save(OUT)
    print(f"saved {OUT} with {len(prs.slides._sldIdLst)} slides")


def _reorder(prs):
    """Originals were slides 0..3; new slides were appended after.
    Desired order: [title(0)] + [all new] + [closing(3)].
    Remove originals 1 (section) and 2 (content) — they were only templates
    to clone — and move closing(3) to the end.
    """
    sldIdLst = prs.slides._sldIdLst
    ids = list(sldIdLst)
    # ids[0]=title, ids[1]=section-template, ids[2]=content-template,
    # ids[3]=closing, ids[4:]=new content slides
    title_el = ids[0]
    section_tmpl = ids[1]
    content_tmpl = ids[2]
    closing_el = ids[3]
    new_slides = ids[4:]

    # drop the two leftover template slides
    for el in (section_tmpl, content_tmpl):
        sldIdLst.remove(el)
    # move closing to the very end
    sldIdLst.remove(closing_el)
    sldIdLst.append(closing_el)
    # (title stays first; new_slides already follow it in order)


if __name__ == "__main__":
    build()
