#!/usr/bin/env python3
"""Tests for latex_to_html, the converter in generate_site.py.

Project descriptions in data/projects.yaml are pasted from LaTeX and Quarto
paper sources, so they arrive carrying LaTeX markup. The template renders the
description with |safe, so anything the converter leaves alone reaches the page
verbatim: before this converter existed, projects.html showed readers a literal
"\\emph{where}" and a literal "$\\alpha$".

Two rules the tests below encode.

First, convert the constructs we recognize and leave everything else exactly as
written. Silently deleting a command we do not understand would hide the
omission; leaving it visible on the page reports it.

Second, choose the HTML element by what the LaTeX means, because a screen
reader may announce the difference. An author writes \\emph{} to stress a word,
so that becomes <em>, which carries stress emphasis. An author writes \\textit{}
and sets math in italic for typographic convention, not stress, so those become
<i>, which a screen reader passes over silently. Wrapping a variable name in
<em> would have a screen reader announce emphasis on every symbol.

Run with: uv run python tests/test_latex_to_html.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_site import latex_to_html


def check(source, expected):
    actual = latex_to_html(source)
    assert actual == expected, (
        '\n  input:    %r\n  expected: %r\n  actual:   %r' % (source, expected, actual)
    )


# --- The five instances that are actually in data/projects.yaml today. -------
# Each is quoted from the "Detecting Where Effects Occur" description except
# $d^2$, which is from the RItools entry under software.

check(
    r'the natural question from a policy maker is: \emph{where} did effects occur?',
    'the natural question from a policy maker is: <em>where</em> did effects occur?',
)

# Braced argument containing a space.
check(
    r'an \emph{error load} that summarizes how rejection probability accumulates',
    'an <em>error load</em> that summarizes how rejection probability accumulates',
)

check(
    r'controls the FWER in the \emph{strong} sense',
    'controls the FWER in the <em>strong</em> sense',
)

# Math sets variables in italic by convention rather than for stress, so the
# converted span is wrapped in <i>, not <em>. The Greek letter becomes a named
# HTML entity rather than a unicode character, which keeps both this file and
# the generated HTML in ASCII while a browser still shows the letter.
check(
    r'We develop an adaptive $\alpha$-schedule for that regime',
    'We develop an adaptive <i>&alpha;</i>-schedule for that regime',
)

check(
    r'It implements the $d^2$ test for omnibus tests',
    'It implements the <i>d<sup>2</sup></i> test for omnibus tests',
)


# --- The rest of the recognized subset. --------------------------------------

check(r'\emph{stress}', '<em>stress</em>')
check(r'\textit{convention}', '<i>convention</i>')
check(r'\textbf{importance}', '<strong>importance</strong>')
check(r'$\beta$ and $\theta$', '<i>&beta;</i> and <i>&theta;</i>')
check(r'$\alpha_i$', '<i>&alpha;<sub>i</sub></i>')
check(r'$d^{ij}$', '<i>d<sup>ij</sup></i>')
check(r'$Y_{i}$', '<i>Y<sub>i</sub></i>')

# Nested commands convert from the inside out.
check(
    r'\emph{nested \textbf{markup}}',
    '<em>nested <strong>markup</strong></em>',
)


# --- Anything unrecognized survives unchanged. -------------------------------

# A command the converter does not know stays visible, so that a reader (and
# Jake) can see it needs handling rather than finding text quietly gone.
check(r'\citep{bowers2026}', r'\citep{bowers2026}')
check(r'$\aleph$', r'$\aleph$')

# Math beyond one symbol with a sub- or superscript is left as written rather
# than converted badly.
check(r'$\sum_{i=1}^n Y_i$', r'$\sum_{i=1}^n Y_i$')
check(r'$H(y_z, w) = y_z$', r'$H(y_z, w) = y_z$')
check(r'$d^2^3$', r'$d^2^3$')

# Dollar signs in prose are not math. Without this guard the pair of dollar
# signs below would be read as a math span and the money would be mangled.
check(
    'a grant of $20,000 and a second of $5,000',
    'a grant of $20,000 and a second of $5,000',
)

# Text with no markup at all comes back untouched.
check(
    'Joint work with Nuole Chen and David Kim.',
    'Joint work with Nuole Chen and David Kim.',
)
check('', '')


# --- One whole sentence, end to end. -----------------------------------------

check(
    r'Whether the procedure also controls the FWER in the \emph{strong} sense '
    r'depends on a single quantity --- an \emph{error load} --- and we develop '
    r'an adaptive $\alpha$-schedule for that regime.',
    'Whether the procedure also controls the FWER in the <em>strong</em> sense '
    'depends on a single quantity --- an <em>error load</em> --- and we develop '
    'an adaptive <i>&alpha;</i>-schedule for that regime.',
)


print('All latex_to_html tests passed.')
