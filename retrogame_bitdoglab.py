from machine import Pin, PWM, I2C, ADC
from ssd1306 import SSD1306_I2C
import time
import random

def game_loop():
    
    SCREEN_W = 128
    SCREEN_H = 64
    BALL_DIM = int(SCREEN_W / 32)
    PADDLE_W = int(SCREEN_W / 8)
    PADDLE_H = int(SCREEN_H / 16)
    PADDLE_Y_POS = SCREEN_H - 2 * PADDLE_H
    
    adc_x = ADC(Pin(26))
    adc_y = ADC(Pin(27))
    
    def move_left():
        if (adc_x.read_u16() > 16384 and adc_y.read_u16() < 16384):
            return False
        return True
    
    def move_right():
        if (adc_x.read_u16() > 16384 and adc_y.read_u16() > 49152):
            return False
        return True
    
    def move_down():
        if (adc_x.read_u16() < 16384 and adc_y.read_u16() > 16384):
            return False
        return True
    
    def move_up():
        if (adc_x.read_u16() > 49152 and adc_y.read_u16() > 16384):
            return False
        return True
    
    btn_1 = Pin(5, Pin.IN, Pin.PULL_UP)
    btn_2 = Pin(6, Pin.IN, Pin.PULL_UP)
    
    buzzer_main = PWM(Pin(21))
    buzzer_main.freq(50)
    buzzer_aux = PWM(Pin(10))
    buzzer_aux.freq(50)
    buzzer_main.duty_u16(0)
    buzzer_aux.duty_u16(0)
    
    i2c_bus = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
    oled_display = SSD1306_I2C(SCREEN_W, SCREEN_H, i2c_bus)
    
    ball_x = 64
    ball_y = 0
    ball_vel_x = 1.0
    ball_vel_y = 1.0
    
    paddle_x = int(SCREEN_W / 2)
    paddle_vel = 6
    
    sound_tone = 400
    game_score = 0
    
    while True:
        if move_right() == 0:
            paddle_x += paddle_vel
            if paddle_x + PADDLE_W > SCREEN_W:
                paddle_x = SCREEN_W - PADDLE_W
        elif move_left() == 0:
            paddle_x -= paddle_vel
            if paddle_x < 0:
                paddle_x = 0
        
        if abs(ball_vel_x) < 1:
            ball_vel_x = 1
        
        ball_x = int(ball_x + ball_vel_x)
        ball_y = int(ball_y + ball_vel_y)
        
        collision = False
        if ball_x < 0:
            ball_x = 0
            ball_vel_x = -ball_vel_x
            collision = True
        
        if ball_x + BALL_DIM > SCREEN_W:
            ball_x = SCREEN_W - BALL_DIM
            ball_vel_x = -ball_vel_x
            collision = True
        
        if ball_y + BALL_DIM > PADDLE_Y_POS and paddle_x - BALL_DIM < ball_x < paddle_x + PADDLE_W + BALL_DIM:
            ball_vel_y = -ball_vel_y
            ball_y = PADDLE_Y_POS - BALL_DIM
            ball_vel_y -= 0.2
            ball_vel_x += (ball_x - (paddle_x + PADDLE_W / 2)) / 10
            collision = True
            game_score += 10
        
        if ball_y < 0:
            ball_y = 0
            ball_vel_y = -ball_vel_y
            collision = True
        
        if ball_y + BALL_DIM > SCREEN_H:
            oled_display.fill(0)
            oled_display.text("GAME OVER", int(SCREEN_W / 2) - int(len("Game Over!") / 2 * 8), int(SCREEN_H / 2) - 8)
            oled_display.text(str(game_score), SCREEN_W - int(len(str(game_score)) * 8), 0)
            oled_display.show()
            buzzer_main.freq(200)
            buzzer_main.duty_u16(2000)
            time.sleep(0.5)
            buzzer_main.duty_u16(0)
            while move_right() != 0 and move_left() != 0 and btn_1.value() != 0 and btn_2.value() != 0:
                time.sleep(0.001)
            break
        
        if collision:
            sound_tone = 800 if sound_tone == 400 else 400
            buzzer_main.freq(sound_tone)
            buzzer_main.duty_u16(2000)
        
        oled_display.fill(0)
        oled_display.fill_rect(paddle_x, PADDLE_Y_POS, PADDLE_W, PADDLE_H, 1)
        oled_display.fill_rect(ball_x, ball_y, BALL_DIM, BALL_DIM, 1)
        oled_display.text(str(game_score), SCREEN_W - int(len(str(game_score)) * 8), 0)
        oled_display.show()
        
        time.sleep(0.001)
        buzzer_main.duty_u16(0)
        
if __name__ == "__main__":
    game_loop()
