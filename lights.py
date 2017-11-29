import cherrypy
import json
import sys
import os
import pixels
import time
from cherrypy.process.plugins import Daemonizer
from multiprocessing import Process, Pipe

color_map = {
  'white':pixels.WHITE,
  'black':pixels.BLACK,
  'red':pixels.RED,
  'orange':pixels.ORANGE,
  'yellow':pixels.YELLOW,
  'green':pixels.GREEN,
  'blue':pixels.BLUE,
  'violet':pixels.VIOLET
}

  #{"action":"rainbow","speed":"1","time":"1","reverse":"0","colors":["red","orange","yellow","green","blue","violet"]}
def rainbow(pixels, action):
  print "Rainbow ", action
  speed = int(action['speed'])
  colors = [color_map[c] for c in action['colors']]
  if int(action['reverse']): colors.reverse()
  if speed == 0: pixels.rainbow_cycle(colors, wait = 0)
  else: pixels.rainbow_cycle(colors, 0.1/speed)

  #{"action":"solid","speed":"0","time":"1","reverse":0,"colors":["orange"],"brightness":"0.75"}
def solid(pixels, action):
  print "Solid ", action
  colors = [color_map[c] for c in action['colors']]
  color = pixels.color_step(colors[0], color_map['black'], 1 - float(action['brightness']))
  pixels.solid(color)
  speed = int(action['speed'])
  if speed == 0: speed = 1
  time.sleep(5/speed)

  #{"action":"trace","speed":"2","time":"1","reverse":0,"colors":["yellow"],"tail":"5"}
def trace(pixels, action):
  print "Trace ", action
  colors = [color_map[c] for c in action['colors']]
  pixels.bounce(int(action['tail']), int(action['reverse']), colors[0], int(action['speed']))

  #{"action":"blink","speed":"1","time":"1","reverse":0,"colors":["violet"],"alternate":"1"}
def blink(pixels, action):
  print "Blink ", action
  speed = int(action['speed'])
  colors = [color_map[c] for c in action['colors']] + [color_map['black']] * int(action['alternate'])
  if int(action['reverse']): colors.reverse()
  pixels.alternating(colors)
  if speed == 0: speed = 1
  time.sleep(1/speed)
  pixels.off()
  time.sleep(0.5/speed)

  #{"action":"alternate","speed":"0","time":"1","reverse":"1","colors":["white","red","green"]}
def alternate(pixels, action):
  print "Atlernate ", action
  colors = [color_map[c] for c in action['colors']]
  if int(action['reverse']): colors.reverse()
  pixels.alternating(colors)
  speed = int(action['speed'])
  if speed == 0: speed = 1
  time.sleep(5/speed)

  # {"action":"cycle","speed":"1","time":"1","reverse":0,"colors":["red","orange","yellow","green","blue","violet"],"brightness":"0.5"}
def cycle(pixels, action):
  print "Cycle ", action
  speed = int(action['speed'])
  brightness = 1 - float(action['brightness'])
  colors = [pixels.color_step(color_map[c], color_map['black'], brightness) for c in action['colors']]
  if int(action['reverse']): colors.reverse()
  pixels.solid_cycle(colors, wait = 0.2/speed)
  
action_map = {
  'rainbow':rainbow,
  'solid':solid,
  'trace':trace,
  'blink':blink,
  'alternate':alternate,
  'cycle':cycle
}

def run_action(action, pipe):
  print "Running ", action 
  exit = 0
  p = pixels.Pixels()
  end = time.time() + float(action['time']) * 60
  infinite = float(action['time']) == 0
  while infinite or time.time() < end:
    action_map[action['action']](p, action)
    if pipe.poll(): break
  if pipe.poll(): 
    pipe.recv()
    exit = 1
  p.off()
  del p
  return exit
    
  #{"state":"0","start":"4","end":"10","actions":[]
def run_actions(actions, pipe):
  start = int(actions['start'])
  end = int(actions['end'])
  exit = 0
  aindex = 0
  alen = len(actions['actions'])
  while exit == 0:
    if start <= time.localtime().tm_hour < end:
      action = actions['actions'][aindex] 
      exit = run_action(action, pipe)
      aindex = (aindex + 1) % alen
    else: 
      time.sleep(1)
      if pipe.poll(): 
        pipe.recv()
        exit = 1
  return exit

class Lights(object):
 
  def __init__(self, fj):
    start, end = 14, 20
    state = 0
    self.actions = {'state':state,'start':start,'end':end,'actions':[]}
    self.file = None
    self.run_pipe, self.stop_pipe = Pipe()
    self.proc = None

    if isinstance(fj, file):
      self.file = fj
      jsonText = ''.join(fj.readlines())
      if len(jsonText.strip()) > 0:
        self.actions = json.loads(jsonText)
        start = int(self.actions['start'])
        end = int(self.actions['end'])
        print "Loaded ", self.actions
    
    if isinstance(fj, dict): self.actions = fj

    if start <= time.localtime().tm_hour <= end: state = 1
    self.actions['state'] = state
    if state: self.start() 
 
  @cherrypy.expose
  def lights(self, save=None):
    if save:
      self.actions = json.loads(save)
      print save
      if self.file:
        self.file.seek(0)
        self.file.truncate(0)
        self.file.write(save)
        self.file.flush()
    return json.dumps(self.actions)

  @cherrypy.expose
  def start(self):
    if self.proc is None:
      print "Starting..."
      self.proc = Process(target = run_actions, args=(self.actions, self.run_pipe))
      self.proc.start()
    return {"state":"1"}

  @cherrypy.expose
  def stop(self):
    if self.proc:
      print "Stopping..."
      self.stop_pipe.send(['STOP'])
      self.proc.join()
    self.proc = None
    return {"state":"0"}

  @cherrypy.expose
  def preview(self, preview_action=None):
    self.stop()
    if preview_action:
      action = json.loads(preview_action)
      action['time'] = "0.15"
      print "Preview ", action
      #simple sanity check
      if len(action['colors']) > 0:
        p = Process(target = run_action, args=(action, self.run_pipe))
        p.start()
        self.stop_pipe.send(['STOP'])
        p.join()
    else:
      for action in self.actions:
        p = Process(target = run_action, args=(action, self.run_pipe))
        p.start()
        self.stop_pipe.send(['STOP'])
        p.join()
    self.start()

  def test(self):
    print self.file
    print self.actions

def help(name):
  print "name [www|test|preview|run] [file|json]"
if __name__ == '__main__':
  if len(sys.argv) < 2: 
    help(sys.argv[0])
    sys.exit(0)

  fj = {}

  if len(sys.argv) > 2:
    fj = sys.argv[2]
    if fj[0] == '{': fj = json.loads(fj)
    else:
      if not os.path.isfile(fj): open(fj, 'w').close()
      fj = open(fj, 'r+')
      

  if sys.argv[1] == 'daemon':
    d = Daemonizer(cherrypy.engine)
    d.subscribe()

    cherrypy.config.update("server.conf")
    cherrypy.quickstart(Lights(fj), '/', "lights.conf")

  if sys.argv[1] == 'www':
    cherrypy.config.update("server.conf")
    cherrypy.quickstart(Lights(fj), '/', "lights.conf")

  if sys.argv[1] == 'test':
    Lights(fj).test()

  if sys.argv[1] == 'preview':
    Lights(fj).preview()

  if sys.argv[1] == 'run':
    Lights(fj).run()
