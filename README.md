# Stardew Damage Calculator
Welcome, I've written up a tool to calculate hit damage and optimize builds in Stardew Valley. If you'd like to jump straight into the data, check out any of the links below!
- [Google Drive Folder](link) // A Google Drive folder of all damage data for many popular weapons.
- [Custom Stats Calculator](link) // A Google Colab with the calculator so that you can add/change/customize anything you want (tutorial below).

## Overview / Description
While researching for this project I could only find a few sources for how damage was actually calculated, mostly [Penguinpanda's Video](https://www.youtube.com/watch?v=_CGaLn6Etvc), [CytheNulle's Video](https://www.youtube.com/watch?v=upUQwXrW_kI) and [the community wiki](https://stardewvalleywiki.com).

I've taken a look through the [decompiled Stardew Valley code](https://github.com/veywrn/StardewValley/tree/master) and recreated the damage calculations so that I could figure out what combination of weapon forges, rings, professions, etc. lets you hit the biggest numbers. In this calculator I am focused on the damage that a weapon does per hit, which means I do not take weapon speed into account or try to calculate damage per second. Other player stats that I ignore are Defense and Knockback since they do not directly affect the hit damage of weapons. Defense of enemies is assumed to be 0, but I hope to update this assumption eventually.

Important to note, the decompiled code is *not* of the newest, `1.6.x` updates of the game but instead for `1.5.4`. To my knowledge, none of the math or weapon stats are any different than they were in `1.5` so this data should still be relevant now. The only addition in `1.6` that is relevant are innate weapon enchants, for which I am assuming the wiki and CytheNulle's video correctly describe how they are factored into the damage formula.

## User Guide

## Stardew Damage Algorithm Breakdown
I want to compile everything about how the game calculates damage in one place here. I'll be using the wiki's conventions for talking about methods / functions in game code, E.g. `StardewValley::Tools::MeleeWeapon.DoDamage` which is effectively the filepath so that you can find the class / functions I reference if you like.

#### Weapon Base Stats / Tooltips

The data for weapons and their base stats like level, min and max damage, crit rate / multiplier, etc. is stored in a file called `Weapons.xnb` [[wiki]](https://stardewvalleywiki.com/Modding:Items#Weapons). This data is loaded by functions like `‎StardewValley::Tools::MeleeWeapon.RecalculateAppliedForges`, which will then apply bonuses to these base stats. 

Something else to note is that weapon tooltips are not always an accurate or understandable reflection of a weapon's actual stats. For example: "Critical Hit Damage" is kind of fake. Each weapon has a value that I'll call "Critical Multiplier", and most weapons have this value set to 3. If this value is larger than 3, the game will give the weapon the "Crit Power" stat, with a bonus based on the formula:

`Crit. Mult. = 3 + (Crit. Power / 50)`  |  `Crit. Power = (Crit. Mult. - 3) * 50`

A good example is the Iridium Needle dagger, which has an incredible +200 Crit. Power. In the game data the Iridium Needle has a base Crit. Multiplier of 7, which when we plug into the formula we see gets us exactly that +200 Crit. Power on the tooltip. The game handles most calculations regarding the extra damage dealt by crits with the Crit Multiplier stat, so it's useful to understand how it works.

In general, the game handles all weapon stats, boosts, etc. behind the scenes and then creates the tooltips afterwards. Speed and Critical Chance (both discussed below) also have weird tooltip calculations that can be confusing, but stats like Defense and Knockback should always be accurate to the tooltip (see `StardewValley::Tools::MeleeWeapon.drawTooltip` for specifics).

So in summary, weapons have their base stats stored in `Weapons.xnb`, which the game then loads and changes based on a weapon's buffs. The tooltips you see on a weapon are *not* directly affecting it, but are a reflection of the buffs it already has.

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

The last 2 lines are the most important part here: because the damage a weapon does has to be an integer, a lot of rounding happens in the calculations. This means that even though the Ruby forge *should* increase a weapon's base damage by 10%, sometimes it's a little less because of this rounding. 

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
Each topaz adds 1 defense level to its weapon. Each defense level makes you take 1 less damage from attacks, down to a minimum of 1 damage. Topaz do not affect the damage done by you or your weapon.

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

Emeralds increase their weapon's speed by 5 per emerald. The weapon's speed value on the tooltip (from now on "tooltip speed") is the "true" speed value divided by 2 and typecast into an integer. The behavior described on the wiki where the first emerald adds 2 tooltip speed, the next 3, and the third 2 is explained by this tooltip speed calculation: 

`1 emerald = +5 true speed = +int(2.5) tooltip speed = +2 tooltip speed`, 

`2 emeralds = +10 true speed = +int(5) tooltip speed = +5 tooltip speed`,

`3 emeralds = +15 true speed = +int(7.5) tooltip speed = +7 tooltip speed`.

This assumes that our base weapon has 0 base speed, which is often not the case, especially for clubs which have an implicit -8 true speed modifier. Only 3 weapons to my knowledge have an odd base speed which would change the bonuses provided by the emerald forges, these being the Galaxy Dagger, Infinity Dagger, and Dwarf Dagger all at 3. This changes the bonus speed per emerald to: 

`0 emeralds = +3 true speed = +1 tooltip speed`, 

`1 emerald = +8 true speed = +4 tooltip speed`, 

`2 emeralds = +13 true speed = +6 tooltip speed`, 

`3 emeralds = +18 true speed = +9 tooltip speed`.

These daggers already have a total attack time so low that it's impractical and probably wasteful to apply emeralds to them, but a fun thought experiment nonetheless. For more information on weapon speed see `StardewValley::Tools::MeleeWeapon` and [the wiki](https://stardewvalleywiki.com/Speed). For the purposes of this damage calculator I do not consider speed as I am currently interested in the raw damage per hit of a weapon, not the damage per second output. 

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
















