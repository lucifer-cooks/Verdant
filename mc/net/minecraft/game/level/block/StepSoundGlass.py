from mc.net.minecraft.game.level.block.StepSound import StepSound

class StepSoundGlass(StepSound):

    def __init__(self, name, volume, pitch):
        super().__init__(name, 1.0, 1.0)

    def stepSoundDir(self):
        return 'random.glass'
