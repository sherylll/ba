# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import RPi.GPIO as GPIO


LED_PIN     = 20
SWITCH_PIN  = 21

# class Device(models.Model):
    # name = models.CharField(max_length=200, null = True, blank = True)

    # def __str__(self):
        # return self.name
    # class Meta:
        # abstract = True
        
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class LED(models.Model):
    """Internet 'thing' that can control GPIO on a Raspberry Pi."""
    name = models.CharField(max_length=200, null = True, blank = True)

    #id = models.AutoField(primary_key=True)

    GPIO.setup(LED_PIN, GPIO.OUT)

    def __str__(self):
        return self.name
    def set_led(self, value):
        """Set the LED to the provided value (True = on, False = off).
        """
        GPIO.output(LED_PIN, value)
        
    def read_led(self):
        return GPIO.input(20)
    
    
    class Meta:
        app_label = "devices"
        permissions = (
            ("led_on", "can turn on LED"),
            ("led_off", "can turn off LED"),
            ("led_view", "can view LED state"),
            ("nfc_feat", "nfc security feature"),
        )
        
class Switch(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=200,  null = True, blank = True)

    GPIO.setup(SWITCH_PIN, GPIO.IN)
    
    #id = models.AutoField(primary_key=True)
    def read_switch(self):
        return GPIO.input(21)
        
    class Meta:
        app_label = "devices"
        permissions = (
            ("switch_view", "can view Switch state"),
        )

# class Person(models.Model):
    # user = models.OneToOneField(User)
    # uid = models.CharField(max_length=20)
    

class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.CharField(max_length=20,  null = True)
    keys = models.CharField(max_length=100,  null = True)