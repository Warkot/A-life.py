#!/usr/bin/python

__author__ = "Mateusz Warkocki"
__email__ = "mateusz.warkocki@gmail.com"

try:
    import cv
except ImportError:
    try:
        import cv2.cv as cv
    except ImportError:
        print 'You need to install OpenCV for Python before running this script.'
        exit()
import timeit
from itertools import product
from random import randint
from optparse import OptionParser

m = 60
scale = 6
border = 1
delay = 50
delay_step = 50
rotation = True

p_width = 170
p_height = 246
b_height = 35
b_span = 2
font = cv.InitFont(2, 0.4, 0.5, 0, 1, cv.CV_AA)

colors = (cv.RGB(0, 0, 0),
          cv.RGB(0, 0, 255),
          cv.RGB(255, 0, 0),
          cv.RGB(0, 255, 0),
          cv.RGB(255, 255, 0),
          cv.RGB(255, 0, 255),
          cv.RGB(255, 255, 255),
          cv.RGB(0, 255, 255),
          cv.RGB(128, 128, 128),
          cv.RGB(255, 200, 200),
          cv.RGB(128, 168, 168),
          cv.RGB(64, 64, 64))

initial_state = ((0, 2, 2, 2, 2, 2, 2, 2, 2),
                 (2, 1, 7, 0, 1, 4, 0, 1, 4, 2),
                 (2, 0, 2, 2, 2, 2, 2, 2, 0, 2),
                 (2, 7, 2, 0, 0, 0, 0, 2, 1, 2),
                 (2, 1, 2, 0, 0, 0, 0, 2, 1, 2),
                 (2, 0, 2, 0, 0, 0, 0, 2, 1, 2),
                 (2, 7, 2, 0, 0, 0, 0, 2, 1, 2),
                 (2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2),
                 (2, 0, 7, 1, 0, 7, 1, 0, 7, 1, 1, 1, 1, 1, 2),
                 (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2))


def randomColors(n):
    return tuple([(0, 0, 0), ] + list((randint(0, 255), randint(0, 255), randint(0, 255)) for i in range(n - 1)))

def parseTableFile(file_name):
    info = {}
    vars_ = {}
    rules = []
    parsed_rules = {}
    
    f = open(file_name, 'r')
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if '#' in line: line = line.split('#')[0].strip()
        if ':' in line:
            info_line = line.split(':')
            try:
                info[info_line[0]] = int(info_line[1])
            except ValueError:
                info[info_line[0]] = info_line[1]
        elif line.startswith('var '):
            vars_line = line.split('=')
            vars_[vars_line[0][4:]] = tuple(vars_line[1][1:-1].split(','))
        else:
            if ',' in line:
                rules.append(tuple(line.split(',')))
            else:
                rules.append(tuple(line))
    f.close()

    for rule in rules:
        vars_in_rule = {}
        var_indices = []
        for i, state in enumerate(rule):
            try:
                int(state)
            except ValueError:
                if state not in vars_in_rule:
                    vars_in_rule[state] = [i, ]
                else:
                    vars_in_rule[state].append(i)
                var_indices.append(i)

        for prod in product(*(vars_[v] for v in vars_in_rule)):
            c_rule = list(rule)
            for i, inds in enumerate(vars_in_rule.values()):
                for ind in inds:
                    c_rule[ind] = prod[i]

            # change order from neswc:r to cnesw:r
            # (c -> center, n -> North, e -> East, s -> South, w -> West, r -> result)
            # to fix an error in ruletablerepository documentation
            if info.get('neighborhood').lower() != 'moore':
                parsed_rules[int(c_rule[1]), int(c_rule[2]),
                             int(c_rule[3]), int(c_rule[4]),
                             int(c_rule[0])] = int(c_rule[5])
            else:
                parsed_rules[int(c_rule[1]), int(c_rule[2]),
                             int(c_rule[3]), int(c_rule[4]),
                             int(c_rule[5]), int(c_rule[6]),
                             int(c_rule[7]), int(c_rule[8]),
                             int(c_rule[0])] = int(c_rule[9])
    
    return info, vars_, parsed_rules
    

def initializeLoop(m, initial_state):
    '''Returns the initial state of the loop.'''
    data_grid = [[] for i in range(m)]
    offset = int(m / 2) - int(len(initial_state) / 2)
    i = 0
    while i < m:
        if i < offset:
            data_grid[i].extend([0 for j in range(m)])
        elif i < offset + len(initial_state):
            data_grid[i].extend([0 for j in range(offset)])
            data_grid[i].extend(initial_state[i - offset])
            data_grid[i].extend([0 for j in range(m - len(initial_state[i - offset]) - offset)])
        else:
            data_grid[i].extend([0 for j in range(m)])
        i += 1
    return data_grid


def drawLoop(data, colors, image):
    '''Displays current state.'''
    cv.Set(image, cv.RGB(64, 64, 64))
    for i in range(len(data)):
        for j in range(len(data[i])):
            cv.Rectangle(image, (j * scale + border, i * scale + border),
                         ((j + 1) * scale - border, (i + 1) * scale - border),
                         colors[data[i][j]], thickness=cv.CV_FILLED, lineType=8, shift=0) 
    cv.ShowImage('The Environment', image)


def updateLoop(data, rotation, info):
    '''Produces a new state based on rules and current state.'''
    new_data_grid = []
    i = 0
    
    if info.get('neighborhood').lower() == 'moore':
        while i < len(data):
            new_data_grid.append([])
            j = 0
            while j < len(data[i]):
                
                # checking neighborhood on torus surface
                n  = data[i-1][j]                # North
                ne = data[i-1][j+1-len(data[i])] # Northeast
                e  = data[i][j+1-len(data[i])]   # East
                se = data[i+1-len(data)][j+1-len(data[i])] #Southeast
                s  = data[i+1-len(data)][j]      # South
                sw = data[i+1-len(data)][j-1]    # Soutwest
                w  = data[i][j-1]                # West
                nw = data[i-1][j-1]              # Northwest
                c  = data[i][j]                  # center
                
                # checking all possible rotations
                if (n, ne, e, se, s, sw, w, nw, c) in rules:
                    new_data_grid[i].append(rules[(n, ne, e, se, s, sw, w, nw, c)])
                elif rotation and (nw, n, ne, e, se, s, sw, w, c) in rules:
                    new_data_grid[i].append(rules[(nw, n, ne, e, se, s, sw, w, c)])
                elif rotation and (w, nw, n, ne, e, se, s, sw, c) in rules:
                    new_data_grid[i].append(rules[(w, nw, n, ne, e, se, s, sw, c)])
                elif rotation and (sw, w, nw, n, ne, e, se, s, c) in rules:
                    new_data_grid[i].append(rules[(sw, w, nw, n, ne, e, se, s, c)])
                elif rotation and (s, sw, w, nw, n, ne, e, se, c) in rules:
                    new_data_grid[i].append(rules[(s, sw, w, nw, n, ne, e, se, c)])
                elif rotation and (se, s, sw, w, nw, n, ne, e, c) in rules:
                    new_data_grid[i].append(rules[(se, s, sw, w, nw, n, ne, e, c)])
                elif rotation and (e, se, s, sw, w, nw, n, ne, c) in rules:
                    new_data_grid[i].append(rules[(e, se, s, sw, w, nw, n, ne, c)])
                elif rotation and (ne, e, se, s, sw, w, nw, n, c) in rules:
                    new_data_grid[i].append(rules[(ne, e, se, s, sw, w, nw, n, c)])
                else:
                    new_data_grid[i].append(data[i][j])
                j += 1
            i += 1
    else:
        while i < len(data):
            new_data_grid.append([])
            j = 0
            while j < len(data[i]):
                
                # checking neighborhood on torus surface
                n = data[i-1][j]                # North
                e = data[i][j+1-len(data[i])]   # East
                s = data[i+1-len(data)][j]      # South
                w = data[i][j-1]                # West
                c = data[i][j]                  # center
                
                # checking all possible rotations
                if (n, e, s, w, c) in rules:
                    new_data_grid[i].append(rules[(n, e, s, w, c)])
                elif rotation and (w, n, e, s, c) in rules:
                    new_data_grid[i].append(rules[(w, n, e, s, c)])
                elif rotation and (s, w, n, e, c) in rules:
                    new_data_grid[i].append(rules[(s, w, n, e, c)])
                elif rotation and (e, s, w, n, c) in rules:
                    new_data_grid[i].append(rules[(e, s, w, n, c)])
                else:
                    new_data_grid[i].append(data[i][j])
                j += 1
            i += 1
    
    return new_data_grid


def updatePanel(panel):
    cv.ShowImage('Control panel', panel)
    

def mouseEventHandler(event_, x, y, flags, panel):
    global running, buttons
    if event_ == 1:
        for b in buttons:
            area = b.getArea()
            if b.callback and x >= area[0][0] and x <= area[1][0] \
               and y >= area[0][1] and y <= area[1][1]:
                b.pressed = True
                b.draw(panel)
                updatePanel(panel)
                inputCallback(b.callback)
    if event_ == 4:
        for b in buttons:
            if b.pressed:
                b.pressed = False
                b.draw(panel)
                updatePanel(panel)


def inputCallback(code):
    global scale, border, delay, data_grid, colors, image
    global buttons, running, user_quit, initial_state
    
    if code == 'start/stop':
        if running:
            running = False
            for b in buttons:
                if b.callback == code:
                    b.text = 'Start (Spacebar)'
                    b.draw(panel)
        else:
            running = True
            for b in buttons:
                if b.callback == code:
                    b.text = 'Stop (Spacebar)'
                    b.draw(panel)
        updatePanel(panel)
        
    elif code == 'step':
        data_grid = updateLoop(data_grid, rotation, info)
        drawLoop(data_grid, colors, image)

    elif code == 'delay+' or code == 'delay-':
        if code == 'delay+':
            if delay == 1: delay = delay_step
            else: delay += delay_step
        elif code == 'delay-':
            delay -= delay_step
        b = buttons[3]
        if delay <= 0:
            delay = 1
            b.text = 'delay: min'
        else:
            b.text = 'delay: ' + str(delay)
        b.draw(panel)
        updatePanel(panel)
   
    elif code == 'size+' or code == 'size-':
        if code == 'size+':
            pos = len(data_grid)
            if len(data_grid) % 2 == 1: pos = 0
            for i, row in enumerate(data_grid):
                row.insert(pos, 0)
                data_grid[i] = row
            data_grid.insert(pos, [0 for i in data_grid[0]])
            image = cv.CreateMat(image.height + scale, image.width + scale, cv.CV_8UC3)
        elif code == 'size-':
            pos = -1
            if len(data_grid) % 2 == 0: pos = 0
            data_grid.pop(pos)
            for i, row in enumerate(data_grid):
                row.pop(pos)
                data_grid[i] = row
            image = cv.CreateMat(image.height - scale, image.width - scale, cv.CV_8UC3)
        drawLoop(data_grid, colors, image)
        b = buttons[6]
        b.text = 'size: ' + str(len(data_grid[0]))
        b.draw(panel)
        updatePanel(panel)
        
    elif code == 'scale+' or code == 'scale-':
        if code == 'scale+': scale += 1
        elif code == 'scale-': scale -= 1
        b = buttons[9]
        if scale <= 1:
            scale = 1
            b.text = 'scale: min'
        else:
            b.text = 'scale: ' + str(scale)
        if scale <= 3: border = 0
        else: border = 1
        b.draw(panel)
        updatePanel(panel)
        m = len(data_grid)
        image = cv.CreateMat(m * scale + border, m * scale + border, cv.CV_8UC3)
        drawLoop(data_grid, colors, image)

    elif code == 'reset':
        data_grid = initializeLoop(len(data_grid), initial_state)
        drawLoop(data_grid, colors, image)
    
    elif code == 'quit':
        running = False
        user_quit = True
        cv.DestroyAllWindows()


class Button:
    global p_width, p_height, b_height, b_span
    
    def __init__(self, text, font, row, position, width, callback):
        self.text = text
        self.font = font
        self.row = row
        self.position = position
        self.width = width
        self.callback = callback
        self.pressed = False
        self.top_left = (self.position * p_width / 100 + b_span,
                        self.row * b_height + b_span)
        self.bottom_right = ((self.position + self.width) * p_width / 100 - b_span,
                             (self.row + 1) * b_height - b_span)
        
    def __repr__(self):
        return '<Button: text = \'%s\', callback = \'%s\'>' % (self.text, self.callback)
    
    def getArea(self):
        return self.top_left, self.bottom_right
    
    def draw(self, panel):
        if self.pressed:
            bg = cv.RGB(92, 92, 92)
            tc = cv.RGB(192, 192, 192)
            b = 2
            sh = -1
        elif not self.callback:
            bg = cv.RGB(128, 128, 128)
            tc = cv.RGB(224, 224, 224)
            b = 1
            sh = -1
        else:
            bg = cv.RGB(160, 160, 160)
            tc = cv.RGB(255, 255, 255)
            b = 1
            sh = 1
        cv.Rectangle(panel, self.top_left, self.bottom_right, bg, cv.CV_FILLED, 8, 0)
        cv.Rectangle(panel, (self.top_left[0] + 1, self.top_left[1] + 1),
                     (self.bottom_right[0] - 1, self.bottom_right[1] - 1), cv.RGB(0, 0, 0), b, 8, 0)
        (t_width, t_height), bline = cv.GetTextSize(self.text, self.font)
        cv.PutText(panel, self.text,
                   (int((self.position + self.width / 2.0) * p_width / 100 - t_width / 2 + sh),
                    int((self.row + 1/2.0) * b_height + t_height / 2) + sh),
                   font, cv.RGB(0, 0, 0))
        cv.PutText(panel, self.text,
                   (int((self.position + self.width / 2.0) * p_width / 100 - t_width / 2),
                    int((self.row + 1/2.0) * b_height + t_height / 2)),
                   font, tc)


if __name__ == '__main__':
    
    op = OptionParser()
    usage = "\n%prog [options] the_file [options]\n the_file - transition function .table file to load"
    op = OptionParser(usage=usage)
    op.add_option("-i", "--initial", dest="initial_state",
                  help="load initial state from the_file",
                  metavar="the_file")
    op.add_option("-c", "--colors", dest="colors",
                  help="load colors from the_file (type random to use random colors)",
                  metavar="the_file")
    op.add_option("-m", "--matrix", dest="matrix", type="int", default=m,
                  help="set the initial size of the environment matrix to # (integer, default=%i)" % m,
                  metavar="#")
    op.add_option("-r", "--no-rotation", default=rotation,
                  action="store_false", dest="rotation",
                  help="transition rules are not rotated - even if rules .table file says there are symmetries")
    op.add_option("-v", "--verbose", default=False,
                  action="store_true", dest="verbose",
                  help="tell me what's going on")
    (options, args) = op.parse_args()
    
    if len(args) == 0:
        op.print_help()
        
    else:
        
        info, vars_, rules = parseTableFile(args[0])
        
        if options.verbose:
            for k, v in info.items():
                print k, '\t:', v
            
        if options.initial_state:
            execfile(options.initial_state)
        if options.colors == 'random' or info.get('n_states', 128) > len(colors):
            colors = randomColors(info.get('n_states', 128))
        elif options.colors:
            execfile(options.colors)
        if options.matrix:
            m = options.matrix
        if info.get('symmetries').lower() == 'none':
            rotation = False
        else:
            rotation = options.rotation
        
        data_grid = initializeLoop(m, initial_state)

        image = cv.CreateMat(m * scale + border, m * scale + border, cv.CV_8UC3)
        drawLoop(data_grid, colors, image)

        panel = cv.CreateMat(p_height, p_width, cv.CV_8UC3)
        cv.Set(panel, cv.RGB(64, 64, 64))

        buttons = (Button('Start (Spacebar)', font, 0, 0, 100, 'start/stop'),
                   Button('Step (Enter/s)', font, 1, 0, 100, 'step'),
                   Button('[-]', font, 2, 0, 23, 'delay-'),
                   Button('delay: ' + str(delay), font, 2, 23, 54, None),
                   Button('[+]', font, 2, 77, 23, 'delay+'),
                   Button('[-]', font, 3, 0, 23, 'size-'),
                   Button('size: ' + str(m), font, 3, 23, 54, None),
                   Button('[+]', font, 3, 77, 23, 'size+'),
                   Button('[-]', font, 4, 0, 23, 'scale-'),
                   Button('scale: ' + str(scale), font, 4, 23, 54, None),
                   Button('[+]', font, 4, 77, 23, 'scale+'),
                   Button('Reinitialize (Ctrl+r)', font, 5, 0, 100, 'reset'),
                   Button('Quit (Esc/q)', font, 6, 0, 100, 'quit'))
        
        for b in buttons:
            b.draw(panel)
        
        cv.ShowImage('Control panel', panel)
        cv.SetMouseCallback('Control panel', mouseEventHandler, panel)
        
        cv.MoveWindow('The Environment', 250, 50)
        cv.MoveWindow('Control panel', 50, 50)

        user_quit = False
        running = False
        time = timeit.default_timer()
        fps = 0
        fps_tmp = 0
        show_fps = False
        show_key_code = False
        
        while not user_quit:
            if show_fps and time + 1 <= timeit.default_timer():
                time = timeit.default_timer()
                if fps: print 'fps:', fps
                fps = 0
            fps += 1
            code = cv.WaitKey(delay)
            if show_key_code and code != -1: print 'key:', code

            # cheking input key code
            if code in (70, 107): # k
                if show_key_code: show_key_code = False
                else: show_key_code = True
            elif code in (75, 102): # f
                if show_fps: show_fps = False
                else:
                    fps = 0
                    show_fps = True
            elif code in (27, 1048603, 113, 1048689): # Esc or q
                inputCallback('quit')
            elif code in (18, 262258, 393298, 1310834, 1441874): # Ctrl + r
                inputCallback('reset')
            elif code in (2555904, 65363): # RigtArrow
                inputCallback('delay+')
            elif code in (2424832, 65361): # LeftArrow
                inputCallback('delay-')
            elif code in (2490368, 65362): # UpArrow
                inputCallback('size+')
            elif code in (2621440, 65364): # DownArrow
                inputCallback('size-')
            elif code in (43, 65579, 1114155, 65451, 1114027): # + or NumPad+
                inputCallback('scale+')
            elif code in (45, 1048621, 65453, 1114029): # - or NumPad-
                inputCallback('scale-')
            elif code in (13, 10, 1048586, 65407, 1113997, 115, 1048691): # Enter, NumPadEnter or s
                inputCallback('step')
            elif code in (32, 131104, 1048608, 1179680): # Spacebar or Spacebar with NumLock on
                inputCallback('start/stop')
            if running:
                data_grid = updateLoop(data_grid, rotation, info)
                drawLoop(data_grid, colors, image)
