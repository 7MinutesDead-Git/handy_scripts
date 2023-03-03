# handy_scripts
Some things I've made I've found to be handy with repeated use.

## no-afk
Effective at avoiding Discord's afk timer for ending long calls prematurely (say if you like falling asleep with your partner on a call).
Interrupt at any time with CTRL-C.

## windows-git-dates-rebase
Used for generating a list of commands for amending git commit dates during a rebase, for **Windows** since Windows requires some extra commands to make this work.

This will change the commit dates of a git repo's history from the most recent commit and working backwards, to random dates within a range between two chosen dates, while ensuring reasonable waking hours are followed (with each new rebased commit date happening anywhere between 5am and 11pm).

Be careful when using this, and make sure you first test on a mock repo when modifying!
