# SG Public Transport Integration for Home Assistant

## Design

Each bus stop is represented config subentry under the API config entry. Each
available bus service is represented as a service under the bus stop subentry.
The bus service contains a sensor for each of the following information:
* Bus type - single deck, double deck
* Estimated arrival time
* Load
* Operator
