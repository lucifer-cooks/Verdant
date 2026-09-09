from mc.net.minecraft.game.level.block.StepSound import StepSound

class StepSoundSand(StepSound):

    def __init__(self, name, volume, pitch):
        super().__init__(name, 1.0, 1.0)

    def stepSoundDir(self):
        return 'step.gravel'
