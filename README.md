[Deprecated]
Project Iterate V2 was a project that scanned Hypixel Skyblock player inventories, for rare glitched items and exotic armours.
For context there was a small community (blobtopia, oats mafia, etc) who's only aim in skyblock was to search for glitches and bugs in order to collect rare glitched items (and dupe/irl trade coins, though I never did that).

First, a database of unique player names was put together by scanning bidders, sellers, etc in the auction house API, then beginning with those players, guildmembers, friends, dungeon parties, coop members, etc (think 6 degrees of seperation) of players were crawled through, resulting in a database of 1.5m playerc names.
The inventories, enderchests, storages, wardrobes, etc of these players these players were then scanned to create a database (>60Gb) cataloging a large proportion of items on the server at the time.
I then developed a method that allowed a user to create custom declarative scripts that were ran against the database.
In coordination with 2 glitched item expert
It was then used to find:
  >40,000 exotic armour pieces
  >10 "common" snowmen pets
  3 "rare" wither skeleton pets
  1 "rare" zombie pigman pet
That being said the project is long deprecated, and the databases deleted.
