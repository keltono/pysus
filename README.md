# The Pysus Programming Language

This language is a work in progress, but as it gets further along, the intention is to have a multi-paradigm systems programming language.
Hopefully it will fall into some overlap between D/C++, rust, and maybe haskell.

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

## TODOS:

#### A quick list of things to implement (in order of intent to implement)

* chars
* strings
* ((singly) linked) lists
* A module system
* imports
* basic runtime library
	* malloc / free 
* for (each) loops
* structures / user defined types
* lambdas/closures
* first class functions
* typeclasses
* currying
