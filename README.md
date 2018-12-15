# Procedural Generation of Peg Solitaire Games Using ASP

## Purpose
<Hypothesis goes here>

## Implementation Details
Unity, C#, ASP, Python

## Shapes Provided
Square, Square with "ears", Rectangle, Cross, H/I shape, Corner Removal, Random (All of the aforementioned shapes)

## Text File Short Explanations
usable\_boards\_easy.txt is board games on the easiest difficulty, but variability set to hard

usable\_boards\_easier.txt is board games on the easiest difficulty and variability set to easy

usable\_boards.txt is board games on the second lowest difficulty and variability set to hard

easy\_medium\_hard.txt contains three boards that are solvable in 2.154, 11.152, and 24.191 seconds

## User Study Command Line
('record' will write the order of the boards' difficulties to an alternate text file; omit 'record' if recording is not desired)

python3 peg_solitaire_game.py easy_medium_hard.txt record
