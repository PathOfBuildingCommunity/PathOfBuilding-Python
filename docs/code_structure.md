# Python Object enumeration thoughts

[dict] All GGPK Extracted Gems { act_str, act_dex, act_int, sup_str, sup_dex, sup_str }
  -- addressable by name

[dict] All Uniques (sub-partitioned by item type)
  -- addressable by name
  -- can return applicable list based on item type

[class] Environment
    [dict] Environment Configuration

[class] Build
    [ref] Tree
    [ref] Player

[class] Tree
    [str] version
    [dict] All Nodes (addressable by NodeID)
    [dict] Selected Nodes (addressable by NodeID)

[class] Player
    [enum] Class Selection
    [enum] Ascendency Selection
    [dict] Stats (e.g. Str/Dex/Int, Hit/Crit, HP/MP, Block/SpellBlock/Evade/Dodge, etc.)
    [dict] Item Slots
        [per slot ref] Item
    [optional list] Minions

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
    [dict] Stats
    [ref array] Items
    [ref array] Skills
    [int] Quantity

[class] EnemyModel (e.g., Shaper, Maven)
    [dict] Stats (e.g. Str/Dex/Int, Hit/Crit, HP/MP, Block/SpellBlock/Evade/Dodge, etc.)

[class] Simulator
    [ref] Environment(s)
    [ref array] Build(s)
    [ref] Enemy Model(s)

[class] Analytics Module
    [func] Node Comparison
    [func] Item Comparison
    [func] Gem Comparison

[list] Saved Builds

[dict] UI API imports/exports

