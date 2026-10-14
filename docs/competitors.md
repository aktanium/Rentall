# Competitors

A short look at three platforms RentAll can learn from.

| | Airbnb | Turo | Bolt |
|---|---|---|---|
| **What it rents** | Homes, rooms, experiences | Private cars (peer-to-peer) | Rides; e-scooters, e-bikes and car sharing in some cities |
| **Who supplies** | Private hosts | Private car owners | The company itself (own fleet) |
| **Booking model** | Dates, instant book or host approval | Dates/times, instant book or owner approval | On-demand, unlock now, pay per minute |
| **Price unit** | Per night | Per day | Per minute / per km |
| **Trust** | Two-way reviews, verified profiles | Reviews, driver verification, insurance plans | Company-run, no peer reviews |

## What RentAll borrows

**From Airbnb**
- A catalog that combines a list view with a map
- A listing page with a gallery, an availability calendar and a sticky booking widget
- Host approval before a booking is final (our `pending → confirmed`)
- Reviews after the stay, shown on the listing

**From Turo**
- Peer-to-peer vehicle rental: private owners list their own cars and bikes
- Hourly or daily pricing for vehicles
- A simple owner dashboard to manage listings and incoming requests

**From Bolt**
- Scooters and bikes as a rental category
- A fast, mobile-friendly flow with few steps from search to payment
- Clear, upfront pricing shown before you commit

## What RentAll does differently
- **One marketplace for many categories:** cars, bikes, scooters, apartments and event venues in one place, where each competitor focuses on one vertical.
- **Flexible price units:** each listing chooses `hour` or `day`, so it fits both a two-hour venue booking and a week-long apartment stay.
- **Peer-to-peer for everything:** unlike Bolt, there is no company fleet; any user can become an owner.
- **Local and simple:** a Russian-language UI for the local market, OpenStreetMap instead of paid map APIs, and a smaller feature set focused on the core book → confirm → pay → review loop.
- **No dynamic pricing:** the price is fixed by the owner and always calculated on the server from the units booked.
