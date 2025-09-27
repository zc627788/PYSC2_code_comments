from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pysc2.maps import lib


class tss_pysc2(lib.Map):
  directory = "tss_pysc2"
  download = ""
  players = 2
  # game_steps_per_episode = 16 * 60 * 30  # 30 minute limit.
  game_steps_per_episode = 22 * 60 * 30  # 30 minute limit.


tss_pysc2_maps = [
  "sdjx_te",
  "adcc_te",
  "fkwz_te",
  "dhls_te",
  "jctq_te",
  "jdsr_te",
  "tlhz_te",
  "swct_te",
  "wwjz_te",
  "wzsy_te",
  "yqgz_te",
  "gmzz_te",
]

for name in tss_pysc2_maps:
  globals()[name] = type(name, (tss_pysc2,), dict(filename=name))
