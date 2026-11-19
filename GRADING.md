# How your work is marked

This page applies to all seven modules. Module 1 summarises it; this is the full version.

## What you hand in

One completed notebook per module: the `.ipynb` file, with every code cell run from top to
bottom so that its output is visible, and every **[insert response]** replaced by your answer.
Submit it the way your instructor tells you to. Before you submit, restart the kernel and
choose **Run All** once. A notebook that only works in the order you happened to run it is
the most common avoidable problem.

## The three kinds of work

| marker | what it is | how it is judged |
|---|---|---|
| `# YOUR CODE HERE` | a coding task | Not scored in points. It must be **attempted**, it must **run**, and the module's checkpoint cell must pass. Your code is the evidence for your write-ups, so if it is wrong your answers will be too. Style is not marked. |
| **[insert response]** | a write-up question | Each numbered question is scored **0, 1 or 2**. |
| *(Stretch.)* | an optional question or activity | Not scored. Feedback is given if you attempt it. |

## The 0 / 1 / 2 scale

- **2 — full credit.** Answers the question, with the mechanism, argued from your own
  notebook's output wherever numbers are involved.
- **1 — partial.** Right direction, but missing the mechanism, the numbers, or one side of a
  both-sides question.
- **0 — no credit.** Missing, restates the question, or asserts without evidence.

**A module is passed at 70% of its available points, with no coding task left unattempted.**

## Four rules that apply to every question

1. **Evidence over assertion.** A claim about data or a model must cite a number your
   notebook produced. "The model got worse" earns 1. "Precision fell from 0.83 to 0.06"
   earns 2.
2. **Predictions are marked on honesty, never on being right.** Many questions ask what you
   expected before you ran something. A wrong prediction with a sensible reason scores full
   marks. Claiming afterwards to have predicted the surprise does not.
3. **Both-sides questions need both sides.** "Argue that it is negligible, then argue that
   it matters" is not answered by one good argument.
4. **Exact figures and approximate ones are different things.** Facts about a dataset (row
   counts, duplicates, class balance) should match the notebook's text exactly; if yours
   differ, something upstream went wrong and it is worth finding. Model scores vary a little
   from machine to machine and are quoted in the text as "about" or as ranges; yours need
   only be near them. You are never marked down for a model score that drifted.

## What good answers look like

They are short. Two to five sentences is usual, and a table is welcome where one is asked
for. They use the numbers you measured, not the ones in the text. They say what the result
means for someone who has to act on it. They do not define terms the question did not ask
about.

## Using AI assistants

<!-- DRAFT POLICY written 2026-11-12; the course owner should confirm or replace this section. -->

Module 6 teaches you to use language models and to check what they tell you, so pretending
they do not exist would be odd. The rule is about whose reasoning is being marked.

- **Allowed:** asking an assistant to explain a concept, an error message or a library
  function; asking it to help you debug code you wrote.
- **Not allowed:** submitting an assistant's text as a write-up answer, or asking it to
  predict or interpret your results for you. The write-ups are the assessment, and they are
  marked on *your* reasoning about *your* numbers. An answer that does not cite your own
  output scores at most 1 under rule 1 in any case.
- **Say so.** If an assistant helped with a coding task, add a one-line comment in that
  cell saying what it helped with. This costs you nothing.

## Resubmission and questions

Ask your instructor about deadlines, resubmission and anything this page does not cover.
