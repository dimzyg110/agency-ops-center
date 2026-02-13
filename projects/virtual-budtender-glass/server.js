import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import admin from 'firebase-admin';
import OpenAI from 'openai';
import { getTenantConfig, tenantExists } from './tenantConfig.js';
import { setupTenantEndpoints } from './tenantEndpoints.js';
import glassClient from './glassClient.js';

dotenv.config();

// Optional Firebase Admin initialization (graceful if env vars are missing)
const hasFirebaseConfig = Boolean(
  process.env.FIREBASE_PROJECT_ID &&
  process.env.FIREBASE_CLIENT_EMAIL &&
  process.env.FIREBASE_PRIVATE_KEY
);

if (hasFirebaseConfig) {
  try {
    const serviceAccount = {
      projectId: process.env.FIREBASE_PROJECT_ID,
      clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
      privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
    };

    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount),
    });
  } catch (error) {
    console.warn('Firebase initialization skipped:', error.message);
  }
}

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Setup tenant-specific endpoints
setupTenantEndpoints(app);

const LOGGED_SESSION_MAX = 10000;
const LOGGED_SESSION_TTL_MS = 24 * 60 * 60 * 1000;
const TENANT_SLUG_REGEX = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

const loggedSessions = new Map();

function getSessionToken(req) {
  return req.body?.sessionToken || req.headers['x-session-token'] || req.body?.sessionId || null;
}

function isAvailable(availability) {
  if (typeof availability === 'boolean') return availability;
  if (typeof availability === 'number') return availability > 0;
  if (typeof availability === 'string') {
    const value = availability.toLowerCase();
    return !['out_of_stock', 'unavailable', 'false', '0', 'none'].includes(value);
  }
  return true;
}

function mapGlassProductToVB(product) {
  const metadata = product?.metadata || {};

  return {
    id: product.id,
    sku: product.sku,
    name: product.name,
    brand: product.brand,
    category: product.category,
    price: Number(product.latest_price) || 0,
    thcPercent: typeof product.thc_percent === 'number' ? product.thc_percent : Number(product.thc_percent) || null,
    cbdPercent: typeof product.cbd_percent === 'number' ? product.cbd_percent : Number(product.cbd_percent) || null,
    strain: metadata.strain || metadata.strain_name || 'N/A',
    type: product.strain_type || metadata.type || null,
    imageUrl: metadata.image_url || metadata.imageUrl || null,
    dutchieUrl: metadata.dutchie_url || metadata.product_url || null,
    weightGrams: typeof product.weight_grams === 'number' ? product.weight_grams : Number(product.weight_grams) || null,
    isCannabis: true,
    inStock: isAvailable(product.availability) ? 1 : 0,
    isAvailableOnline: isAvailable(product.availability),
  };
}

function pruneLoggedSessions(now = Date.now()) {
  for (const [token, createdAt] of loggedSessions.entries()) {
    if (now - createdAt > LOGGED_SESSION_TTL_MS) {
      loggedSessions.delete(token);
    }
  }

  while (loggedSessions.size > LOGGED_SESSION_MAX) {
    const oldestToken = loggedSessions.keys().next().value;
    if (!oldestToken) break;
    loggedSessions.delete(oldestToken);
  }
}

function isValidTenantSlug(value) {
  return typeof value === 'string' && TENANT_SLUG_REGEX.test(value.trim());
}

function isValidMessage(value) {
  return typeof value === 'string' && value.trim().length > 0 && value.trim().length <= 2000;
}

function maybeLogSession(req, tenantId, tenantConfig) {
  const sessionToken = getSessionToken(req);
  if (!sessionToken) {
    return sessionToken;
  }

  pruneLoggedSessions();
  if (loggedSessions.has(sessionToken)) {
    return sessionToken;
  }

  loggedSessions.set(sessionToken, Date.now());
  glassClient.logSession(
    tenantId,
    tenantConfig.glassOperatorId,
    sessionToken,
    req.body?.deviceType,
    req.headers.referer || req.body?.referrer
  );

  return sessionToken;
}

function resolveTenantId(req, bodyTenantId) {
  const pathTenantId = req.params?.tenantId;
  const queryTenantId = req.query?.tenant;
  const queryTenantIdLegacy = req.query?.tenantId;

  return pathTenantId || queryTenantId || queryTenantIdLegacy || bodyTenantId || 'ch';
}

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * Get all products (for testing)
 */
app.get('/products', async (req, res) => {
  try {
    const tenantId = req.query.tenantId || 'ch';
    if (!tenantExists(tenantId)) {
      return res.status(404).json({ error: `Unknown tenant: ${tenantId}` });
    }

    const tenantConfig = getTenantConfig(tenantId);
    const items = await glassClient.fetchProducts(tenantConfig.glassOperatorId);
    const products = items.map(mapGlassProductToVB).filter(product => product.isAvailableOnline).slice(0, 50);

    res.json({ products, count: products.length });
  } catch (error) {
    console.error('Error fetching products:', error);
    res.status(500).json({ error: 'Failed to fetch products' });
  }
});

/**
 * Main recommendation endpoint
 */
app.post(['/recommend', '/recommend/:tenantId'], async (req, res) => {
  const requestStartedAt = Date.now();

  try {
    const { tenantId: bodyTenantId, answers, message } = req.body;
    const tenantId = resolveTenantId(req, bodyTenantId);

    if (!isValidTenantSlug(tenantId)) {
      return res.status(400).json({ error: 'Invalid tenantId format' });
    }

    if (message !== undefined && !isValidMessage(message)) {
      return res.status(400).json({ error: 'message must be a non-empty string up to 2000 characters' });
    }

    if (!answers || typeof answers !== 'object') {
      return res.status(400).json({ error: 'answers is required and must be an object' });
    }

    // Validate tenant
    if (!tenantExists(tenantId)) {
      return res.status(404).json({ error: `Unknown tenant: ${tenantId}` });
    }
    
    const tenantConfig = getTenantConfig(tenantId);
    const sessionToken = maybeLogSession(req, tenantId, tenantConfig);

    const items = await glassClient.fetchProducts(tenantConfig.glassOperatorId);

    let allCannabisProducts = items
      .map(mapGlassProductToVB)
      .filter(product => 
        product.isCannabis === true &&
        product.inStock > 0 &&
        product.isAvailableOnline === true
      );


    // Try exact format match first
    let candidates = allCannabisProducts;
    let isExactMatch = true;
    
    if (answers.format && answers.format !== 'any') {
      const exactMatches = candidates.filter(p => p.category === answers.format);
      
      if (exactMatches.length > 0) {
        candidates = exactMatches;
        console.log(`✅ Found ${candidates.length} products in exact category: ${answers.format}`);
      } else {
        // No exact matches - keep all products and note it
        isExactMatch = false;
        console.log(`⚠️  No exact matches for ${answers.format}, will recommend closest alternatives`);
      }
    }

    console.log(`📦 Filtering from ${candidates.length} candidates`);

    // Apply budget filter
    if (answers.budget && answers.budget !== 'none') {
      candidates = candidates.filter(product => {
        if (answers.budget === '<25') return product.price < 25;
        if (answers.budget === '25-50') return product.price >= 25 && product.price <= 50;
        if (answers.budget === '50+') return product.price > 50;
        return true;
      });
    }

    console.log(`💰 After budget filter: ${candidates.length} candidates`);

    // If still no candidates after budget filter, broaden the budget
    if (candidates.length === 0 && answers.budget !== 'none') {
      console.log(`🔄 No products in budget, removing budget filter...`);
      candidates = allCannabisProducts;
      
      // Reapply format filter if it was exact match
      if (answers.format && answers.format !== 'any' && isExactMatch) {
        candidates = candidates.filter(p => p.category === answers.format);
      }
      
      console.log(`📦 After removing budget: ${candidates.length} candidates`);
    }

    // Apply experience-based THC filtering
    if (answers.experience === 'new' && answers.goal !== 'high') {
      // Deprioritize very high THC for new users (unless they want to get high)
      const lowToMidTHC = candidates.filter(p => !p.thcPercent || p.thcPercent < 28);
      const highTHC = candidates.filter(p => p.thcPercent && p.thcPercent >= 28);
      candidates = [...lowToMidTHC, ...highTHC]; // Put high THC at the end
    }

    // Send all candidates to LLM (no limit - GPT-4o-mini is cheap!)
    // With GPT-4o-mini at $0.15/1M tokens, even 100 products costs <$0.002 per request
    // candidates = candidates.slice(0, 20); // OLD LIMIT - REMOVED

    if (candidates.length === 0) {
      // Absolute fallback - just show any products
      candidates = allCannabisProducts.slice(0, 20);
      console.log(`🆘 Using fallback: showing ${candidates.length} general recommendations`);
    }

    console.log(`🤖 Sending ${candidates.length} candidates to LLM`);

    // Prepare product list for LLM - use numbers instead of IDs for reliability
    const productList = candidates.map((p, idx) => {
      const productNumber = idx + 1;
      let productInfo = `${productNumber}. name:"${p.name}", brand:"${p.brand}", category:"${p.category}", price:$${p.price}`;
      
      // Add cannabinoid info
      if (p.thcPercent) productInfo += `, thc:${p.thcPercent}%`;
      if (p.cbdPercent) productInfo += `, cbd:${p.cbdPercent}%`;
      
      // Add strain info
      if (p.strain && p.strain !== 'N/A') productInfo += `, strain:"${p.strain}"`;
      
      // Add type if available
      if (p.type) productInfo += `, type:"${p.type}"`;
      
      return productInfo;
    }).join('\n');

    // Build LLM prompt using tenant's system prompt
    const systemPrompt = tenantConfig.systemPrompt;

    // Build context for LLM based on what we found
    let contextNote = '';
    if (!isExactMatch && answers.format !== 'any') {
      contextNote = `\n\nNote: We don't have exact matches for ${answers.format} right now, so I'm showing you the closest alternatives that might work for you.`;
    }
    
    const userPrompt = `The customer told you:
- Goal: ${answers.goal}
- Experience: ${answers.experience}
- Format preference: ${answers.format}
- Budget: ${answers.budget}${contextNote}

Here are the available products:

${productList}

Using ONLY these products, choose 2-4 that best match the customer. Be conversational and friendly. If they wanted a specific format but we don't have it, acknowledge that and explain why your recommendations are still great alternatives.

IMPORTANT: Use the product NUMBER (1, 2, 3, etc.) not IDs. For example, if you want product "5. name:Cape Cod...", use productNumber: 5

Respond in valid JSON format:
{"message": "your message", "recommendations": [{"productNumber": 5, "reason": "why this fits"}]}`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-5-mini',
      service_tier: 'priority',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      response_format: { type: 'json_object' }
    });

    const llmResponse = JSON.parse(completion.choices[0].message.content);
    console.log('✅ LLM response received:', llmResponse);

    // Enrich recommendations with full product data using product numbers
    const enrichedRecommendations = llmResponse.recommendations.map(rec => {
      const productIndex = rec.productNumber - 1; // Convert 1-based to 0-based
      
      if (productIndex < 0 || productIndex >= candidates.length) {
        console.error(`Invalid product number: ${rec.productNumber} (valid range: 1-${candidates.length})`);
        return null;
      }
      
      const product = candidates[productIndex];
      return {
        ...rec,
        product: {
          id: product.id,
          name: product.name,
          brand: product.brand,
          price: product.price,
          thcPercent: product.thcPercent,
          imageUrl: product.imageUrl,
          category: product.category,
          strain: product.strain,
          dutchieUrl: product.dutchieUrl || null,  // Shop link
        }
      };
    }).filter(rec => rec !== null);

    glassClient.logQuery(
      sessionToken,
      tenantId,
      JSON.stringify(answers || {}),
      'recommend',
      enrichedRecommendations.map(rec => rec.product?.id).filter(Boolean),
      Date.now() - requestStartedAt
    );

    res.json({
      message: llmResponse.message,
      recommendations: enrichedRecommendations
    });

  } catch (error) {
    console.error('❌ Error in /recommend:', error);
    res.status(500).json({ 
      error: 'Failed to generate recommendations',
      details: error.message 
    });
  }
});

/**
 * Conversational AI endpoint
 */
app.post(['/chat', '/chat/:tenantId'], async (req, res) => {
  const requestStartedAt = Date.now();

  try {
    const { tenantId: bodyTenantId, message, conversationHistory = [] } = req.body;
    const tenantId = resolveTenantId(req, bodyTenantId);

    if (!isValidTenantSlug(tenantId)) {
      return res.status(400).json({ error: 'Invalid tenantId format' });
    }

    if (!isValidMessage(message)) {
      return res.status(400).json({ error: 'message must be a non-empty string up to 2000 characters' });
    }

    // Validate tenant
    if (!tenantExists(tenantId)) {
      return res.status(404).json({ error: `Unknown tenant: ${tenantId}` });
    }
    
    const tenantConfig = getTenantConfig(tenantId);
    const sessionToken = maybeLogSession(req, tenantId, tenantConfig);
    console.log(`💬 ${tenantConfig.name}: "${message}"`);

    // Get available products for context
    const items = await glassClient.fetchProducts(tenantConfig.glassOperatorId);

    const allProducts = items
      .map(mapGlassProductToVB)
      .filter(product => 
        product.isCannabis === true &&
        product.inStock > 0 &&
        product.isAvailableOnline === true
      );

    console.log(`📦 ${allProducts.length} products available`);

    // Send ALL products to AI - no limits!
    // With GPT-4o-mini at $0.15/1M input tokens, even 100 products only costs ~$0.0015 per request
    // This provides better recommendations and covers the full inventory
    const categorizedProducts = {
      flower: allProducts.filter(p => p.category?.toLowerCase().includes('flower')),
      preroll: allProducts.filter(p => p.category?.toLowerCase().includes('roll')),
      vape: allProducts.filter(p => 
        p.category?.toLowerCase().includes('cartridge') ||
        p.category?.toLowerCase().includes('vape')
      ),
      edible: allProducts.filter(p => p.category?.toLowerCase().includes('edible')),
      concentrate: allProducts.filter(p => 
        p.category?.toLowerCase().includes('concentrate') ||
        p.category?.toLowerCase().includes('rosin')
      )
    };

    // Use ALL products - no slice() limits
    const selectedProducts = [
      ...categorizedProducts.flower,
      ...categorizedProducts.preroll,
      ...categorizedProducts.vape,
      ...categorizedProducts.edible,
      ...categorizedProducts.concentrate
    ].filter(Boolean);


    // Create indexed product list - AI will return numbers instead of IDs (much more reliable!)
    const productListForContext = selectedProducts.map((p, idx) => {
      // Use simple index number - AI is much better at copying numbers than long ID strings
      const productNumber = idx + 1;
      let productInfo = `${productNumber}. name:"${p.name}", brand:"${p.brand}", category:"${p.category}", price:$${p.price}`;
      
      // Add cannabinoid info (critical for recommendations)
      if (p.thcPercent) productInfo += `, thc:${p.thcPercent}%`;
      if (p.cbdPercent) productInfo += `, cbd:${p.cbdPercent}%`;
      
      // Add strain info (helps AI understand effects)
      if (p.strain && p.strain !== 'N/A') productInfo += `, strain:"${p.strain}"`;
      
      // Add type if available (indica/sativa/hybrid)
      if (p.type) productInfo += `, type:"${p.type}"`;
      
      return productInfo;
    }).join('\n');

    // Build system prompt for conversational AI
    const systemPrompt = `You are a friendly and knowledgeable virtual budtender for ${tenantConfig.name}. Your role is to help customers find the perfect cannabis products from the current inventory.

CORE RULES:
1. Be conversational, friendly, and helpful
2. If customer asks about SPECIFIC products (brand, category, or type) - ALWAYS SHOW THEM in recommendations
3. Only ask questions for VAGUE requests like "help me relax" or "what do you recommend"
4. Keep responses concise (2-3 sentences max)
5. Review conversation history - don't repeat questions you've already asked

CRITICAL - WHEN CUSTOMER ASKS FOR SPECIFIC PRODUCTS:
If someone asks "do you have X vapes?" or "show me Y flower" - IMMEDIATELY return matching products!
Do NOT just say "yes we have them" and ask follow-up questions. SHOW THE PRODUCTS!

AVAILABLE PRODUCTS:
${productListForContext}

CATEGORY MATCHING (actual categories from inventory):
- "vapes" = category contains "Cartridge" (e.g., "Cartridge 1000mg")
- "flower" = category contains "Flower"
- "pre-rolls" = category contains "Roll" (e.g., "Pre-Rolls", "Pre-Rolls-1g")
- "edibles" = category contains "Edible" (e.g., "Edibles")
- "concentrates" = category contains "Concentrate" or "Rosin" (e.g., "Live Rosin", "Concentrate")

CRITICAL - PRODUCT NUMBERS AND INVENTORY:
1. LOOK AT THE PRODUCT LIST ABOVE - those are the ONLY products available
2. USE PRODUCT NUMBERS: Each product has a number (1, 2, 3, etc.) - use these numbers, NOT made-up IDs
3. CHECK PRICES: If customer says "under $30", count how many products have price < 30
4. CHECK CATEGORY: Count how many products match the category they want
5. BE TRUTHFUL: If you don't have products matching their criteria, SAY SO
6. DON'T HALLUCINATE: Never make up product numbers - use ONLY the numbers from 1 to ${selectedProducts.length}
7. If NO products match: Ask if they want to adjust budget or try a different category

BRAND SEARCH - CRITICAL:
When a customer asks for a specific BRAND (e.g., "Advanced Cultivators", "ROVE", "Treeworks"):
1. Search BOTH the "name:" field AND the "brand:" field in the product list
2. Brand names can appear in either field - check BOTH!
3. Example: "Advanced Cultivator | Honey Banana Zuava..." has brand:"Advanced Cultivators" - this IS an Advanced Cultivators product!
4. If you find products matching the brand AND the requested category, RECOMMEND THEM
5. NEVER say "we don't have" a brand's products without first searching the ENTIRE list

EXAMPLES:

Customer: "I want vapes under $30"
You check list: Only 2 vapes exist, both are $56 (not under $30)
Response: {
  "message": "I only have 2 vapes available right now, but they're both $56. Would you like to see them, or try a different product type in your budget?",
  "recommendations": [],
  "suggestedReplies": ["Show me the $56 vapes", "Show flower under $30", "Show pre-rolls under $30"]
}

Customer: "show me the $56 vapes"
Response: {
  "message": "Here are our 2 premium live rosin vapes - high quality with 94-95% THC!",
  "recommendations": [
    {"id": "25286917", "reason": "Pineapple Express - 94.1% THC"},
    {"id": "61021955", "reason": "Maui Waui - 95% THC"}
  ],
  "suggestedReplies": ["Show cheaper options", "What about pre-rolls?", "Show me flower"]
}

Customer: "help me sleep"
Response: {
  "message": "I can help with that! What's your experience level with cannabis?",
  "recommendations": [],
  "suggestedReplies": ["New to cannabis", "Casual user", "Regular user"]
}

Customer: "do you have any Advanced Cultivators vapes?"
Search the product list for brand:"Advanced Cultivators" AND category:"Cartridges"
Found: Product #X "Advanced Cultivator | Honey Banana..." brand:"Advanced Cultivators" category:"Cartridges"
Response: {
  "message": "Yes! We have 2 Advanced Cultivators live rosin vapes at $40 each. Both are .5g cartridges - great quality!",
  "recommendations": [
    {"productNumber": X, "reason": "Honey Banana Zuava - premium live rosin"},
    {"productNumber": Y, "reason": "Skkrt Berry Zuava - another great live rosin option"}
  ],
  "suggestedReplies": ["Tell me more about these", "Show other vape brands", "What else does Advanced Cultivators make?"]
}

RESPONSE FORMAT (respond with valid JSON):
{
  "message": "Your message here",
  "recommendations": [{"productNumber": 5, "reason": "why this fits"}],
  "suggestedReplies": ["Option 1", "Option 2", "Option 3"]
}

IMPORTANT RULES FOR PRODUCT NUMBERS:
- Include 4-6 products when recommending (UI shows 3 initially with "Show More")
- Use the NUMBER from the list (e.g., if you want "1. name:Cape Cod...", use productNumber: 1)
- ONLY use numbers from 1 to ${selectedProducts.length}
- DO NOT make up numbers outside this range
- DO NOT use product names or IDs - ONLY use the product NUMBER
- Keep message concise and friendly
- Only include suggestedReplies if asking a question or offering alternatives
- Always respond in JSON format

EXAMPLE:
If you want to recommend products 5, 12, and 23 from the list:
{"recommendations": [
  {"productNumber": 5, "reason": "Great for sleep"},
  {"productNumber": 12, "reason": "Budget friendly"},
  {"productNumber": 23, "reason": "High THC"}
]}`;

    // Prepare conversation for OpenAI
    const messages = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory.slice(-6), // Keep last 6 messages for context (3 exchanges)
      { role: 'user', content: message }
    ];

    // Simple keyword-based content filter (skip AI classification for budget/simple responses)
    const simpleResponses = /^\d+$|^under\s+\d+$|^less\s+than\s+\d+$|^\$?\d+$|^yes$|^no$|^maybe$/i;
    const isSimpleResponse = simpleResponses.test(message.trim());

    // Only classify complex messages
    if (!isSimpleResponse && message.length > 5) {
      const classificationPrompt = `Is this message related to cannabis shopping, products, or budtender questions? Answer only YES or NO.

Message: "${message}"`;

      const classificationResponse = await openai.chat.completions.create({
        model: 'gpt-5-mini',
        service_tier: 'priority',
        messages: [
          { role: 'system', content: 'Answer YES for cannabis-related messages, NO for completely unrelated topics. If uncertain, answer YES.' },
          { role: 'user', content: classificationPrompt }
        ],
      });

      const isOnTopic = classificationResponse.choices[0].message.content.trim().toUpperCase().includes('YES');

      if (!isOnTopic) {
        console.log('⚠️  Off-topic message detected:', message);
        return res.json({
          message: "I'm specifically here to help you find the perfect cannabis products! For other questions, please contact our team directly. Now, what can I help you find today? 🌿",
          recommendations: []
        });
      }
    }

    // Generate AI response
    const completion = await openai.chat.completions.create({
      model: 'gpt-5-mini',
      service_tier: 'priority',
      messages: messages,
      response_format: { type: 'json_object' }
    });

    const llmResponse = JSON.parse(completion.choices[0].message.content);

    let enrichedRecommendations = [];
    if (llmResponse.recommendations && llmResponse.recommendations.length > 0) {
      // Quick validation: check if numbers are in valid range
      const invalidNumbers = llmResponse.recommendations.filter(rec => 
        !rec.productNumber || rec.productNumber < 1 || rec.productNumber > selectedProducts.length
      );
      
      if (invalidNumbers.length > 0) {
        console.warn(`⚠️  AI returned ${invalidNumbers.length} invalid product numbers!`);
        console.warn(`   Valid range: 1-${selectedProducts.length}`);
      }
      
      enrichedRecommendations = llmResponse.recommendations
        .map(rec => {
          // Use productNumber to index into selectedProducts array
          const productIndex = rec.productNumber - 1; // Convert 1-based to 0-based
          
          if (productIndex < 0 || productIndex >= selectedProducts.length) {
            console.error(`   ✗ Invalid product number: ${rec.productNumber} (valid range: 1-${selectedProducts.length})`);
            return null;
          }
          
          const product = selectedProducts[productIndex];
          
          // Log the product for debugging
          console.log(`   ✓ #${rec.productNumber}: ${product.name} ($${product.price}, ${product.category})`);
          
          return {
            ...rec,
            product: {
              id: product.id,
              name: product.name,
              brand: product.brand,
              price: product.price,
              thcPercent: product.thcPercent,
              imageUrl: product.imageUrl,
              category: product.category,
              strain: product.strain,
              dutchieUrl: product.dutchieUrl
            }
          };
        })
        .filter(rec => rec !== null);
      
      console.log(`✅ Successfully enriched ${enrichedRecommendations.length} recommendations`);
    }

    glassClient.logQuery(
      sessionToken,
      tenantId,
      message,
      'chat',
      enrichedRecommendations.map(rec => rec.product?.id).filter(Boolean),
      Date.now() - requestStartedAt
    );

    res.json({
      message: llmResponse.message,
      recommendations: enrichedRecommendations
    });

  } catch (error) {
    console.error('❌ Error in /chat:', error);
    res.status(500).json({ 
      error: 'Failed to process chat message',
      details: error.message 
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Backend server running on http://localhost:${PORT}`);
  console.log(`📍 Endpoints:`);
  console.log(`   GET  /health`);
  console.log(`   GET  /products`);
  console.log(`   POST /recommend`);
  console.log(`   POST /chat`);
});
