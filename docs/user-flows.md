# User flows

Three main flows for the MVP. UI text will be in Russian; the button and page names below are working names in English.

Booking statuses used here: `pending` → `confirmed` → `paid` (active, cannot overlap), plus non-active outcomes such as declined or cancelled.

---

## 1. Renter: search → view listing → book → pay → leave a review

**Precondition:** the renter has an account and is logged in. If not, the "Book" button sends them to log in or register, then back to the listing.

1. **Search**
   1. Opens the Home page and enters a query in the search bar: category (car, bike, scooter, apartment, venue), city or location, and dates.
   2. Lands on the Catalog with results as a list plus a map (Leaflet + OSM).
   3. Narrows the results with filters: price range, price unit (hour/day) and category-specific options. Sorts by price, rating or newest.
2. **View the listing**
   1. Clicks a listing card and opens Listing details.
   2. Looks at the photos, description, price per hour or day, location on the map, owner info and reviews.
   3. Checks availability in the calendar, where dates that are already booked appear blocked.
3. **Book**
   1. Picks a start and an end (date and time for hourly listings, dates for daily ones).
   2. Sees the total price calculated **on the server**, with the number of units × the price.
   3. Clicks "Book". The server checks for overlaps with active bookings:
      - **Free:** the booking is created as `pending` and the owner is notified.
      - **Overlap:** an error appears and the renter picks other dates.
   4. The booking shows up in the renter's Dashboard as "Waiting for owner".
4. **Pay**
   1. After the owner confirms, the booking becomes `confirmed` and the renter is notified.
   2. From the Dashboard (or the Booking page) the renter clicks "Pay" and is redirected to Stripe Checkout.
   3. A successful payment goes through the Stripe webhook and the booking becomes `paid`. The renter sees a confirmation.
   4. If the payment is cancelled or fails, the booking stays `confirmed` and the renter can try again.
5. **Leave a review**
   1. After the rental period ends, a "Leave review" button appears on the booking in the Dashboard.
   2. The renter gives a 1–5 star rating and a text comment. One review per booking is allowed.
   3. The review appears on the Listing details page and updates the listing's average rating.

---

## 2. Owner: become an owner → create a listing → confirm/decline a booking

1. **Become an owner**
   1. A logged-in user opens the Dashboard and clicks "Become an owner" (or "List your item" in the header).
   2. Fills in a short owner profile with phone and display name, then accepts the rules.
   3. The account gets the owner role, and the Dashboard shows the "My listings" and "Incoming bookings" tabs.
2. **Create a listing**
   1. Clicks "New listing" and opens the Create listing form.
   2. Fills in the title, category, description, price, price unit (`hour` / `day`), address and location (map pin), and uploads photos.
   3. Submits the form. The server validates it, and on errors the form is shown again with messages.
   4. The listing is published and appears in the Catalog and under "My listings".
   5. Later the owner can edit the listing or hide it. Only the owner can do this; anyone else gets 403.
3. **Confirm or decline a booking**
   1. The owner gets a notification about a new `pending` booking.
   2. Opens Dashboard → "Incoming bookings" and sees the renter, dates and total price.
   3. Clicks **Confirm**: the booking becomes `confirmed` and the renter is asked to pay.
      Clicks **Decline**: the booking is declined, the dates free up and the renter is notified.
   4. Only the listing owner can confirm or decline. Anyone else gets 403.

---

## 3. Guest: browse the catalog without an account

1. Opens the Home page and sees the hero search bar, the categories and featured listings.
2. Goes to the Catalog through the search or a category tile.
3. Uses filters, sorting and the map just like a logged-in user.
4. Opens any Listing details page and sees the photos, price, location, availability and reviews.
5. Tries to book, which sends them to Log in / Register with a "Log in to book" message.
6. After registering or logging in, they return to the same listing and continue the Renter flow.

Guests **cannot** book, pay, leave reviews or create listings.

---

## Open questions
- Can the owner role be granted instantly, or does it need verification?
- Should an unpaid `confirmed` booking expire after some time to free up the dates?
- Should the renter be able to cancel a booking, and up to which status?
