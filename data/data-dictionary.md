# ZoroLogistics Data Dictionary

| table | column | dtype | meaning |
|---|---|---|---|
| carriers | carrier_id | object | Primary key; e.g. C001..C020 |
| carriers | carrier_name | object | Display name (Atlas Freight, BlueHarbor, ...) |
| carriers | region | object | Operating region: North/South/East/West/Central |
| carriers | on_time_rate | float64 | Reliability 0.60-0.99; drives lateness probability |
| carriers | base_rate_usd_per_km_ton | float64 | USD per km per ton, 0.6-2.6 |
| carriers | fleet_size | int64 | Number of vehicles, 50-4000 |
| lanes | lane_id | object | Primary key; e.g. L001..L020 |
| lanes | origin | object | Origin city |
| lanes | destination | object | Destination city |
| lanes | distance_km | float64 | Route distance; has planted NaNs (Week 2 finds them) |
| lanes | avg_transit_days | float64 | Expected transit in days |
| lanes | toll_km | int64 | Kilometers of toll road on the lane |
| lanes | port_region | object | Nearest port |
| shipments | shipment_id | object | Primary key; S0000001.. |
| shipments | carrier_id | object | FK -> carriers.carrier_id |
| shipments | lane_id | object | FK -> lanes.lane_id |
| shipments | commodity | object | Cargo type (electronics, apparel, ...) |
| shipments | weight_kg | float64 | Weight; has planted NaNs |
| shipments | value_usd | float64 | Declared value |
| shipments | planned_departure | datetime64[ns] | Scheduled pickup |
| shipments | planned_arrival | datetime64[ns] | Promised delivery |
| shipments | actual_arrival | datetime64[ns] | Real delivery |
| shipments | delay_hours | float64 | actual minus planned in hours; the Week 3-4 target |
| shipments | is_on_time | bool | delay_hours <= 2.0 grace window |
| shipments | status | object | Delivered / In Transit / Booked |
| shipments | weather_severity | object | clear/light/moderate/severe at dispatch |
