# The Pysus Programming Language

This language is a work in progress, but as it gets further along, the intention is to have a multi-paradigm systems programming language.
Hopefully it will fall into some overlap between D/C++, rust, and maybe haskell.

# Status of this project

This project ground to a halt for a few reasons
1. school started again

    Being busy programming all day didn't leave me much time to program on things i like

2. Python became more of an issue

    A lot of this project became working around dynamic typing rather than actually writing productive code

3. I learned a lot about programming language design and type theory in the past few months

    I realized that i was basically writing rust but worse (with regaurds to trying to be as functional as possible). I also realized that it would be a good idea to start with a strong theoretical basis for typing (e.g martin-löf type theory, Hindley-Milner type system, cubical type theory, etc...) If we are going to try to be more functional than rust.

4. I realized I didn't have a plan for how to handle dynamic memory management

    Well, i did have a plan -- malloc/free -- but i soon realized that this was a bad plan if we're trying to be even remotely functional. Something like linear types/(ownership/borrowing) is a much better fit for the idea of (systems programming but functional).
    I've also been working my way through a report/dissertation by Raphaël L. Proust (https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-908.pdf) which seems promising.

5. I had some cool ideas that were incompatible with this project
    The idea of an {ML|Haskell}-like syntax for this project is very appealing. So is using a parser generator/parser combinators. Macros? meta-programming? woah.

So yeah. This project is now on indefinite hiatus. I may or may not come back to it later, but who knows!

## Why python?
One of my deepest regrets in life.

Not really, of course, but I have begun to regret python as a language choice for a few reasons. 

- Poor support for functional programming
	- I really miss my optimized tail recursion :/
- Incredibly weak/dynamic type system.
	- Types are a great way to encode parse trees properly. I've gathered something vaguely similar here, but it's a hack to make up for lack of strong typing here.
- It's slow
	- I thought it would be a good choice for a sub-ideal compiler leading into a boot strap. This is still the plan, but it was very silly of me to not realize the scope of writing any compiler. 
- No (good) llvm support
	- This one is more or less fine, since the idea here was that I would need to implement an llvm backend for the self-hosting compiler and it would be good to get my feet wet in a more familiar environment. This has held true, but has made it harder.

If i were to start this project again today, I'd probably choose OCaml or haskell (and use a half-decent parser combinator library.)

## Feature list:
- pointers
- arrays
- while loops
- if statements

## TODOS:
#### A quick list of things to implement (in order of intent to implement)

* c strings
* ((singly) linked) lists
* strings (list based)
* inline assembly
* A module system
* imports
* basic runtime library
	* malloc / free 
* for (each) loops
* structures / user defined types
* lambdas/closures
* first class functions
* typeclasses
* pattern matching
* currying
