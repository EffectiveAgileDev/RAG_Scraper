Website Configuration for RAG_Scraper Compatibility

  1. Robots.txt Configuration

  User-agent: *
  Disallow: /admin/
  Disallow: /private/
  # Allow restaurant data pages
  Allow: /
  Allow: /menu
  Allow: /about
  Allow: /contact

  2. Structured Data (Highest Priority)

  Add JSON-LD markup using schema.org Restaurant vocabulary:
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": "Your Restaurant Name",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "123 Main Street",
      "addressLocality": "Portland",
      "addressRegion": "OR",
      "postalCode": "97201"
    },
    "telephone": "(503) 555-1234",
    "servesCuisine": "Italian",
    "priceRange": "$15-$30",
    "openingHours": "Mo-Su 11:00-22:00"
  }
  </script>

  3. Microdata Markup (Medium Priority)

  <div itemscope itemtype="https://schema.org/Restaurant">
    <h1 itemprop="name">Restaurant Name</h1>
    <div itemprop="address" itemscope itemtype="https://schema.org/PostalAddress">
      <span itemprop="streetAddress">123 Main St</span>
      <span itemprop="addressLocality">Portland</span>
    </div>
    <span itemprop="telephone">(503) 555-1234</span>
  </div>

  4. SEO-Friendly HTML (Fallback)

  - Use clear headings (<h1> for restaurant name)
  - Include contact info in readable format
  - Use semantic CSS classes like class="restaurant-name", class="address"
  - Add proper page titles and meta descriptions

  5. What Our Tool Extracts

  - Restaurant name and cuisine type
  - Address and phone number
  - Operating hours and price ranges
  - Menu items and sections
  - Social media links (Facebook, Instagram, Twitter)

  6. Performance Tips

  - Keep pages under 2MB for faster processing
  - Avoid heavy JavaScript that blocks content rendering
  - Use standard HTML markup patterns
  - Include alt text and descriptive content

  Bottom line: The more structured data you provide (especially JSON-LD), the better our extraction accuracy and confidence
  scores will be!
