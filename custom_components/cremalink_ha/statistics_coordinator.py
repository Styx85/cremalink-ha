"""Statistics update coordinator for Cremalink."""

from __future__ import annotations

import logging
from datetime import timedelta

from cremalink import Client
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# A complete ECAM610 A2 table currently takes about 15 seconds to read.
# Lifetime counters do not need the fast 1/30-second monitor polling.
STATISTICS_UPDATE_INTERVAL = timedelta(minutes=10)


class CremalinkStatisticsCoordinator(DataUpdateCoordinator[dict]):
    """Fetch slow-changing machine statistics independently of monitoring."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        dsn: str,
        token_file: str,
    ) -> None:
        """Initialize the statistics coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_statistics",
            update_interval=STATISTICS_UPDATE_INTERVAL,
        )

        self.dsn = dsn
        self.token_file = token_file

    async def _async_update_data(self) -> dict:
        """Fetch a complete live ECAM610 statistics snapshot."""

        def _read_statistics() -> dict:
            client = Client(self.token_file)
            return client.get_ecam610_statistics(self.dsn)

        try:
            return await self.hass.async_add_executor_job(
                _read_statistics
            )
        except Exception as err:
            raise UpdateFailed(
                f"Error reading ECAM statistics: {err}"
            ) from err
