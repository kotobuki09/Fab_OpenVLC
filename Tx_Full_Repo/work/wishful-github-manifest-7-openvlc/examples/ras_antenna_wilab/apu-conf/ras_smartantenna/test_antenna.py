import time
import smartantenna as smartantenna

control = smartantenna.Controller()

t0 = time.time()
for cfg in range(0, 9):
  control.set_sas_conf(5, cfg, cfg, 0, 0)
  now = time.time()
  diff = now - t0
  print("%0.2f: set cfg = %d" % (diff, cfg))
  time.sleep(5)
  

# control.test_leds()

del control

exit(0)
