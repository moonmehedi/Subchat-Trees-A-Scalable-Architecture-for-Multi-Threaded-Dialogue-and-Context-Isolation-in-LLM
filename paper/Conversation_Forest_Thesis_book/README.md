# Conversation Forest Thesis Book

This folder is an isolated thesis-book conversion of `paper/Conversation_Forest/sn-article.tex`, organized using the institutional structure from `paper/Thesis_Book_Template`.

## Build

```bash
latexmk -pdf -outdir=out 00thesis.tex
```

Or run:

```bash
pdflatex -output-directory=out 00thesis.tex
bibtex out/00thesis
pdflatex -output-directory=out 00thesis.tex
pdflatex -output-directory=out 00thesis.tex
```

## Required personal details

Before submission, replace the placeholders in `parameters/students.txt`, `parameters/student_list.txt`, `parameters/supervisor.txt`, and `parameters/thesisdate.txt`. The Bangla abstract is also intentionally left as a placeholder pending final review.

Journal-derived prose was transferred without grammar or style rewriting. Structural LaTeX commands were adapted for the report-based thesis template.
