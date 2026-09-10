
import os, sys, time, cProfile, pstats, io
import mc.net.minecraft.client.Minecraft as _mc_mod

_ORIG_ON_DRAW = _mc_mod.Minecraft.on_draw
_PROFILE_FRAMES = 300
_frame_count = [0]
_profiler = cProfile.Profile()
_frame_times = []
_last_frame_t = [None]

def _profiled_on_draw(self):
    now = time.perf_counter()
    if _last_frame_t[0] is not None:
        _frame_times.append(now - _last_frame_t[0])
    _last_frame_t[0] = now
    if _frame_count[0] < _PROFILE_FRAMES:
        _profiler.enable()
        _ORIG_ON_DRAW(self)
        _profiler.disable()
        _frame_count[0] += 1
        if _frame_count[0] == _PROFILE_FRAMES:
            _dump_results()
    else:
        _ORIG_ON_DRAW(self)

def _dump_results():
    sep = '=' * 70
    print()
    print(sep)
    print('  VERDANT PROFILER -- %d frames captured' % _PROFILE_FRAMES)
    print(sep)
    if _frame_times:
        ft_ms = [t * 1000 for t in _frame_times]
        ft_sorted = sorted(ft_ms)
        n = len(ft_sorted)
        avg = sum(ft_ms) / n
        avg_fps = 1000.0 / avg if avg else 0
        p1_low = ft_sorted[max(0, int(n * 0.99) - 1):]
        p1_avg = sum(p1_low) / len(p1_low)
        p1_fps = 1000.0 / p1_avg if p1_avg else 0
        print('  Frame times (%d samples):' % n)
        print('    Avg  : %.2f ms  (%.1f FPS)' % (avg, avg_fps))
        print('    Min  : %.2f ms' % ft_sorted[0])
        print('    Max  : %.2f ms' % ft_sorted[-1])
        print('    p50  : %.2f ms' % ft_sorted[n // 2])
        print('    p95  : %.2f ms' % ft_sorted[int(n * 0.95)])
        print('    1pct_low : %.2f ms  (%.1f FPS)' % (p1_avg, p1_fps))
    print()
    print('  TOP 40 HOTSPOTS (cumulative time):')
    s = io.StringIO()
    pstats.Stats(_profiler, stream=s).sort_stats('cumulative').print_stats(40)
    print(s.getvalue())
    print('  TOP 40 HOTSPOTS (total self time):')
    s2 = io.StringIO()
    pstats.Stats(_profiler, stream=s2).sort_stats('tottime').print_stats(40)
    print(s2.getvalue())
    _profiler.dump_stats('verdant_profile.prof')
    print('  Profile saved to verdant_profile.prof')
    print(sep)

_mc_mod.Minecraft.on_draw = _profiled_on_draw

from mc.net.minecraft.client.Minecraft import Minecraft
mc_instance = Minecraft(fullscreen=False, creative=False, width=854, height=480, caption='VERDANT')
mc_instance.run()
