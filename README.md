# Stardew Damage Calculator
Welcome, I've written up a tool to calculate hit damage and optimize builds in Stardew Valley. If you'd like to jump straight into the data, check out any of the links below!
- [Google Drive Folder](link) // A Google Drive folder of all damage data for many popular weapons.
- [Custom Stats Calculator](link) // A Google Colab with the calculatory so that you can add/change/customize anything you want (tutorial below).

## Overview / Description
I've taken a look through the [decompiled Stardew Valley code](https://github.com/veywrn/StardewValley/tree/master) and recreated the damage calculations so that I could figure out what combination of weapon forges, rings, professions, etc. lets you hit the biggest numbers. 


## Stardew Damage Algorithm Breakdown
While researching for this project I could only find a few sources for how damage was actually calculated, mostly [[Penguinpanda's Video]](https://www.youtube.com/watch?v=_CGaLn6Etvc), [[CytheNulle's Video]](https://www.youtube.com/watch?v=upUQwXrW_kI) and [the community wiki](https://stardewvalleywiki.com), So I want to compile everything about how the game calculates damage in one place here. I'll be using the wiki's conventions for talking about methods / functions in game code, E.g. `StardewValley::Tools::MeleeWeapon.DoDamage` which is effectively the filepath so that you can find the class / functions I reference if you like.

#### Weapon Base Stats

The data for weapons and their base stats like level, min and max damage, crit rate / multiplier, etc. is stored in a file called `Weapons.xnb` [[wiki]](https://stardewvalleywiki.com/Modding:Items#Weapons). This data is loaded by `‎StardewValley::Tools::MeleeWeapon.RecalculateAppliedForges`, which will then apply bonuses to these base stats. 

Something that tripped me up when learning about this stuff for the first time was the fact that "Critical Hit Damage" is kind of fake. Each weapon has a value that I'll call "Critical Multiplier", and most weapons have this value set to 3. If this value is larger than 3, the game will give the weapon the "Crit Power" stat, with a bonus based on the formula:

`Crit. Mult. = 3 + (Crit. Power / 50)`  |  `Crit. Power = (Crit. Mult. - 3) * 50`

A good example is the Iridium Needle dagger, which has an incredible +200 Crit. Power. Using this we can plug it into the formula for Crit. Mult. and see its base Crit. Multiplier is 7. The game handles most calculations regarding the extra damage dealt by crits with the Crit Multiplier stat, so it's useful to understand how it works.

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

Emeralds increase their weapon's speed by 5 per emerald. The weapon's speed value on the tooltip (from now on "final speed") is the "true" speed value divided by 2 and typecast into an integer. The behavior described on the wiki where the first emerald adds 2 final speed, the next 3, and the third 2 is explained by this final speed calculation: 

`1 emerald = +5 true speed = +int(2.5) final speed = +2 final speed`, 

`2 emeralds = +10 true speed = +int(5) final speed = +5 final speed`,

`3 emeralds = +15 true speed = +int(7.5) final speed = +7 final speed`.

This assumes that our base weapon has 0 base speed, which is often not the case, especially for clubs which have an implicit -8 true speed modifier. Only 3 weapons to my knowledge have an odd base speed being the Galaxy Dagger, Infinity Dagger, and Dwarf Dagger all at 3. This changes the bonus speed per emerald to: 

`1 emerald = +3 final speed, 2 emeralds = +5 final speed, 3 emeralds = +8 final speed`.

These daggers already have a total attack time so low that it's impractical and probably wasteful to apply emeralds to them, but a fun thought experiment nonetheless. For more information on weapon speed see `StardewValley::Tools::MeleeWeapon` and [the wiki](https://stardewvalleywiki.com/Speed). For the purposes of this damage calculator I do not consider speed as I am currently interested in the raw damage per hit of a weapon, not the damage per second output. 
















