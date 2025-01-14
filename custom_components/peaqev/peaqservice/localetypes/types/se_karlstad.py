from homeassistant.components.utility_meter.sensor import (
    HOURLY
)

from custom_components.peaqev.peaqservice.localetypes.localtypebase import LocaleTypeBase
from custom_components.peaqev.peaqservice.util.constants import (
    QUERYTYPE_BASICMAX
)


class SE_Karlstad(LocaleTypeBase):
    def __init__(self):
        observed_peak = QUERYTYPE_BASICMAX #todo check if correct
        charged_peak = QUERYTYPE_BASICMAX #todo check if correct
        peakcycle = HOURLY
        super().__init__(
            observedpeak=observed_peak,
            chargedpeak=charged_peak,
            peakcycle=peakcycle
        )

"""
Note, high load extra is added on weekdays from 6-18 during november - march. 
This does not affect the peak, but should in future updates be cause for forced non-/or caution-hours to lessen the cost for the consumer.
"""

#https://karlstadsnat.se/elnat/kund/priser-och-tariffer/effekttariff/
