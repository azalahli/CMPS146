README:
	By Myron P, Jay Parikh
The heuristic turned out to be stupid fun to implement.
Over the course of around 4 hours I made various explicit rules for the bot.
This resulted in various cycles, notably (in this order) the great:
Wood surplus!
	As life would have it, the bot enjoys punching trees, as it is by default always the best choice for it.
	It had around 200-500 wood, mostly because it had choices to choose from
Ore surplus!
	As a result of my horribly abusive weight to go mine, the bot mined. At this time, I also implemented another action-set reducing list
	and that kinda left the bot in an infinite loop mining.
	¯\_(ツ)_/¯
	Bot slave mining is hardly the worst outcome possible
	Then I had to limit the bot to have at most 3 ore;
	This follows from an intechangabiliy from the sequence mine-mine-mine-mine-smelt-smelt-smelt-smelt vs just one mine-smelt
	This allowed the bot to actually make ingots, but it kept mining ore it didn't need to, so
	ingot count + ore count should not exceed 3, because that gave nice results for the pickaxe
Ingot surplus!
	As a result of an even heftier bonus to actually melting the ore, this eventually ended with what, around 500 ingots?
	Turns out there's really no point to that, as no recipe requires more than 6 ingots, and again,
	because sequences of actions are effectively equal, there's no downside unlike a real game 
	where theoretically we would have spacial locality for certain actions
	E.g Runescape's Al-Kharid Mining + Smithing + Crafting all at one place
Cart surplus!
	This was entirely expected at this point, and to be perfectly clear, this heuristic does not allow the bot to desire
	more than one cart at a time.
	This was a design decision undertaken because of the additional overhead a change would neccessitate: It would need to also be passed
	the goal set to check for X carts.
	However, a player should not require more than one cart, and it makes the search very fast.
These factors together allowed for the creation of over 1k rails, because at the end, the bot probably only has 7 actions,
punch wood, smelt, and dig x2(coal/ore) + rails + planks/sticks
Unfortunately, I could never get the bot to actually use the axe, and thus uh, entirely prevented them from aquiring the axe.
Thankfully, due to a single piece of wood being worth a lot of sticks, this represents a marginal loss in the total algorithm.

The search itself was pretty bog-standard dijkstra, copied over mostly from P1.
The trickiest part of it was finding out which action was taken, which was eventually given its own list
the cut_copies list was to prevent it from repeatedly trying an action, which it does reasonably well
the dead_list list was also meant to prevent it from spammed, and is seperate because the dead_list needs to be avalible for when the heuteristic is called

The heuristic was designed around what I would expect to generally be the optimal path for a new minecraft entity:
Upgrade tools as fast as you can, and then everything is marginally faster, and thus better.
As it turns out, unless the goal revolves around a lot of wood, you can easily just stick to using hand-gathered wood.

Honorable mention must be given to the state representation, which was extremely hard to wrap what exactly needed to be given as a key to figure out the initial checks.
That part took us to about late Thursday to understand that we'd need to find the key from the rule before sticking that into the state.

The last modification was done to the if resulting_plan:
This turned out to be the only place that could return the real cost, because the heuristic returns extremely low values as a result of negative weights.

TL;DR:
This is very fast, and gains time mostly in wood-heavy environments.
If the player was a builder who needed 1000 planks for instance, this bot would probably try to punch down the Amazon rainforest.
All while holding a perfectly good iron axe.