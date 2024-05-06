# Stardew Damage Calculator
Welcome, I've written up a tool to calculate hit damage and optimize builds in Stardew Valley. If you'd like to jump straight into the data, check out any of the links below!
- [Google Drive Folder](https://drive.google.com/drive/folders/1ScqYYKtp3xlBXglB-zdL1vPJCRdSRu9N?usp=sharing) // A Google Drive folder of all damage data for many popular weapons.
- [Custom Stats Calculator](https://colab.research.google.com/drive/1bXk5HagE50bXV4Zv95TRcvtJTRaaKBDP?usp=sharing) // A Google Colab with the calculator so that you can add/change/customize anything you want (tutorial below).

## Overview / Description
While researching for this project I could only find a few sources for how damage was actually calculated, mostly [Penguinpanda's Video](https://www.youtube.com/watch?v=_CGaLn6Etvc), [CytheNulle's Video](https://www.youtube.com/watch?v=upUQwXrW_kI) and [the community wiki](https://stardewvalleywiki.com).

I've taken a look through the [decompiled Stardew Valley code](https://github.com/veywrn/StardewValley/tree/master) and recreated the damage calculations so that I could figure out what combination of weapon forges, rings, professions, etc. lets you hit the biggest numbers. In this calculator I am focused on the damage that a weapon does per hit, which means I do not take weapon speed into account or try to calculate damage per second. In the spreadsheets I assume the target's defense to be 0, as well as any bonus attack and luck the player might get from eating food. These assumptions are all able to be changed in the customizable calculator.

Using the calculator I am able to generate stats for a weapon's average hit damage, critical strike chance, minimum and maximum damage for crits and non-crits, and more. These damage numbers are based off of the player's rings, weapon, forges, etc. which can be searched and filtered through in the provided spreadsheets, or created custom to fit any build in the customizable calculator above.

Important to note, the decompiled code is *not* of the newest, `1.6.x` updates of the game but instead for `1.5.4`. To my knowledge, none of the current math or weapon stats are any different than they were in `1.5.x` so this data should still be relevant now. The only addition in `1.6` that is relevant are innate weapon enchants, for which I am assuming the wiki and CytheNulle's video correctly describe how they are factored into the damage formula.

## Table of Contents
#### [User Guide]()
#### [Stardew Damage Algorithm Breakdown](#stardew-damage-algorithm-breakdown-1)
- [Weapon Base Stats / Tooltips](#weapon-base-stats--tooltips)
- [Forges](#forges)
- [Dagger Crit. Chance Buff](#dagger-crit-chance-buff)
- [Rings](#rings)
- [Innate Enchantments](#innate-enchantments)
- [Scout Crit. Chance Boost](#scout-crit-chance-boost)
- [Damage and Crit. Rolls](#damage-and-crit-rolls)
- [Attack Boosts](#attack-boosts)
- [Professions](#professions)
- [Enchantments](#enchantments)
- [Finished](#finished)
#### [Meta Discussion](#meta-discussion-1)
#### [Closing Thoughts](#closing-thoughts)

## User Guide
### Browsing Google Sheets

I hope to have made these spreadheets as user-friendly as possible, but here's a quick explanation of what's in them and how I have been using them. I ran `sdv dps lite.py` on 19 different weapons including Infinity, Dragontooth, Dwarf, and Galaxy weapon families. I also included weapons the player finds in standard mine reward chests like the Obsidian Edge and Crystal Dagger for fun. The weapons are sorted into spreadsheets by type (Dagger, Sword, Club), except for the Infinity and Galaxy families. This is because they cannot have Innate Enchantments and I wanted to keep the format the same across each sheet. 

Every sheet is sorted by High to Low Avg. Hit Damage by default. To sort data further, create a filter view by selecting `Data -> Create filter view` and clicking on the horizontal green lines by each column name. I find helpful things to filter are `Free Rings` to one or two to make room for other non-damage rings and `Professions` to find a build for specific characters.

That's all for the guide so if that's all you came for feel free to start looking around! Otherwise, these are all the possible starting inputs I used to generate the spreadsheets, with some notes on what I chose to include / omit. The calculator basically takes all possible combinations of these inputs and spits out the damage stats for each which is why I want to go over them here; These are all the different rings, forges, etc. you can expect to see represented in the spreadsheets.
- __Rings__: `["Iridium","Aquamarine","Jade","Ruby","Lucky","Other"]`
  - Any game-allowed combination of these rings, assuming the player has combined rings and both ring slots available can be inputs.
  - Warrior Ring was not included as I feel you cannot expect 100% uptime on the buff unless in a very enemy dense environment. An option to enable the Warrior Ring is available in the customizable calculator.
- __Forges__: `["Aquamarine","Jade","Ruby","Other"]`
  - Any combination of these 4 forges is valid.
  - I chose not to include Emerald / Speed forges because I calculate hit damage, not damage per second. There is a section in the algorithm breakdown that discussed speed forges for those interested.
- __Weapon Enchantments__: `[]`
  - I assume that the weapon does not have a damage boosting enchant like Crusader. These Weapon Enchants *are* available in the customizable calculator.
- __Innate Enchantments__: `["Crit Power",3],["Crit Chance",3],["Attack",5],["Other",0]`
  - Any of these 4 enchantments can be inputs. They are assumed to be at their maximum level. Changing an Innate Enchant's input level is possible in the customizable calculator.
- __Professions__: `["Fighter"],["Fighter","Brute"],["Scout"],["Scout","Desperado"]`
  - Any of these 4 profession paths can be inputs. Level 10 professions that are not Brute or Desperado do not increase damage so for players with Scout and Acrobat for example, the `["Scout"]` input would accurately calculate their damage.
- __Other Options__: `extra_luck = 0, extra_atk = 0, enemy_defense = 0`
  - All extra options are set to 0 when generating the spreadsheets. These are able to be edited in the customizable calculator.

Please refer to the customizable calculator for additrional options if the premade spreadsheets feel limited.

### Using Google Colab

To avoid losing your changes when working with the calculator, please create a copy by going to `File -> Save a copy in Drive`. The calculator has a bunch of labeled sections with dropdowns to show their corresponding code block. To edit any given section, simply change the code under the `# edit here` comment. Defaults, examples and format guides are available in each section for convenience. 
Once all settings have been changed, run all cells using `Runtime -> Run all`, or `Ctrl + F9`. The custom .csv will be available under the `Files` tab on the left side of the window. These instructions are also in the calculator.

# Stardew Damage Algorithm Breakdown
I want to compile everything about how the game calculates damage in one place here. I'll be using the wiki's conventions for talking about methods / functions in game code, E.g. `StardewValley::Tools::MeleeWeapon.DoDamage` which is effectively the filepath so that you can find the class / functions I reference if you like.

## Weapon Base Stats / Tooltips

The data for weapons and their base stats like Min and Max Damage, Crit. Rate / Multiplier, etc. is stored in a file called `Weapons.xnb` [[wiki]](https://stardewvalleywiki.com/Modding:Items#Weapons). This data is loaded by functions like `‎StardewValley::Tools::MeleeWeapon.RecalculateAppliedForges`, which will then apply bonuses to these base stats. 

Something else to note is that weapon tooltips are not always an accurate or understandable reflection of a weapon's actual stats. For example: the `Crit. Power` tooltip is kind of fake. Each weapon has a value that I'll call `Crit. Multiplier`, and most weapons have this value set to `3`. If it's larger than that, the game will give the weapon a Crit. Power bonus on the tooltip, with the bonus based on the formulas:

`Crit. Mult. = 3 + (Crit. Power / 50)`  |  `Crit. Power = (Crit. Mult. - 3) * 50`

A good example is the Iridium Needle dagger, which has an incredible +200 Crit. Power. In the game data the Iridium Needle has a base Crit. Multiplier of 7, which when we plug into the formula we see gets us exactly that +200 Crit. Power on the tooltip. The game handles most calculations regarding the extra damage dealt by crits with the Crit. Multiplier stat, so it's useful to understand how it works.

In general, the game handles all weapon stats, boosts, etc. behind the scenes and then creates the tooltips afterwards. Speed and Crit. Chance (both discussed below) also have weird tooltip calculations that can be confusing, but stats like Defense and Knockback should always be accurate to the tooltip (see `StardewValley::Tools::MeleeWeapon.drawTooltip` for specifics).

So in summary, weapons have their base stats stored in `Weapons.xnb`, which the game then loads to calculate things like forged mineral buffs. The tooltips you see on a weapon are *not* directly affecting it, but are a reflection of the stats it already has.

## Forges

Each mineral that can be forged onto a weapon has its own class in the code describing its behavior. Here's a breakdown of how exactly they all affect their weapon: 
___
- Ruby - `StardewValley::RubyEnchantment`
```c#
base._ApplyTo(item);
MeleeWeapon weapon = item as MeleeWeapon;
if (weapon != null)
{
  string[] array = Game1.temporaryContent.Load<Dictionary<int, string>>("Data\\weapons")[weapon.InitialParentTileIndex].Split('/');
  int baseMin = Convert.ToInt32(array[2]);
  int baseMax = Convert.ToInt32(array[3]);
  weapon.minDamage.Value += Math.Max(1, (int)((float)baseMin * 0.1f)) * GetLevel();
  weapon.maxDamage.Value += Math.Max(1, (int)((float)baseMax * 0.1f)) * GetLevel();
}
```

The last 2 lines are the important part here: Stardew damage works only with whole numbers, or integers. Because the damage a weapon does has to be an integer, a lot of rounding happens in the calculations. This means that even though the Ruby forge *should* increase a weapon's base damage by 10%, sometimes it's a little less because of this rounding. 

Whenever a number is cast to an integer using `(int)` it drops all the decimals and does no rounding, so even `(int)3.999999 = 3`. The `Math.Max` function usually doesn't affect the result of ruby forges because by the time you've unlocked the forge, you have a pretty strong weapon where 10% of it's minimum damage is at least 1 anyway.  If you forge something like your starter sword with rubies however, this `Math.Max` will ensure that you at least get 1 bonus damage added per ruby. 
___
- Jade - `StardewValley::JadeEnchantment`
```c#
base._ApplyTo(item);
MeleeWeapon weapon = item as MeleeWeapon;
if (weapon != null)
{
  weapon.critMultiplier.Value += 0.1f * (float)GetLevel();
}
```

Jades increase their weapon's Crit Multiplier by 0.1 per jade, which is equivalent to +5 Crit. Power per jade. 
___
- Aquamarine - `StardewValley::AquamarineEnchantment`
```c#
base._ApplyTo(item);
MeleeWeapon weapon = item as MeleeWeapon;
if (weapon != null)
{
  weapon.critChance.Value += 0.046f * (float)GetLevel();
}
```

Aquamarines increase their weapon's *base* Crit. Chance addatively by +4.6%. Most weapons have a base crit chance of 2%, so even one forge is a substantial increase to a weapon's Crit. Chance. 

The tooltip for Crit. Chance on a weapon is *roughly* +1 tooltip Crit. Chance for each 1% base Crit. Chance above 2%. This is a rough estimation because of the game rounding numbers and daggers having a slightly buffed Crit. Chance in the game code (see `StardewValley::Tools::MeleeWeapon.drawTooltip`).

___
- Topaz - `StardewValley::TopazEnchantment`
```c#
base._ApplyTo(item);
MeleeWeapon weapon = item as MeleeWeapon;
if (weapon != null)
{
  weapon.addedDefense.Value += GetLevel();
}
```
Each topaz adds 1 defense level to its weapon. Each defense level makes you take 1 less damage from attacks, down to a minimum of 1 damage. Topaz do not affect the damage done by a weapon.
___
- Emerald - `StardewValley::EmeraldEnchantment`
```c#
base._ApplyTo(item);
MeleeWeapon weapon = item as MeleeWeapon;
if (weapon != null)
{
  weapon.speed.Value += 5 * GetLevel();
}
```

Emeralds increase their weapon's speed by 5 per emerald. The weapon's speed value on the tooltip (from now on "tooltip speed") is the "true" speed value divided by 2 and typecast into an integer. The behavior described on [the wiki](https://stardewvalleywiki.com/Forge#Weapon_forging) where the first emerald adds +2 tooltip speed, the second +3, and the third +2 is explained by this tooltip speed calculation: 

`1 emerald = +5 true speed = +int(2.5) tooltip speed = +2 tooltip speed`, 

`2 emeralds = +10 true speed = +int(5) tooltip speed = +5 tooltip speed`,

`3 emeralds = +15 true speed = +int(7.5) tooltip speed = +7 tooltip speed`.

This assumes that our base weapon has an even base speed, which is rarely not the case. Only 3 weapons to my knowledge have an odd base speed which would change the bonuses provided by the emerald forges, these being the Galaxy Dagger, Infinity Dagger, and Dwarf Dagger all at 3 base speed. This changes the bonus speed per emerald to:

`0 emeralds = +3 true speed = +1 tooltip speed`, 

`1 emerald = +8 true speed = +4 tooltip speed`, 

`2 emeralds = +13 true speed = +6 tooltip speed`, 

`3 emeralds = +18 true speed = +9 tooltip speed`.

These daggers already have a total attack time so low that it's impractical and probably wasteful to apply emeralds to them, but a fun thought experiment nonetheless. For more information on weapon speed see `StardewValley::Tools::MeleeWeapon` and [the wiki](https://stardewvalleywiki.com/Speed).
___
- Amethyst - `StardewValley::AmethystEnchantment`
```c#
base._ApplyTo(item);
MeleeWeapon weapon = item as MeleeWeapon;
if (weapon != null)
{
  weapon.knockback.Value += GetLevel();
}
```
Each amethyst adds 1 to the level of a weapon's knockback per forge. This translates to +10 weight on a weapon's tooltip. See [the wiki](https://stardewvalleywiki.com/Weight) for more info. Weight does not directly affect the damage done by a weapon.
___
That was a lot, so to recap:

__Ruby__ : Increase a weapon's base damage by +10% rounded down or +1, whichever is higher (per ruby forge).

__Jade__ : Increases a weapon's Crit. Multiplier by +0.1, or +5 Crit. Power (per jade forge).

__Aquamarine__ : Increases a weapon's base Crit. Chance by +4.6% (per aquamarine forge).

__Topaz__ : Increases the defense of the player by +1 (per topaz forge) while holding the weapon.

__Emerald__ : Increases the "true speed" of the weapon by +5 (per emerald forge).

__Amethyst__ : Increases the knockback of the weapon by +1 (per amethyst forge).

These changes are the first thing that happens when calculating damage done by a weapon. Forges can be thought of as modifying the base stats of the weapon they're applied to.

## Dagger Crit. Chance Buff

All daggers are given a small boost in Crit. Chance that is given by this formula from `StardewValley::Tools::MeleeWeapon.DoDamage`:

```c#
float effectiveCritChance2 = critChance;
if ((int)type == 1)
{
  effectiveCritChance2 += 0.005f;
  effectiveCritChance2 *= 1.12f;
}
```

For example, a dagger with 2% base Crit. Chance has 2.8% after the boost. This boost in Crit. Chance always occurs *after* forges are applied to a weapon, meaning it synergizes very well with the Aquamarine forges. If a dagger with base 2% Crit. Chance has 3 Aquamarine forges it will have 18.256% Crit. Chance after the boost. This boost is always given after forges are applied but before other buffs like rings and professions.

## Rings

Only a few of the game's rings will affect a weapon's damage, some of the most important being the Iridium Ring / Ruby Ring, Aquamarine Ring, Jade Ring, and Lucky Ring. With the exception of the Lucky Ring, all other mentioned rings provide a 10% boost to their respective stat. Rings stack addatively with each other, meaning wearing 2 Ruby Rings provide a 20% boost to attack.

So far we've spent practically all our time in the `StardewValley::Tools::MeleeWeapon` file, and this will be the last section where this is true. In the function `StardewValley::Tools::MeleeWeapon.DoDamage`, the function `StardewValley::GameLoction::damageMonster` is called, and is passed these parameters: 
```c#
location.damageMonster(areaOfEffect,
                      (int)((float)(int)minDamage * (1f + who.attackIncreaseModifier)),
                      (int)((float)(int)maxDamage * (1f + who.attackIncreaseModifier)),
                      isBomb: false,
                      (float)knockback * (1f + who.knockbackModifier),
                      (int)((float)(int)addedPrecision * (1f + who.weaponPrecisionModifier)),
                      effectiveCritChance2 * (1f + who.critChanceModifier),
                      (float)critMultiplier * (1f + who.critPowerModifier),
                      (int)type != 1 || !isOnSpecial, lastUser
                      )
```
The general idea is that each of the stats we care about like Min/Max Damage and Crit. Chance / Multplier are being increased by their respective `Modifier` variable. These modifiers refer to the player's equipped ring bonuses. Each specific ring's effects can be seen in the `StardewValley::Objects::Ring` file, but I will summarize here: 

- For each Ruby / Iridium Ring: `attackIncreaseModifier += 0.1`
- For each Aquamarine Ring: `critChanceModifier += 0.1`
- For each Jade Ring: `critPowerModifier += 0.1`

As an example, if you have two combined Iridium + Ruby Rings equipped, your total  `attackIncreaseModifier = 0.4`. This means that `newMinDamage = (int)(minDamage * (1 + 0.4))`, So your rings are giving you 40% more damage. The actual damage you do might be a little lower because of the integer typecasting at the very end. With respect to Crit. Chance and Crit. Multipliers, these values are stored as floats and so we don't have to worry about any rounding happening with those two. As for the rest of the variables, They do not directly affect the damage calculations so we can ignore them.

## Innate Enchantments

Because I do not have access to a decompiled version of Stardew Valley's `1.6.x` code, I cannot verify the exact way that Innate Enchantments affect damage, but by using the wiki's examples [(Crit. Chance)](https://stardewvalleywiki.com/Combat#Critical_hit_chance), 
 [(Crit. Power)](https://stardewvalleywiki.com/Crit._Power) and CytheNulle's video I believe this is the accurate way to include these Innate Enchantments into the damage calculation. 

There are four Innate Enchantments that affect damage done and they are all mutually exclusive: Slime Slayer, Crit. Power (1-3), Crit. Chance (1-3), and Attack (1-5). Attack does not affect damage until a later step, and I am unsure as to when Slime Slayer affects damage done. My best guess would be at the very end of the calculations alongside enchants like Crusader or Bug Killer. That leaves the Crit. Enchantments that can be factored in at this step. 

Crit. Chance factors in addatively with the ring bonuses above, and can be described with the formula: 

`newCritChance = critChance * (1 + critChanceModifier + 0.02*critChanceEnchantLevel)`.

Basically, every Aquamarine Ring equipped adds +10% to the multiplier and every level of the Crit. Chance Enchant adds another +2%.

Crit. Power works similarly:

`newCritMultiplier = critMultiplier * (1 + critPowerModifier + 0.5*critPowerEnchantLevel)`.

Same as last time, Every Jade Ring adds +10% to the Crit. Multiplier multiplier and each level of the Crit. Power enchant adds +50%.

## Scout Crit. Chance Boost

From now on we're working inside the `StardewValley::GameLoction::damageMonster` function, and the first order of business is to check if the player has the Scout profession:

```c#
if (who.professions.Contains(25))
{
  critChance += critChance * 0.5f;
}
```

If they do, multiply their Crit. Chance by 1.5. Nice and easy!

## Damage and Crit. Rolls

```c#
damageAmount5 = Game1.random.Next(minDamage, maxDamage + 1);
if (who != null && Game1.random.NextDouble() < (double)(critChance + (float)who.LuckLevel * (critChance / 40f)))
{
  crit = true;
  playSound("crit");
}
damageAmount5 = (crit ? ((int)((float)damageAmount5 * critMultiplier)) : damageAmount5);
```
Next up, the game rolls a damage value between the Minimum and Maximum Damage, and denotes it as `damageAmount5`. This will end up being the final value that the player hits in-game after a few more bits of code. After the damage is rolled, the game checks whether or not the hit was a Critical Strike. It factors the player's luck into the final Critical Strike Chance using this formula:

`finalCritChance = critChance * (1 + LuckLevel/40)`.

This formula multiplicatively increases the player's Crit. Chance by +2.5% per point of luck. Daily luck does not factor into `LuckLevel`, and only increases such as Lucky Rings or Luck buffs from food will matter here. After the Critical Strike roll is done the `damageAmount5` is multiplied by `critMultiplier` if the Crit. roll succeeded, otherwise it stays the same if it failed. 

## Attack Boosts
```c#
damageAmount5 = Math.Max(1, damageAmount5 + ((who != null) ? (who.attack * 3) : 0));
```
This line of code increases the damage of the player's attack by `3 * attack`. Things that can influence the player's attack include the Warrior Ring buff, other buffs from eating food, as well as the Attack Innate Enchantment.  The fact that this line of code comes right after the critical strike section can create some very strange damage outputs, well showcased in Penguinpanda's video.

## Professions

```c#
if (who != null && who.professions.Contains(24))
{
  damageAmount5 = (int)Math.Ceiling((float)damageAmount5 * 1.1f);
}
if (who != null && who.professions.Contains(26))
{
  damageAmount5 = (int)Math.Ceiling((float)damageAmount5 * 1.15f);
}
if (who != null && crit && who.professions.Contains(29))
{
  damageAmount5 = (int)((float)damageAmount5 * 2f);
}
```
Nearly there now, here the game is checking for the three damage increasing professions. The first `if` block checks for the `Fighter` profession and multiplies the player's damage by 1.1. It also rounds the number up, meaning you will do at least one more damage per hit with the profession selected. 

The next `if` block checks for the `Brute` profession and is very similar to the last check. This time it multiplies damage by 1.15, rounding up again. If you have both Fighter and Brute selected you can expect to do about 1.265 times the damage you would do without them, and in practice even a little more because of the rounding up. 

The final `if` block checks for the `Desperado` profession, and multiplies the damage by 2 if the current hit is a critical strike. 

## Enchantments
``` c#
foreach (BaseEnchantment enchantment in who.enchantments)
{
  enchantment.OnCalculateDamage(monster, this, who, ref damageAmount5);
}
```

The last thing to do is to apply weapon enchantments (not innate enchantments, save for maybe Slime Slayer) to `damageAmount5`, if applicable. The two weapon enchantments with this property are:

- Crusader - `StardewValley::CrusaderEnchantment` - Multiplies damage by 1.5 against undead and void enemies.
```c#
protected override void _OnDealDamage(Monster monster, GameLocation location, Farmer who, ref int amount)
{
  if (monster is Ghost || monster is Skeleton || monster is Mummy || monster is ShadowBrute || monster is ShadowShaman || monster is ShadowGirl || monster is ShadowGuy || monster is Shooter)
  {
    amount = (int)((float)amount * 1.5f);
  }
}
```

- Bug Killer - `StardewValley::BugKillerEnchantment` - Multiplies damage by 2 against bug enemies.
```c#
protected override void _OnDealDamage(Monster monster, GameLocation location, Farmer who, ref int amount)
{
  if (monster is Grub || monster is Fly || monster is Bug || monster is Leaper || monster is LavaCrab || monster is RockCrab)
  {
    amount = (int)((float)amount * 2f);
  }
}
```

## Finished

```#c
damageAmount5 = monster.takeDamage(damageAmount5, (int)trajectory.X, (int)trajectory.Y, isBomb, (double)addedPrecision / 10.0, who);
```
It's the end! This is where the final `damageAmount5` will be dealt to the enemy. The enemy's defense will reduce the damage done by 1 per point (here's the code for that real quick: `int actualDamage = Math.Max(1, damage - (int)resilience);`), and that's the end of our story.

# Meta Discussion

Even from just looking at the spreadsheets for a few seconds, it's very clear that the basic way to create a high damage build with practically any weapon is to forge it with Aquamarines for the generous bonus crit. chance they offer and spec. into Scout and Desperado to take advantage of the critical strikes even more. If possible, get the best Crit. Power innate enchant on your weapon as it adds a very sizable amount of Crit. Power and overall damage, especially compared to the Crit. Chance enchant. For rings it's best to stack on as many damage boosting Iridium and Ruby Rings as you can, that way the critical strikes have a higher base damage to multiply and increase. I intentionally omitted Warrior Rings from the spreadsheets however, from my testing one is just as good if not a little bit better than a Ruby or Iridium Ring *if* you can keep the buff up 100% of the time. In my opinion this is only possible in places like the dangerous mines or with monster musk, which makes it somewhat situational and probably not worth using.

That critical focused build is only applicable in the later stages of the game, after forging has been unlocked. What kinds of builds are best before this point? By filtering the spreadsheets to only show three `Other` forges, we can find the answer! It seems that for most weapons, the optimal mid-game build is wholly focused on boosting weapon damage and attack with Fighter, Brute, and Ruby/Iridium Rings.

For fun, I'll take a look at the Steel Smallsword with only 2 rings, no forges or innate enchantments or anything fancy. Again it seems like getting as much attack boosting gear as possible with Fighter is the way to go, but there is a little more diversity with ring selection this time around. Some decently optimal ring combos here are any combination of Ruby/Iridium , Jade and Aquamarine. The reason it's a little different this time is because Ruby and Iridium Rings affect damage less the lower a weapon's base attack is. This means that critical focused rings catch up in average damage increase and rival the attack boosting rings! The reason Fighter is better than Scout this early on is that it *guarentees* at least +1 bonus damage, which is huge with weapon damages this low.

In short, the way to make your combat training and progression as smooth as possible goes like this: 
- Equip any damage boosting rings as soon as you get them.
- Take Fighter at level 5 combat.
- Try to get to Ruby/Iridium Rings as soon as you get a decent base weapon like the Obsidian Edge.
- Take Brute at level 10 combat.
- Pivot to Scout + Desperado with Aquamarine forged weapon and 2 combined Iridium/Ruby Rings.

Another interesting question to ask is: What type of weapon is the best to use? Each have their own ups and downs:
- Daggers have an inherent boost to Crit. Chance, a very fast rate of attack, and a special attack which can output incredible damage. They also have low base damage and a very small hitbox, so you will likely be trading hits with enemies in combat.
- Swords are very middle of the pack with a decent base damage, decent swing speed, and defensive blocking special attack. They have a very large hitbox that even got buffed slightly in `1.6`.
- Clubs / Hammers are slow, heavy, hard-hitting weapons with a very powerful special attack. Their swing hitboxes are similar to swords, and their special attacks are *ONLY* affected by damage boosts from forges.

In my opinion, all weapon types are plenty viable for progression through the entire game. Hammers are incredible in the early game, especially considering their special attack can be repeatedly triggered during the animation. Swords are a jack-of-all-trades, good at dealing with large quantities of enemies, swinging fast enough to stunlock them into terrain, as well as having defensive capabilities. Daggers have historically been considered lacking but with their crit bonus and being able to lock enemies into their special attack, I believe they are unrivaled at single-target damage output. Unfortunately, there are few combat scenarios where this really makes daggers shine.

At the end of the day, the diversity in weapon choices just lets people choose a combat style that suits them and their build preferences. All weapons when paired with the right build will tear through even the end game combat challenges, so pick whatever feels best and have fun!

# Closing Thoughts

Realistically, there's no point or need to min-max damage this hard in a cute farming sim. *But* it was a lot of fun, and hopefully you learned something along the way. My hope is that no one will come away from seeing the calculator and feeling like they have to use the highest damage build. Enemies at the endgame have around 400 Health at the very most, and lots of the top builds in the spreadsheets double that on a crit. The best builds in the game are comically overkill for the enemies, and I hope that fact inspires you to get creative and try to cook up a fun and unique build the next time you play. This tool started as a way for me to check the stats for my own special build where I combine a Burglar and Hot Java ring together for lots of coffee drops. 

Sincerely, thank you for reading! Happy farming :)

