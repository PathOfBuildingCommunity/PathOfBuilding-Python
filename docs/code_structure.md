# Python Object Enumeration Thoughts

[dict] All GGPK Extracted Gems { act_str, act_dex, act_int, sup_str, sup_dex, sup_str }
  -- addressable by name

[dict] All Uniques (sub-partitioned by item type)
  -- addressable by name
  -- can return applicable list based on item type

[class] Environment
    [set] Environment Configuration

[class] Build
    [ref] Tree
    [ref] Player

[class] Tree
    [str] version
    [set] All Nodes (addressable by Node ID)
    [set] Allocated Nodes (addressable by Node ID)

[class] Player
    [enum] Class Selection
    [enum] Ascendancy Selection
    [set] Stats (e.g. Str/Dex/Int, Hit/Crit, Life/Mana, Block/Spell Block/Evade/Dodge, etc.)
    [list] Skills
    [set] Item Sets
        [per slot ref] Item
    [optional set] Minions

[class] Item
    [dict] Attribute requirements
    [list] Modifiers
    [optional ref] Skill class (for skills granted by items)

[class] Skill
    [dict] Requirements (per level Str, Dex, Int)
    [list] Granted Effect reference
    [list] Supports

[class] GrantedEffect
    [str] Name
    [dict] PerLevelEffects

[class] Minion
    [ref] Player
    [set] Stats
    [ref list] Items
    [ref list] Skills
    [int] Quantity

[class] EnemyModel (e.g. Shaper, Maven)
    [str] Name
    [set] Stats (e.g. Str/Dex/Int, Hit/Crit, Life/Mana, Block/Spell Block/Evade/Dodge, etc.)

[class] Simulator
    [ref] Environment(s)
    [ref list] Build(s)
    [ref] Enemy Model(s)

[module] Analytics Module
    [func] Node Comparison
    [func] Item Comparison
    [func] Gem Comparison
    [func] Minion Comparison

[set] Saved Builds

[dict] UI API imports/exports
