# Stardew Damage Calculator
Welcome, I've written up a tool to calculate hit damage and optimize builds in Stardew Valley. If you'd like to jump straight into the data, check out any of the links below!
- [Google Drive Folder](link) // A Google Drive folder of all damage data for many popular weapons.
- [Custom Stats Calculator](link) // A Google Colab with the calculator so that you can add/change/customize anything you want (tutorial below).

## Overview / Description
While researching for this project I could only find a few sources for how damage was actually calculated, mostly [Penguinpanda's Video](https://www.youtube.com/watch?v=_CGaLn6Etvc), [CytheNulle's Video](https://www.youtube.com/watch?v=upUQwXrW_kI) and [the community wiki](https://stardewvalleywiki.com).

I've taken a look through the [decompiled Stardew Valley code](https://github.com/veywrn/StardewValley/tree/master) and recreated the damage calculations so that I could figure out what combination of weapon forges, rings, professions, etc. lets you hit the biggest numbers. In this calculator I am focused on the damage that a weapon does per hit, which means I do not take weapon speed into account or try to calculate damage per second. Other player stats that I ignore are Defense and Knockback since they do not directly affect the hit damage of weapons. Defense of enemies is assumed to be 0, but I hope to update this assumption eventually.

Important to note, the decompiled code is *not* of the newest, `1.6.x` updates of the game but instead for `1.5.4`. To my knowledge, none of the math or weapon stats are any different than they were in `1.5` so this data should still be relevant now. The only addition in `1.6` that is relevant are innate weapon enchants, for which I am assuming the wiki and CytheNulle's video correctly describe how they are factored into the damage formula.

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
#### [Methods](#methods)

## User Guide
### Browsing Google Sheets

### Using Google Colab

## Stardew Damage Algorithm Breakdown
I want to compile everything about how the game calculates damage in one place here. I'll be using the wiki's conventions for talking about methods / functions in game code, E.g. `StardewValley::Tools::MeleeWeapon.DoDamage` which is effectively the filepath so that you can find the class / functions I reference if you like.

#### Weapon Base Stats / Tooltips

The data for weapons and their base stats like level, min and max damage, crit rate / multiplier, etc. is stored in a file called `Weapons.xnb` [[wiki]](https://stardewvalleywiki.com/Modding:Items#Weapons). This data is loaded by functions like `‎StardewValley::Tools::MeleeWeapon.RecalculateAppliedForges`, which will then apply bonuses to these base stats. 

Something else to note is that weapon tooltips are not always an accurate or understandable reflection of a weapon's actual stats. For example: `Crit. Power` is kind of fake. Each weapon has a value that I'll call `Crit. Multiplier`, and most weapons have this value set to `3`. If it's larger than that, the game will give the weapon the Crit. Power stat, with a bonus based on the formula:

`Crit. Mult. = 3 + (Crit. Power / 50)`  |  `Crit. Power = (Crit. Mult. - 3) * 50`

A good example is the Iridium Needle dagger, which has an incredible +200 Crit. Power. In the game data the Iridium Needle has a base Crit. Multiplier of 7, which when we plug into the formula we see gets us exactly that +200 Crit. Power on the tooltip. The game handles most calculations regarding the extra damage dealt by crits with the Crit. Multiplier stat, so it's useful to understand how it works.

In general, the game handles all weapon stats, boosts, etc. behind the scenes and then creates the tooltips afterwards. Speed and Crit. Chance (both discussed below) also have weird tooltip calculations that can be confusing, but stats like Defense and Knockback should always be accurate to the tooltip (see `StardewValley::Tools::MeleeWeapon.drawTooltip` for specifics).

So in summary, weapons have their base stats stored in `Weapons.xnb`, which the game then loads to calculate things like forged mineral buffs. The tooltips you see on a weapon are *not* directly affecting it, but are a reflection of the stats it already has.

#### Forges

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

Aquamarines increase their weapon's *base* Crit. Chance addatively by 4.6%. Most weapons have a base crit chance of 2%, so even one forge is a substantial increase to a weapon's Crit. Chance. 

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

These daggers already have a total attack time so low that it's impractical and probably wasteful to apply emeralds to them, but a fun thought experiment nonetheless. For more information on weapon speed see `StardewValley::Tools::MeleeWeapon` and [the wiki](https://stardewvalleywiki.com/Speed). For the purposes of this damage calculator I do not consider speed as I am currently interested in the raw damage per hit of a weapon, not the damage per second output. 
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

As an example, if you have two combined Iridium + Ruby Rings equipped, your total  `attackIncreaseModifier = 0.4`. This means that `newMinDamage = (int)minDamage * (1 + 0.4)`, So your rings are giving you 40% more damage. The actual damage you do might be a little lower because of the integer typecasting at the very end. With respect to Crit. Chance and Crit. Multipliers, these values are stored as floats and so we don't have to worry about any rounding happening with those two. As for the rest of the variables, They do not directly affect the damage calculations so we can ignore them.

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
Next up, the game rolls a damage value between the Minimum and Maximum Damage, and denotes it as `damageAmount5`. This will end up being the final value that we can use as the actual number you hit in game after a few more bits of code. After the damage is rolled, the game checks whether or not the hit was a Critical Strike. It factors the player's luck into the final Critical Strike Chance using this formula:

`finalCritChance = critChance * (1 + LuckLevel/40)`.

This formula multiplicatively increases the player's Crit. Chance by 2.5% per point of luck. Daily luck does not factor into `LuckLevel`, and only increases such a Lucky Rings or Luck buffs from food will matter here. After the Critical Strike roll is done the `damageAmount5` is multiplied by `critMultiplier` if the Crit. roll succeeded, otherwise it stays the same if it failed. 

## Attack Boosts
```c#
damageAmount5 = Math.Max(1, damageAmount5 + ((who != null) ? (who.attack * 3) : 0));
```
This sneaky line of code increases the damage of the player's attack by `3 * attack`. Things that can influence the player's attack include the Warrior Ring buff, other buffs from eating food, as well as the Attack Innate Enchantment.  The fact that this line of code comes right after the critical strike section can create some very strange damage outputs, well showcased in Penguinpanda's video.

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
Nearly there now, here the game is checking for the three damage increasing professions. The first `if` block checks for the `Fighter` profession and multiplies the player's damage by 1.1. It also rounds the number up, meaning you will do at least one more damage per hit. 

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

# Methods

In this section I hope to give a deeper dive into how I programmed the calculator for those interested. All calculator code is written in `Python`, and I make use of the `numpy` and `pandas` packages.

# Discussion




# Closing Thoughts




