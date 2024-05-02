# Stardew Damage Calculator
Welcome, I've written up a tool to calculate hit damage and optimize builds in Stardew Valley. If you'd like to jump straight into the data, check out any of the links below!
- [Google Drive Folder](link) // A Google Drive folder of all damage data for many popular weapons.
- [Custom Stats Calculator](link) // A Google Colab with the calculatory so that you can add/change/customize anything you want (tutorial below).

## Overview / Description
I've taken a look through the [decompiled Stardew Valley code](https://github.com/veywrn/StardewValley/tree/master) and recreated the damage calculations so that I could figure out what combination of weapon forges, rings, professions, etc. lets you hit the biggest numbers. 


## Stardew Damage Algorithm Breakdown
While researching for this project I could only find a few sources for how damage was actually calculated, mostly [[Penguinpanda's Video]](https://www.youtube.com/watch?v=_CGaLn6Etvc), [[CytheNulle's Video]](https://www.youtube.com/watch?v=upUQwXrW_kI) and [the community wiki](https://stardewvalleywiki.com), So I want to compile everything about how the game calculates damage in one place here. I'll be using the wiki's conventions for talking about methods / functions in game code, E.g. `StardewValley::Tools::MeleeWeapon.DoDamage` which is effectively the filepath so that you can find the class / functions I reference if you like.

#### Weapon Base Stats

The data for weapons and their base stats like level, min and max damage, crit rate / multiplier, etc. is stored in a file called `Weapons.xnb` [[wiki]](https://stardewvalleywiki.com/Modding:Items#Weapons). This data is loaded by `‎StardewValley::Tools::MeleeWeapon.RecalculateAppliedForges`, which will then apply bonuses to these base stats. Something that tripped me up when learning about this stuff for the first time was the fact that "Critical Hit Damage" is kind of fake. Each weapon has a value that I'll call "Critical Multiplier", and most weapons have this value set to 3. If this value is larger than 3, the game will give the weapon the "Crit Power" stat, with a bonus based on the formula:

`Crit. Mult. = 3 + (Crit. Power / 50)`  |  `Crit. Power = (Crit. Mult. - 3) * 50`

A good example is the Iridium Needle dagger, which has an incredible +200 Crit. Power. Using this we can plug it into the formula for Crit. Mult. and see it's base Crit. Multiplier is 7. The game handles most calculations regarding the extra damage dealt by crits with the Crit Multiplier stat, so it's useful to understand how it works.

#### Forges

Each mineral that can be forged onto a weapon has its own class in the code describing its behavior. Here's a breakdown of how exactly they all affect their weapon: 
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
