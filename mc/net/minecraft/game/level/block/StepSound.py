class StepSound:

    def __init__(self, name, volume, pitch):
        self.__sound = name
        self.soundVolume = volume
        self.soundPitch = pitch

    def stepSoundDir(self):
        return f'step.{self.__sound}'

    def stepSoundDirStep(self):
        return f'step.{self.__sound}'
