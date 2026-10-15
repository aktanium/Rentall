# Key pages

The six key pages and the blocks each one contains. This is the basis for the wireframes. Every page shares the same **header** (logo, search shortcut, "List your item", login/register or the user menu) and **footer** (links, contacts).

---

## 1. Home
- **Hero search bar:** category selector, location input, date range, "Search" button
- **Category tiles:** cars, bikes, scooters, apartments, venues
- **Featured / new listings:** a row of listing cards
- **How it works:** three steps (find → book → pay)
- **Call to action for owners:** "Earn by renting out your stuff" → become an owner
- **Recent reviews** (optional): short testimonials

## 2. Catalog (search results)
- **Search bar** (compact), pre-filled with the current query
- **Filters panel:** category, price range, price unit (hour/day), dates, minimum rating, category-specific filters
- **Sort dropdown:** price ↑/↓, rating, newest
- **Results list:** listing cards (photo, title, price per unit, location, rating)
- **Map** (Leaflet + OSM) with a marker per listing that stays in sync with the list
- **Results counter + pagination**
- **Empty state:** "Nothing found, try changing the filters"

## 3. Listing details
- **Photo gallery:** main image plus thumbnails
- **Title block:** title, category badge, rating, number of reviews, location
- **Price block:** price per hour or day
- **Description and attributes:** category-specific details
- **Location map** with a pin
- **Availability calendar** with booked dates blocked
- **Booking widget** (sticky): start/end picker, server-calculated total, "Book" button (guests are sent to login)
- **Owner card:** name, avatar, member since, number of listings
- **Reviews list:** rating, author, date, text
- **Owner-only controls:** "Edit" and "Hide", visible only to the owner

## 4. Create / Edit listing
- **Form sections:**
  - Basic info: title, category, description
  - Pricing: price, price unit (`hour` / `day`)
  - Location: address input plus a map to place a pin
  - Photos: upload, preview, reorder or delete
  - Category-specific fields
- **Validation messages** next to each field
- **Actions:** "Publish" / "Save changes", "Cancel"; in edit mode also "Hide listing"
- Access: logged-in owners only. Editing someone else's listing returns 403.

## 5. Booking (checkout / booking details)
- **Listing summary:** photo, title, location, owner
- **Booking details:** dates or times, number of hours or days
- **Price breakdown:** units × price = total, calculated on the server
- **Status badge:** pending / confirmed / paid / declined / cancelled
- **Status timeline:** requested → confirmed → paid
- **Actions by status:**
  - renter + `confirmed`: "Pay" (redirects to Stripe Checkout)
  - owner + `pending`: "Confirm" / "Decline"
- **Payment result message:** success or cancelled, after returning from Stripe

## 6. User dashboard
- **Profile summary:** name, email, avatar, role, "Edit profile"
- **Tabs:**
  - *My bookings* (renter): upcoming and past bookings with status, plus "Pay" and "Leave review" buttons
  - *My listings* (owner): listing cards with views and status, plus "Edit", "Hide" and "New listing"
  - *Incoming bookings* (owner): requests with "Confirm" / "Decline"
  - *My reviews*: reviews the user has written
- **"Become an owner"** banner for users who aren't owners yet
- **Notifications area:** booking status changes
