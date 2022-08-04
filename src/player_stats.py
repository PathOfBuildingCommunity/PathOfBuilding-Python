"""
This Class if communicating between the calculation Classes and the UI Classes
"""

from qdarktheme.qtpy.QtWidgets import QHBoxLayout, QLabel, QLayout, QListWidgetItem, QWidget
from PoB_Main_Window import Ui_MainWindow
from pob_config import *
from constants import *


class PlayerStats:
    def __init__(self, _config: Config, _win: Ui_MainWindow) -> None:
        self.config = _config
        self.win = _win
        self.build = self.win.build
        self.stats = {}

        # self.AverageHit = ""
        # self.Speed = ""
        # self.HitSpeed = ""
        # self.PreEffectiveCritChance = ""
        # self.CritChance = ""
        # self.CritMultiplier = ""
        # self.TotalDPS = ""
        # self.TotalDot = ""
        # self.WithBleedDPS = ""
        # self.WithIgniteDPS = ""
        # self.WithPoisonDPS = ""
        # self.TotalDotDPS = ""
        # self.CullingDPS = ""
        # self.CombinedDPS = ""
        # self.Cooldown = ""
        # self.AreaOfEffectRadius = ""
        # self.ManaCost = ""
        # self.LifeCost = ""
        # self.ESCost = ""
        # self.RageCost = ""
        # self.ManaPercentCost = ""
        # self.LifePercentCost = ""
        # self.ManaPerSecondCost = ""
        # self.LifePerSecondCost = ""
        # self.ManaPercentPerSecondCost = ""
        # self.LifePercentPerSecondCost = ""
        # self.ESPerSecondCost = ""
        # self.ESPercentPerSecondCost = ""
        # self.Str = ""
        # self.Dex = ""
        # self.Int = ""
        # self.Omni = ""
        # self.ReqOmni = ""
        # self.Devotion = ""
        # self.TotalEHP = ""
        # self.SecondMinimalMaximumHitTaken = ""
        # self.Life = ""
        # self.Spec_LifeInc = ""
        # self.LifeUnreserved = ""
        # self.LifeUnreservedPercent = ""
        # self.LifeRegen = ""
        # self.LifeLeechGainRate = ""
        # self.Mana = ""
        # self.Spec_ManaInc = ""
        # self.ManaUnreserved = ""
        # self.ManaUnreservedPercent = ""
        # self.ManaRegen = ""
        # self.ManaLeechGainRate = ""
        # self.Ward = ""
        # self.EnergyShield = ""
        # self.Spec_EnergyShieldInc = ""
        # self.EnergyShieldRegen = ""
        # self.EnergyShieldLeechGainRate = ""
        # self.Evasion = ""
        # self.Spec_EvasionInc = ""
        # self.MeleeEvadeChance = ""
        # self.ProjectileEvadeChance = ""
        # self.Armour = ""
        # self.Spec_ArmourInc = ""
        # self.PhysicalDamageReduction = ""
        # self.EffectiveMovementSpeedMod = ""
        # self.BlockChance = ""
        # self.SpellBlockChance = ""
        # self.AttackDodgeChance = ""
        # self.SpellDodgeChance = ""
        # self.SpellSuppressionChance = ""
        # self.FireResist = ""
        # self.FireResistOverCap = ""
        # self.ColdResist = ""
        # self.ColdResistOverCap = ""
        # self.LightningResist = ""
        # self.LightningResistOverCap = ""
        # self.ChaosResist = ""
        # self.ChaosResistOverCap = ""
        # self.FullDPS = ""
        # self.PowerCharges = ""
        # self.PowerChargesMax = ""
        # self.FrenzyCharges = ""
        # self.FrenzyChargesMax = ""
        # self.EnduranceCharges = ""
        # self.EnduranceChargesMax = ""

    # def __repr__(self) -> str:
    #     return (
    #         f"Level {self.level} {self.player_class.name}" f" {self.ascendancy.value}\n"
    #         if self.ascendancy.value is not None
    #         else "\n"
    #     )

    def load(self, build):
        """
        Load internal structures from the build object
        """
        for idx, stat in enumerate(build["PlayerStat"]):
            _stat = stat["@stat"]
            _value = stat["@value"]
            self.stats[_stat] = _value
            print(f' "{stat["@stat"]}": ": ",')
            print(idx, stat["@stat"], stat["@value"])
        self.win.textedit_Statistics.clear()
        for idx in stats_list:
            _value = float(self.stats.get(idx, 0))
            if _value != 0:
                _label = stats_list[idx].get("label")
                print(idx, _label)
                _label = "{0:>24}".format(_label)
                _colour = stats_list[idx].get("colour", ColourCodes.NORMAL)
                _fmt = stats_list[idx].get("fmt")
                # if fmt is an int, force the value to be an int.
                if "d" in _fmt:
                    _value = int(self.stats.get(idx, 0))
                if _value < 0:
                    _str_value = f'<span style="color:{ColourCodes.NEGATIVE.value};">{_fmt.format(_value)}</span>'
                else:
                    _str_value = _fmt.format(_value)
                self.win.textedit_Statistics.append(f'<span style="white-space: pre; color:{_colour.value};">{_label}:</span> {_str_value}')

    def save(self):
        """
        Save internal structures back to the build object
        """
        pass


# def test() -> None:
#     stats_ui = PlayerStats()
#     print(stats_ui)
#
#
# if __name__ == "__main__":
#     test()
