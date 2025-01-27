from homeassistant.components.utility_meter.sensor import (
    HOURLY
)

from custom_components.peaqev.peaqservice.localetypes.localtypebase import LocaleTypeBase
from custom_components.peaqev.peaqservice.util.constants import (
    QUERYTYPE_BASICMAX
)


class SE_Partille(LocaleTypeBase):
    def __init__(self):
        observed_peak = QUERYTYPE_BASICMAX
        charged_peak = QUERYTYPE_BASICMAX
        peakcycle = HOURLY
        super().__init__(
            observedpeak=observed_peak,
            chargedpeak=charged_peak,
            peakcycle=peakcycle
        )
