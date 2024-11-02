from vex import *

brain=Brain()

Right_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)
Right_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
right_front = Motor(Ports.PORT11, GearSetting.RATIO_18_1, True)
Right = MotorGroup(Right_motor_a, Right_motor_b)
R = MotorGroup(Right_motor_a, Right_motor_b, right_front)

Left_motor_a = Motor(Ports.PORT10, GearSetting.RATIO_6_1, True)
Left_motor_b = Motor(Ports.PORT9, GearSetting.RATIO_6_1, False)
left_front = Motor(Ports.PORT20, GearSetting.RATIO_18_1, False)
Left = MotorGroup(Left_motor_a, Left_motor_b)
L = MotorGroup(Left_motor_a, Left_motor_b, left_front)

intake = Motor(Ports.PORT18, GearSetting.RATIO_18_1, True)
controller_1 = Controller(PRIMARY)
potV2 = PotentiometerV2(brain.three_wire_port.a)
air_front = DigitalOut(brain.three_wire_port.h)
arm = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)
shoot_motor_a = Motor(Ports.PORT3, GearSetting.RATIO_36_1, False)
shoot_motor_b = Motor(Ports.PORT8, GearSetting.RATIO_36_1, True)
shoot = MotorGroup(shoot_motor_a, shoot_motor_b)
inertial = Inertial(Ports.PORT4)
air_back = DigitalOut(brain.three_wire_port.b)

# wait for rotation sensor to fully initialize
wait(30, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")

#endregion VEXcode Generated Robot Configuration

air_count = 0
speed_level = 2
n1 = 0 
n2 = 0

class Base():
    """底盘类"""
    def __init__(self,kp_move = 0.11,ks_move = 1):
        """初始化属性"""
        self.direction = 0
        self.error = 0
        self.kp_angle = 0.68
        self.ks_angle = 1
        self.kp_move = kp_move
        self.ks_move = ks_move


    def turn_angle(self,rotation_angle):
        """转向函数方法"""
        self.direction = rotation_angle 
        brain.timer.clear()
        while True:
            self.error = rotation_angle - inertial.rotation(DEGREES)
            if self.error > 0:
                self.ks_angle = abs(self.ks_angle)
            elif  self.error < 0:
                self.ks_angle = -abs(self.ks_angle)
            else:
                self.ks_angle = 0
            self.output = self.error * self.kp_angle + self.ks_angle
            if self.output > 100 :
                self.output = 100 
            L.set_velocity(self.output, PERCENT)
            R.set_velocity(-self.output, PERCENT)
            L.spin(FORWARD)
            R.spin(FORWARD)
            if abs(self.error) < 0.5:
                break
        L.stop()
        R.stop()

    def speed_up(self):
        v_up = 0
        while v_up < 100:
            L.set_velocity(v_up, PERCENT)
            R.set_velocity(v_up, PERCENT)
            L.spin(FORWARD)
            R.spin(FORWARD)
            v_up += 2
            wait(6,MSEC)

    def speed_reverse(self):
        v_up = 0
        while v_up > -100:
            L.set_velocity(v_up, PERCENT)
            R.set_velocity(v_up, PERCENT)
            L.spin(FORWARD)
            R.spin(FORWARD)
            v_up -= 2
            wait(6,MSEC)

    def move(self,code):     
        """底盘编码器方法"""  
        L.set_position(0,DEGREES)
        R.set_position(0,DEGREES)
        if code > 200:
            Base.speed_up(self)
        if code < -200:
            Base.speed_reverse(self)
        while True :
            self.error = code - Left.position(DEGREES)
            if self.error > 0 :
               self.ks_move = abs(self.ks_move)
            elif self.error < 0 :
                self.ks_move = -abs(self.ks_move)
            self.output = self.error * self.kp_move + self.ks_move

            L.set_velocity(self.output + (self.direction - inertial.rotation(DEGREES))*1, PERCENT)
            R.set_velocity(self.output - (self.direction - inertial.rotation(DEGREES)) *1, PERCENT)
            L.spin(FORWARD)
            R.spin(FORWARD)

            if abs(self.error) < 2 :
                break
            wait(5,MSEC)
        L.stop()
        R.stop()  
        self.turn_angle(self.direction)

    def time_move(self,time_v = 40,sec = 0.7):
        """底盘移动时间控制方法，单位为秒"""
        L.set_velocity(time_v, PERCENT)
        R.set_velocity(time_v, PERCENT)
        L.spin(FORWARD)
        R.spin(FORWARD)

        wait(sec, SECONDS)
        L.stop()
        R.stop()

    def direct_move(self,c):
        """底盘直接移动方式"""
        Left.set_position(0,DEGREES)
        Right.set_position(0,DEGREES)
        left_front.set_stopping(COAST)
        right_front.set_stopping(COAST)
        left_front.stop()
        right_front.stop()
        Left.set_velocity(100, PERCENT)
        Right.set_velocity(100, PERCENT)

        Left.spin_for(FORWARD,c,DEGREES,wait=False)
        Right.spin_for(FORWARD,c,DEGREES) 
        Left.stop()
        Right.stop()
        left_front.set_stopping(BRAKE)
        right_front.set_stopping(BRAKE)
        left_front.stop()
        right_front.stop()

'''
GUI
'''
class ButtonUi:
    class Button:
        def __init__(self):
            # 初始化参数
            self.index = 0
            self.xpos = 0
            self.ypos = 0
            self.width = 80
            self.height = 80
            self.color = Color.WHITE
            self.text = ''
            self.alttext = ''
            self.state = False
            self.toggle = False
            self.callback = None

        # 开关式按钮
        def set_toggle(self, toggle, text):
            self.toggle = toggle
            if text is not None:
                self.alttext = text
            else:
                self.alttext = self.text
            return self

        # 设置按钮大小
        def set_size(self, width, height):
            self.width = width
            self.height = height
            return self

        # 设置按钮颜色
        def set_color(self, color):
            self.color = color
            return self
    
    def __init__(self):
        self.brain = Brain()
        self._buttons = []
        self._enabled = True
        self.brain.screen.pressed(self._screen_press)
        self.brain.screen.released(self._screen_release)

    @staticmethod
    # 按钮查找函数
    def _find_button(b, xpos, ypos):
        if xpos < b.xpos or xpos > (b.xpos + b.width):
            return False

        if ypos < b.ypos or ypos > (b.ypos + b.height):
            return False

        return True

    # 按钮绘制函数
    def _draw_button(self, b, bHighlight):
        if bHighlight:
            self.brain.screen.draw_rectangle(
                b.xpos, b.ypos, b.width, b.height, Color(0x808080))
        else:
            self.brain.screen.draw_rectangle(
                b.xpos, b.ypos, b.width, b.height, b.color)

        self.brain.screen.draw_rectangle(
            b.xpos, b.ypos, b.width, b.height, Color.TRANSPARENT)
        self.brain.screen.set_fill_color(Color.BLACK)
        self.brain.screen.set_pen_color(Color.WHITE)
        self.brain.screen.set_font(FontType.MONO20)

        if b.toggle and b.state:
            text = b.alttext
        else:
            text = b.text
        # we need to add text width to python VM, this will do for now
        textwidth = len(text) * 10
        self.brain.screen.print_at(
            text, opaque=False, x=b.xpos + (b.width-textwidth)/2, y=b.ypos + b.height/2 + 10)

    # 多个按钮绘制
    def _draw_buttons(self):
        for b in self._buttons:
            self._draw_button(b, False)
    
    # 按钮按下检测
    def _screen_press(self):
        if not self._enabled:
            return

        xpos = self.brain.screen.x_position()
        ypos = self.brain.screen.y_position()

        for b in self._buttons:
            if self._find_button(b, xpos, ypos):
                if b.toggle is True:
                    b.state = not b.state
                else:
                    b.state = True

                self._draw_button(b, True)
                if b.callback is not None:
                    b.callback(b.index, b.state)
                return

    # 按钮抬起检测
    def _screen_release(self):
        if not self._enabled:
            return

        for b in self._buttons:
            if not b.toggle:
                if b.state:
                    b.state = False
                    if b.callback is not None:
                        b.callback(b.index, b.state)

        self._draw_buttons()

    # 添加按钮
    def add_button(self, x, y, text, callback):
        b = ButtonUi.Button()
        b.index = len(self._buttons)
        b.xpos = x
        b.ypos = y
        b.text = text
        b.callback = callback
        self._buttons.append(b)
        return b

    # 启用
    def enable(self):
        self._enabled = True

    # 禁用
    def disable(self):
        self._enabled = False

    # 显示按钮
    def display(self, bClearScreen=False):
        if bClearScreen:
            self.brain.screen.clear_screen()
        self._draw_buttons()

'''
GUI按钮检测
'''
def userTouchAction(index, state):
    if index == 0 and not state:
        pass

    if index == 1 and not state:
        pass

    if index == 2 and not state:
        auton_attack()

    if index == 3 and not state:
        pass

# GUI对象创建
ui = ButtonUi()



def pneu_toggle():
    global air_count
    """前置气动结构展开与收起"""
    air_count += 1
    if air_count % 2 == 1 :
        air_front.set(True)
    else:
        air_front.set(False)

def onevent_controller_1buttonLeft_pressed_0():
    """后置气动结构展开"""
    air_back.set(True)

def onevent_controller_1buttonRight_pressed_0():
    """后置气动结构收起"""
    air_back.set(False)

def intake_forward():
    global n1,n2
    n1 += 1
    n2 = 0
    if n1 % 2 == 1 :
        intake.spin(FORWARD)
    else:
        intake.stop()

def intake_reverse():
    global n1,n2
    n2 += 1
    n1 = 0
    if n2 % 2 == 1 :
        intake.spin(REVERSE)
    else:
        intake.stop()

def speed_level_high():
    """高速档位"""
    global speed_level
    speed_level = 2
    controller_1.screen.clear_line(3)
    controller_1.screen.set_cursor(3,1)
    controller_1.screen.print("高速挡位")

        
def speed_level_low():
    """低速档位"""
    global speed_level
    speed_level = 1       
    controller_1.screen.clear_line(3)
    controller_1.screen.set_cursor(3,1)
    controller_1.screen.print("低速挡位")

def init_1():
    """初始化"""
    global shoot_ready
    Left.set_stopping(BRAKE)
    Right.set_stopping(BRAKE)
    left_front.set_stopping(BRAKE)
    right_front.set_stopping(BRAKE)
    intake.set_stopping(BRAKE)
    shoot.set_stopping(HOLD)
    arm.set_stopping(COAST)
    air_back.set(False)
    air_front.set(False)
    shoot.set_velocity(90,PERCENT)   
    shoot.set_max_torque(100,PERCENT)
    intake.set_velocity(100,PERCENT)
    arm.set_velocity(100,PERCENT)
    inertial.calibrate()
    wait(2,SECONDS)
    shoot_ready()
    ui.add_button(50, 20, "SD_UP", userTouchAction).set_color(Color.RED)
    ui.add_button(150, 20, "SD_DOWN", userTouchAction).set_color(Color.BLUE)
    ui.add_button(250, 20, "AUTON", userTouchAction).set_color(Color.RED)
    ui.add_button(350, 20, "LOOP", userTouchAction).set_color(Color(0x208020))
    ui.display()
    controller_1.screen.set_cursor(3,1)
    controller_1.screen.print("高速挡位")    

def init_2():
    """打印与反馈线程"""
    while True:
        print("Angle:{} Code:{}".format(inertial.rotation(DEGREES),Left.position(DEGREES))) 
        brain.screen.print_at("Angle: ", inertial.rotation(DEGREES), x=150, y=150)
        brain.screen.print_at("Code: ", Left.position(DEGREES), x=150, y=175)
        wait(0.1,SECONDS)

def shoot_ready():
    """发射结构预位"""
    shoot.set_stopping(HOLD)
    while potV2.angle(PERCENT) < 22:
        shoot.spin(FORWARD)
    shoot.stop()

def driver_control():
    """遥控程序"""
    global shoot_ready,speed_level
    speed_level = 2
    xs = 1.2
    ys = 1.0
    while True :
        """变速判断"""
        if speed_level == 2 :
            xs = 1.0
            ys = 1.0
        elif speed_level == 1 :
            xs = 0.525
            ys = 0.75

        
        if controller_1.buttonL2.pressing():
            shoot.set_stopping(HOLD)
            shoot.spin(FORWARD)
        else:
            shoot.stop()

        """底盘遥控"""
        y = controller_1.axis3.position() * ys
        x = controller_1.axis1.position() * xs
        if abs(y) > 10 or abs(x) > 10 :
            Left.set_velocity( y + x , PERCENT )
            Right.set_velocity( y - x , PERCENT )
            left_front.set_velocity( y + x , PERCENT )
            right_front.set_velocity( y - x , PERCENT )
          
            Left.spin(FORWARD)
            Right.spin(FORWARD)
            left_front.spin(FORWARD)
            right_front.spin(FORWARD)
           
        else :
            Left.stop()
            Right.stop()
            left_front.stop()
            right_front.stop()
   

        """机械臂手控部分"""
        if controller_1.buttonUp.pressing():
            arm.spin(FORWARD)
        elif controller_1.buttonDown.pressing():
            arm.spin(REVERSE)
        else:
            arm.stop()


        """发射按键"""
        if controller_1.buttonL1.pressing():
            shoot.set_stopping(HOLD)
            shoot.set_timeout(0.5,SECONDS)
            shoot.spin_for(FORWARD,200,DEGREES)
            shoot.stop()
            shoot_ready()

        wait(5,MSEC)

def release(s = 0.3):
    intake.spin(REVERSE)
    wait(s,SECONDS)
    intake.stop()

def auton_attack():
    base = Base()
    intake.spin(FORWARD)
    base.direct_move(100)
    wait(50,MSEC)
    base.direct_move(-1900)
    base.turn_angle(-40)
    # ON
    pneu_toggle()
    wait(50,MSEC)
    base.direct_move(-1000)
    wait(50,MSEC)
    base.turn_angle(-70)
    wait(50,MSEC)
    base.direct_move(-1000)
    wait(50,MSEC)
    # OFF
    pneu_toggle()
    base.direct_move(680)
    base.turn_angle(100)
    intake.spin(REVERSE)
    wait(50,MSEC)
    base.move(680)
    base.turn_angle(0)
    intake.spin(FORWARD)
    base.direct_move(600)
    base.turn_angle(18)
    base.direct_move(2250)
    wait(50,MSEC)
    base.turn_angle(90)
    base.direct_move(400)
    base.turn_angle(180)
    base.direct_move(400)
    # ON
    pneu_toggle()
    wait(50,MSEC)
    base.direct_move(1400)
    intake.spin(REVERSE)
    # OFF
    pneu_toggle()
    wait(50,MSEC)
    intake.spin(FORWARD)
    base.turn_angle(19)
    base.direct_move(1600)
    base.turn_angle(180)
    base.direct_move(1800)

def auton_defense():
    base = Base()
    intake.spin(FORWARD)
    base.turn_angle(40)
    pneu_toggle()
    base.move(700)
    base.turn_angle(80)
    base.move(600)
    base.move(-800)
    pneu_toggle()
    base.direct_move(900)
    intake.spin(REVERSE)
    base.move(-600)
    wait(100,MSEC)
    # base.turn_angle(-90)
    # base.direct_move(-500)
    base.turn_angle(-135)
    base.move(1700)
    base.turn_angle(180)
    base.move(1400)
    # base.turn_angle(180)
    # base.direct_move(-500)
    # base.turn_angle(-135)
    # base.direct_move(-1400)
    
def auton_defense2():
    base = Base()
    intake.spin(FORWARD)
    base.move(-600)
    # ON
    pneu_toggle()
    base.move(600)
    base.turn_angle(-45)
    base.move(1000)
    base.direct_move(-600)
    # OFF
    pneu_toggle()
    base.turn_angle(0)
    wait(50, MSEC)
    base.turn_angle(180)
    base.direct_move(1400)
    base.turn_angle(-135)
    intake.spin(REVERSE)
    base.move(500)
    wait(50,MSEC)
    base.turn_angle(0)
    base.direct_move(1600)


    
# create a function for handling the starting and stopping of all autonomous tasks
def vexcode_auton_function():
    # Start the autonomous control tasks
    """
    在这里改自动
    """
    auton_task_0 = Thread( auton_defense2 ) # ←此处
    # wait for the driver control period to end
    while( competition.is_autonomous() and competition.is_enabled() ):
        # wait 10 milliseconds before checking again
        wait( 10, MSEC )
    # Stop the autonomous control tasks
    auton_task_0.stop()

def vexcode_driver_function():
    # Start the driver control tasks
    driver_control_task_0 = Thread( driver_control )

    # wait for the driver control period to end
    while( competition.is_driver_control() and competition.is_enabled() ):
        # wait 10 milliseconds before checking again
        wait( 10, MSEC )
    # Stop the driver control tasks
    driver_control_task_0.stop()


# register the competition functions
competition = Competition( vexcode_driver_function, vexcode_auton_function )

# system event handlers

controller_1.buttonUp.pressed(speed_level_high)
controller_1.buttonDown.pressed(speed_level_low)
# controller_1.buttonLeft.pressed(side_down)
# controller_1.buttonRight.pressed(side_up)
controller_1.buttonB.pressed(pneu_toggle)
controller_1.buttonR1.pressed(intake_forward)
controller_1.buttonR2.pressed(intake_reverse)
# controller_1.buttonA.pressed(side_toggle)
# controller_1.buttonX.pressed(side_clear)

# add 15ms delay to make sure events are registered correctly.
wait(15, MSEC)

ws2 = Thread( init_2 )
init_1()



