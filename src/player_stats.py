"""
This Class if communicating between the calculation Classes and the UI Classes
"""


from PoB_Main_Window import Ui_MainWindow
from pob_config import *
from pob_config import _VERSION


class PlayerStats:
    def __init__(self, _config: Config) -> None:
        self.pob_config = _config
        self.win = self.pob_config.win
        self.build = self.win.build

        self.AverageHit = ""
        self.Speed = ""
        self.HitSpeed = ""
        self.PreEffectiveCritChance = ""
        self.CritChance = ""
        self.CritMultiplier = ""
        self.TotalDPS = ""
        self.TotalDot = ""
        self.WithBleedDPS = ""
        self.WithIgniteDPS = ""
        self.WithPoisonDPS = ""
        self.TotalDotDPS = ""
        self.CullingDPS = ""
        self.CombinedDPS = ""
        self.Cooldown = ""
        self.AreaOfEffectRadius = ""
        self.ManaCost = ""
        self.LifeCost = ""
        self.ESCost = ""
        self.RageCost = ""
        self.ManaPercentCost = ""
        self.LifePercentCost = ""
        self.ManaPerSecondCost = ""
        self.LifePerSecondCost = ""
        self.ManaPercentPerSecondCost = ""
        self.LifePercentPerSecondCost = ""
        self.ESPerSecondCost = ""
        self.ESPercentPerSecondCost = ""
        self.Str = ""
        self.Dex = ""
        self.Int = ""
        self.Omni = ""
        self.ReqOmni = ""
        self.Devotion = ""
        self.TotalEHP = ""
        self.SecondMinimalMaximumHitTaken = ""
        self.Life = ""
        self.Spec: LifeInc = ""
        self.LifeUnreserved = ""
        self.LifeUnreservedPercent = ""
        self.LifeRegen = ""
        self.LifeLeechGainRate = ""
        self.Mana = ""
        self.Spec: ManaInc = ""
        self.ManaUnreserved = ""
        self.ManaUnreservedPercent = ""
        self.ManaRegen = ""
        self.ManaLeechGainRate = ""
        self.Ward = ""
        self.EnergyShield = ""
        self.Spec: EnergyShieldInc = ""
        self.EnergyShieldRegen = ""
        self.EnergyShieldLeechGainRate = ""
        self.Evasion = ""
        self.Spec: EvasionInc = ""
        self.MeleeEvadeChance = ""
        self.ProjectileEvadeChance = ""
        self.Armour = ""
        self.Spec: ArmourInc = ""
        self.PhysicalDamageReduction = ""
        self.EffectiveMovementSpeedMod = ""
        self.BlockChance = ""
        self.SpellBlockChance = ""
        self.AttackDodgeChance = ""
        self.SpellDodgeChance = ""
        self.SpellSuppressionChance = ""
        self.FireResist = ""
        self.FireResistOverCap = ""
        self.ColdResist = ""
        self.ColdResistOverCap = ""
        self.LightningResist = ""
        self.LightningResistOverCap = ""
        self.ChaosResist = ""
        self.ChaosResistOverCap = ""
        self.FullDPS = ""
        self.PowerCharges = ""
        self.PowerChargesMax = ""
        self.FrenzyCharges = ""
        self.FrenzyChargesMax = ""
        self.EnduranceCharges = ""
        self.EnduranceChargesMax = ""

    def __repr__(self) -> str:
        return (
            f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
            if self.ascendancy.value is not None
            else "\n"
        )

    def load(self):
        """
        Load internal structures from the build object
        """
        pass

    def save(self):
        """
        Save internal structures back to the build object
        """
        pass


def test() -> None:
    stats_ui = PlayerStats()
    print(stats_ui)


if __name__ == "__main__":
    test()
