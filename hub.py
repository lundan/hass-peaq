import logging
from datetime import datetime
from custom_components.peaq.peaq.extensionmethods import Extensions as ex

from custom_components.peaq.chargecontroller import ChargeController
from custom_components.peaq.prediction import Prediction
from custom_components.peaq.threshold import Threshold

from homeassistant.helpers.event import async_track_state_change
from homeassistant.core import (
    HomeAssistant,
    callback,
)

from custom_components.peaq.peaq.locale import LocaleData
from custom_components.peaq.peaq.chargertypes import ChargerTypeData

_LOGGER = logging.getLogger(__name__)

class Hub:

    NAME = "Peaq"
    HUB_ID = 1342
    CONSUMPTION_INTEGRAL_NAME = "Energy excluding car"
    CONSUMPTION_TOTAL_NAME = "Energy including car" 

    """for getters and setters internals"""
    _currentPeaksensor = 0 #sensor
    _powersensor = 0
    _carpowersensor = 0
    _totalhourlyenergy = 0
    _PowerSensorMovingAverage = 0
    """for getters and setters internals"""

    def __init__(
        self, 
        hass: HomeAssistant, 
        configInputs: dict
        ):

        """from the config inputs"""
        self._powersensor_includes_car = configInputs["powersensorincludescar"]
        self._monthlystartpeak = configInputs["monthlystartpeak"]
        self.nonhours = configInputs["nonhours"]
        self.cautionhours = configInputs["cautionhours"]
        self.powersensorentity = self._SetPowerSensors(configInputs["powersensor"])
        """from the config inputs"""
        
        #tillfälliga
        self.Locale = configInputs["locale"]
        self.ChargerType = configInputs["chargertype"]
        #tillfälliga

        #self.currentPeaksensorentity = f"sensor.{self._name}_{self.CONSUMPTION_TOTAL_NAME}_hourly"
        self.TotalHourlyEnergy_Entity = f"sensor.{self.NAME.lower()}_{ex.NameToId(self.CONSUMPTION_TOTAL_NAME)}_hourly"
        self.PowerSensorMovingAverage_Entity = "sensor.peaq_average_consumption"

        """these should be generic and taken from chargertypes.py"""
        self.chargeamps = {}
        # self.chargeampspower = 0
        self.chargeampsswitch = {}
        """these should be generic and taken from chargertypes.py"""

        self.charging_done = False
        self.ChargerEnabled = True

        # """for getters and setters externals"""
        # self.PowerSensorMovingAverage
        # self.TotalEnergyThisHour
        # self.powersensor
        # self.carpowersensor
        # self.currentPeak
        # """for getters and setters externals"""

        """Init the subclasses"""
        self.LocaleData = LocaleData(configInputs["locale"])
        self.ChargerTypeData = ChargerTypeData(configInputs["chargertype"])
        self.TotalPowerSensor = MiniSensor("Total Power")
        self.Prediction = Prediction(self)
        self.Threshold = Threshold(self)
        self.ChargeController = ChargeController(self)
        """Init the subclasses"""

        self._ChargerEntity = self.ChargerTypeData.Charger.ChargerEntity
        self._ChargerEntity_Power = self.ChargerTypeData.Charger.PowerMeter
        self._ChargerEntity_Switch = self.ChargerTypeData.Charger.PowerSwitch

        trackerEntities = []
        trackerEntities.append(self._ChargerEntity)
        trackerEntities.append(self._ChargerEntity_Power)
        trackerEntities.append(self._ChargerEntity_Switch)

        trackerEntities.append(self.powersensorentity)
        #mock
        trackerEntities.append(self.TotalHourlyEnergy_Entity)
        trackerEntities.append(self.PowerSensorMovingAverage_Entity)
        #mock
        async_track_state_change(hass, trackerEntities, self.state_changed)


    """Moving average house powersensor"""
    @property
    def PowerSensorMovingAverage(self):
        return self._PowerSensorMovingAverage

    @PowerSensorMovingAverage.setter
    def PowerSensorMovingAverage(self, value):
        self._PowerSensorMovingAverage = int(float(value))


    """Total hourly energy"""
    @property
    def TotalEnergyThisHour(self):
        return self._totalhourlyenergy

    @TotalEnergyThisHour.setter
    def TotalEnergyThisHour(self, value):
        self._totalhourlyenergy = float(value)


    """House powersensor"""
    @property
    def powersensor(self):
        return self._powersensor

    @powersensor.setter
    def powersensor(self, value):
        self._powersensor = int(float(value))


    """Car powersensor"""
    @property
    def carpowersensor(self):
        return self._carpowersensor

    @carpowersensor.setter
    def carpowersensor(self, value):
        self._carpowersensor = int(float(value))


    """Current peak"""
    @property
    def currentPeak(self):
        return max(self._currentPeaksensor, float(self._monthlystartpeak[datetime.now().month]))

    @currentPeak.setter
    def currentPeak(self, value):
        self._currentPeaksensor = float(value)


    @callback
    async def state_changed(self, entity_id, old_state, new_state):
        if  new_state is None:
            _LOGGER.warn("State was None: ", entity_id)
            return
        try:
            if old_state.state != new_state.state:
                self._UpdateSensor(entity_id, new_state.state)
        except Exception as e:
            _LOGGER.warn("Unable to handle data: ", entity_id)
            pass


    def _SetPowerSensors(self, powerSensorName) -> str: 
        if powerSensorName.startswith("sensor."):
            return powerSensorName
        else:
            return "sensor." + powerSensorName


    def _UpdateSensor(self,entity,value):
        if entity == self.powersensorentity:
            self.powersensor = value
            self.TotalPowerSensor.State = int(float(value)) + self.carpowersensor
        elif entity == self._ChargerEntity:
            _LOGGER.warn(f"peaq-update-sensor (chargeamps sensor): {value}")
            self.chargeamps = value
        elif entity == self._ChargerEntity_Power:
            self.carpowersensor = int(float(value))
            self.TotalPowerSensor.State = int(float(value)) + self.powersensor
        elif entity == self._ChargerEntity_Switch:
            self.chargeampsswitch = value
        #elif entity == self.currentPeaksensorentity:
            #self.currentPeak = value
        elif entity == self.TotalHourlyEnergy_Entity:
            self.TotalEnergyThisHour = value
        elif entity == self.PowerSensorMovingAverage_Entity:
            self.PowerSensorMovingAverage = value


class MiniSensor: 
    
    def __init__(self, name):
        self.Name = name
        self.Id = ex.NameToId(self.Name)
        self._state = 0

    @property
    def State(self):
        return self._state

    @State.setter
    def State(self, value):
        self._state = int(float(value))