/**
 * @vitest-environment jsdom
 */
import { describe, it, expect } from "vitest";
import { JSDOM } from "jsdom";
import { DomExtractionEngine } from "../index";

describe("Marketplace DOM Extraction Engine Unit Tests", () => {
  // ── 1. Amazon Adapter ──────────────────────────────────────────────────────
  describe("AmazonAdapter", () => {
    it("extracts structured ProductCard from Amazon HTML DOM", () => {
      const html = `
        <html>
          <body>
            <span id="productTitle">Sony WH-1000XM5 Wireless Headphones</span>
            <span class="a-price-whole">29,990.00</span>
            <div id="merchant-info">
              <a href="#">Appario Retail Private Ltd</a>
            </div>
            <img id="landingImage" src="https://images-na.ssl-images-amazon.com/images/I/61+jNfc77EL._AC_SL1500_.jpg" />
            <span class="a-icon-alt">4.5 out of 5 stars</span>
            <span id="acrCustomerReviewText">1,245 ratings</span>
            <a id="bylineInfo">Visit the Sony Store</a>
            <div id="availability"><span>In Stock</span></div>
          </body>
        </html>
      `;
      const dom = new JSDOM(html);
      const card = DomExtractionEngine.extract(dom.window.document, "Amazon", "https://www.amazon.in/dp/B0CX237A12");

      expect(card.marketplace).toBe("Amazon");
      expect(card.title).toBe("Sony WH-1000XM5 Wireless Headphones");
      expect(card.price).toBe(29990);
      expect(card.seller).toBe("Appario Retail Private Ltd");
      expect(card.image).toBe("https://images-na.ssl-images-amazon.com/images/I/61+jNfc77EL._AC_SL1500_.jpg");
      expect(card.rating).toBe(4.5);
      expect(card.reviewCount).toBe(1245);
      expect(card.brand).toBe("Sony");
      expect(card.confidenceScore).toBe(100);
    });

    it("uses selector fallback cascade when primary title ID is missing", () => {
      const html = `
        <html>
          <body>
            <h1 class="a-size-large">Amazon Basics High-Speed HDMI Cable</h1>
            <span class="a-offscreen">₹499</span>
          </body>
        </html>
      `;
      const dom = new JSDOM(html);
      const card = DomExtractionEngine.extract(dom.window.document, "Amazon", "https://www.amazon.in/dp/B014I8SSD0");

      expect(card.title).toBe("Amazon Basics High-Speed HDMI Cable");
      expect(card.price).toBe(499);
      expect(card.confidenceScore).toBeGreaterThanOrEqual(65);
    });
  });

  // ── 2. Flipkart Adapter ────────────────────────────────────────────────────
  describe("FlipkartAdapter", () => {
    it("extracts ProductCard from Flipkart HTML DOM", () => {
      const html = `
        <html>
          <body>
            <span class="VU-VGd">Apple iPhone 15 (Blue, 128 GB)</span>
            <div class="Nx9bqj _1pcnmf">₹65,999</div>
            <div id="sellerName"><span>TREASURE TROLL RETAIL</span></div>
            <img class="_396cs4 _2amPTt _3qWZwn" src="https://rukminim2.flixcart.com/image/832/832/xif0q/mobile/k/l/l/-original-imagtc5fz9spysyk.jpeg" />
            <div class="_3LWZlK">4.6</div>
            <span class="_2_R_DZ">8,421 Ratings & 512 Reviews</span>
          </body>
        </html>
      `;
      const dom = new JSDOM(html);
      const card = DomExtractionEngine.extract(dom.window.document, "Flipkart", "https://www.flipkart.com/apple-iphone-15/p/itm123");

      expect(card.marketplace).toBe("Flipkart");
      expect(card.title).toBe("Apple iPhone 15 (Blue, 128 GB)");
      expect(card.price).toBe(65999);
      expect(card.seller).toBe("TREASURE TROLL RETAIL");
      expect(card.rating).toBe(4.6);
      expect(card.confidenceScore).toBe(100);
    });
  });

  // ── 3. Myntra Adapter ──────────────────────────────────────────────────────
  describe("MyntraAdapter", () => {
    it("extracts ProductCard from Myntra HTML DOM", () => {
      const html = `
        <html>
          <body>
            <h1 class="pdp-title">Nike</h1>
            <h1 class="pdp-name">Air Max 270 Running Shoes</h1>
            <span class="pdp-price">Rs. 12995</span>
            <div class="seller-name">Nike India Official Store</div>
            <img class="pdp-image" src="https://assets.myntassets.com/h_1440,q_90,w_1080/v1/assets/images/12345/image.jpg" />
          </body>
        </html>
      `;
      const dom = new JSDOM(html);
      const card = DomExtractionEngine.extract(dom.window.document, "Myntra", "https://www.myntra.com/casual-shoes/nike/24589210/buy");

      expect(card.marketplace).toBe("Myntra");
      expect(card.title).toBe("Nike Air Max 270 Running Shoes");
      expect(card.brand).toBe("Nike");
      expect(card.price).toBe(12995);
      expect(card.seller).toBe("Nike India Official Store");
      expect(card.confidenceScore).toBe(100);
    });
  });

  // ── 4. AJIO Adapter ────────────────────────────────────────────────────────
  describe("AJIOAdapter", () => {
    it("extracts ProductCard from AJIO HTML DOM", () => {
      const html = `
        <html>
          <body>
            <h2 class="brand-name">PUMA</h2>
            <h1 class="prod-name">Smash v2 Leather Sneakers</h1>
            <div class="prod-sp">₹2,499</div>
            <div class="seller-name">Reliance Retail Ltd</div>
            <img class="rilrtl-lazy-img" src="https://assets.ajio.com/medias/sys_master/root/puma.jpg" />
          </body>
        </html>
      `;
      const dom = new JSDOM(html);
      const card = DomExtractionEngine.extract(dom.window.document, "AJIO", "https://www.ajio.com/puma-sneakers/p/469123456_blue");

      expect(card.marketplace).toBe("AJIO");
      expect(card.title).toBe("PUMA Smash v2 Leather Sneakers");
      expect(card.brand).toBe("PUMA");
      expect(card.price).toBe(2499);
      expect(card.seller).toBe("Reliance Retail Ltd");
      expect(card.confidenceScore).toBe(100);
    });
  });

  // ── 5. Meesho Adapter ──────────────────────────────────────────────────────
  describe("MeeshoAdapter", () => {
    it("extracts ProductCard from Meesho HTML DOM", () => {
      const html = `
        <html>
          <body>
            <h1 class="ProductDescription__Title">Stylish Cotton Anarkali Kurti</h1>
            <h4 class="ProductPrice__Price">₹499</h4>
            <span class="SupplierName">Sartorial Fashion House</span>
            <img class="ProductImage" src="https://images.meesho.com/images/products/123/1.jpg" />
          </body>
        </html>
      `;
      const dom = new JSDOM(html);
      const card = DomExtractionEngine.extract(dom.window.document, "Meesho", "https://www.meesho.com/sartorial-kurti/p/1a2b3c");

      expect(card.marketplace).toBe("Meesho");
      expect(card.title).toBe("Stylish Cotton Anarkali Kurti");
      expect(card.price).toBe(499);
      expect(card.seller).toBe("Sartorial Fashion House");
      expect(card.confidenceScore).toBe(100);
    });
  });

  // ── 6. TradeIndia Adapter ──────────────────────────────────────────────────
  describe("TradeIndiaAdapter", () => {
    it("extracts ProductCard from TradeIndia B2B HTML DOM", () => {
      const html = `
        <html>
          <body>
            <h1 class="title">Industrial Centrifugal Water Pump</h1>
            <div class="price">Rs 15,000 / Piece</div>
            <div class="company-name">Apex Engineering Works Pvt Ltd</div>
            <div class="product-image"><img src="https://img.tradeindia.com/fp/123456/pump.jpg" /></div>
          </body>
        </html>
      `;
      const dom = new JSDOM(html);
      const card = DomExtractionEngine.extract(dom.window.document, "TradeIndia", "https://www.tradeindia.com/fp123456/pump.html");

      expect(card.marketplace).toBe("TradeIndia");
      expect(card.title).toBe("Industrial Centrifugal Water Pump");
      expect(card.price).toBe(15000);
      expect(card.seller).toBe("Apex Engineering Works Pvt Ltd");
      expect(card.confidenceScore).toBe(100);
    });
  });
});
